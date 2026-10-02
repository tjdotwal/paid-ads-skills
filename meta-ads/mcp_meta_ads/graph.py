"""Direct Marketing API (Graph API) client for the surfaces the `meta ads` CLI
doesn't cover.

The CLI handles the simple cases well (list/get/update/delete, single-image
creatives, country targeting). It cannot build a real local-service campaign:
no radius / city / zip targeting, no interests, no custom or lookalike
audiences, no placements, no Advantage+ audience toggle, no carousel
creatives. Everything in this module exists to close those gaps.

Auth is the same system-user token the CLI uses (`ACCESS_TOKEN` in env), so
adding this layer costs no extra setup.

Every function here is thin: build a request, send it, surface Meta's error
message verbatim. No business logic — that lives in `build.py`.
"""

from __future__ import annotations

import json
import mimetypes
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

_UA = "meta-ads/0.6.0"
_GRAPH = "https://graph.facebook.com"

# Chunk size for resumable video upload. Meta accepts up to ~1 GB per chunk
# but 8 MB keeps retries cheap and progress visible.
_VIDEO_CHUNK_BYTES = 8 * 1024 * 1024


class GraphApiError(RuntimeError):
    """Raised when the Graph API returns an error object or a non-2xx status."""

    def __init__(self, path: str, status: int, error: dict[str, Any] | None, raw: str = ""):
        self.path = path
        self.status = status
        self.error = error or {}
        self.raw = raw
        msg = self.error.get("error_user_msg") or self.error.get("message") or raw or "unknown error"
        title = self.error.get("error_user_title")
        code = self.error.get("code")
        sub = self.error.get("error_subcode")
        detail = f" [code {code}{f'/{sub}' if sub else ''}]" if code else ""
        super().__init__(
            f"Graph API {path} failed (HTTP {status}){detail}: "
            f"{title + ' — ' if title else ''}{msg}"
        )


# ---------------------------------------------------------------------------
# Core request plumbing
# ---------------------------------------------------------------------------


def api_version() -> str:
    return os.environ.get("META_API_VERSION", "v23.0")


def _token() -> str:
    token = os.environ.get("ACCESS_TOKEN")
    if not token:
        raise RuntimeError("ACCESS_TOKEN env var not set; cannot call the Graph API.")
    return token


def normalize_account_id(ad_account_id: str | None) -> str:
    """Return `act_XXXX`, falling back to AD_ACCOUNT_ID from env."""
    acct = ad_account_id or os.environ.get("AD_ACCOUNT_ID", "")
    if not acct:
        raise RuntimeError(
            "No ad account: pass ad_account_id or set AD_ACCOUNT_ID in ~/.env."
        )
    acct = str(acct).strip()
    return acct if acct.startswith("act_") else f"act_{acct}"


def _encode_value(v: Any) -> str:
    """Graph API wants nested structures as JSON strings in form fields."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v, separators=(",", ":"))
    return str(v)


def _send(req: urllib.request.Request, path: str, timeout: int) -> Any:
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            err = json.loads(body).get("error")
        except Exception:
            err = None
        raise GraphApiError(path, e.code, err, body[:500]) from e
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        return {"_raw": body}
    if isinstance(data, dict) and "error" in data:
        raise GraphApiError(path, status, data["error"], body[:500])
    return data


def graph_get(path: str, params: dict[str, Any] | None = None, *, timeout: int = 60) -> Any:
    """GET /{version}/{path}?params. Nested params are JSON-encoded."""
    qs = {k: _encode_value(v) for k, v in (params or {}).items() if v is not None}
    qs["access_token"] = _token()
    url = f"{_GRAPH}/{api_version()}/{path.lstrip('/')}?{urllib.parse.urlencode(qs)}"
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    return _send(req, path, timeout)


def graph_get_all(path: str, params: dict[str, Any] | None = None, *, max_pages: int = 20) -> list[dict]:
    """Follow `paging.next` cursors and return the concatenated `data` list."""
    out: list[dict] = []
    params = dict(params or {})
    for _ in range(max_pages):
        page = graph_get(path, params)
        out.extend(page.get("data") or [])
        after = ((page.get("paging") or {}).get("cursors") or {}).get("after")
        if not after or not (page.get("paging") or {}).get("next"):
            break
        params["after"] = after
    return out


def graph_post(
    path: str,
    data: dict[str, Any] | None = None,
    files: dict[str, str | Path] | None = None,
    *,
    timeout: int = 120,
) -> Any:
    """POST /{version}/{path}. Form-encoded by default; multipart when `files`
    maps field names to local file paths."""
    fields = {k: _encode_value(v) for k, v in (data or {}).items() if v is not None}
    fields["access_token"] = _token()
    url = f"{_GRAPH}/{api_version()}/{path.lstrip('/')}"

    if files:
        body, ctype = _multipart(fields, files)
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"User-Agent": _UA, "Content-Type": ctype},
        )
    else:
        req = urllib.request.Request(
            url, data=urllib.parse.urlencode(fields).encode(), method="POST",
            headers={"User-Agent": _UA, "Content-Type": "application/x-www-form-urlencoded"},
        )
    return _send(req, path, timeout)


def graph_delete(path: str, *, timeout: int = 60) -> Any:
    url = f"{_GRAPH}/{api_version()}/{path.lstrip('/')}?{urllib.parse.urlencode({'access_token': _token()})}"
    req = urllib.request.Request(url, method="DELETE", headers={"User-Agent": _UA})
    return _send(req, path, timeout)


def _multipart(fields: dict[str, str], files: dict[str, str | Path], file_bytes: dict[str, bytes] | None = None) -> tuple[bytes, str]:
    boundary = f"----metaads{uuid.uuid4().hex}"
    parts: list[bytes] = []
    for k, v in fields.items():
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
        )
    for field, p in files.items():
        p = Path(p)
        if file_bytes and field in file_bytes:
            raw = file_bytes[field]
        else:
            raw = p.read_bytes()
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        parts.append(
            (
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; "
                f"filename=\"{p.name}\"\r\nContent-Type: {mime}\r\n\r\n"
            ).encode()
            + raw
            + b"\r\n"
        )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


# ---------------------------------------------------------------------------
# Asset uploads
# ---------------------------------------------------------------------------


def upload_image(path: str | Path, ad_account_id: str | None = None) -> dict[str, Any]:
    """Upload an image to the account's image library. Returns {hash, url, name}.

    Meta dedupes by content: re-uploading the same bytes returns the same hash,
    so this is safe to call repeatedly.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Image not found: {p}")
    acct = normalize_account_id(ad_account_id)
    resp = graph_post(f"{acct}/adimages", files={"filename": p})
    images = resp.get("images") or {}
    if not images:
        raise RuntimeError(f"adimages returned no image for {p.name}: {resp}")
    entry = next(iter(images.values()))
    return {"hash": entry.get("hash"), "url": entry.get("url"), "name": p.name}


def upload_video(
    path: str | Path,
    ad_account_id: str | None = None,
    *,
    title: str | None = None,
    wait_ready: bool = True,
    timeout_s: int = 600,
) -> dict[str, Any]:
    """Resumable (chunked) upload of a video to the ad account.

    Returns {id, status, thumbnail_url}. With `wait_ready`, blocks until Meta
    finishes processing (a creative referencing an unprocessed video fails
    with a cryptic error, so waiting here saves a confusing failure later).
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Video not found: {p}")
    acct = normalize_account_id(ad_account_id)
    size = p.stat().st_size

    start = graph_post(f"{acct}/advideos", {"upload_phase": "start", "file_size": size})
    session_id = start["upload_session_id"]
    video_id = start["video_id"]
    start_offset = int(start["start_offset"])
    end_offset = int(start["end_offset"])

    # Meta drives the loop: each transfer response returns the next
    # [start_offset, end_offset) window. Equal offsets mean "all bytes received".
    with p.open("rb") as fh:
        while start_offset < end_offset:
            fh.seek(start_offset)
            chunk = fh.read(end_offset - start_offset)
            if not chunk:
                break
            fields = {
                "upload_phase": "transfer",
                "upload_session_id": session_id,
                "start_offset": str(start_offset),
                "access_token": _token(),
            }
            body, ctype = _multipart(fields, {"video_file_chunk": p}, {"video_file_chunk": chunk})
            url = f"{_GRAPH}/{api_version()}/{acct}/advideos"
            req = urllib.request.Request(
                url, data=body, method="POST", headers={"User-Agent": _UA, "Content-Type": ctype}
            )
            resp = _send(req, f"{acct}/advideos[transfer]", 300)
            start_offset, end_offset = int(resp["start_offset"]), int(resp["end_offset"])

    graph_post(
        f"{acct}/advideos",
        {"upload_phase": "finish", "upload_session_id": session_id, **({"title": title} if title else {})},
    )

    out: dict[str, Any] = {"id": video_id, "status": "processing", "thumbnail_url": None}
    if wait_ready:
        out.update(wait_video_ready(video_id, timeout_s=timeout_s))
    return out


def wait_video_ready(video_id: str, *, timeout_s: int = 600, poll_s: float = 5.0) -> dict[str, Any]:
    """Poll until `status.video_status == ready`. Returns status + a thumbnail URL."""
    deadline = time.time() + timeout_s
    last: dict[str, Any] = {}
    while time.time() < deadline:
        last = graph_get(video_id, {"fields": "status,thumbnails{uri,is_preferred}"})
        status = (last.get("status") or {}).get("video_status")
        if status == "ready":
            thumbs = ((last.get("thumbnails") or {}).get("data")) or []
            preferred = next((t for t in thumbs if t.get("is_preferred")), thumbs[0] if thumbs else {})
            return {"status": "ready", "thumbnail_url": preferred.get("uri")}
        if status == "error":
            raise RuntimeError(f"Meta failed to process video {video_id}: {last.get('status')}")
        time.sleep(poll_s)
    raise TimeoutError(
        f"Video {video_id} still processing after {timeout_s}s "
        f"(last status: {(last.get('status') or {}).get('video_status')})."
    )


# ---------------------------------------------------------------------------
# Lookups used by the targeting builder
# ---------------------------------------------------------------------------


def search_geo(
    q: str,
    location_types: list[str],
    country_code: str | None = None,
    region_id: str | None = None,
    limit: int = 25,
) -> list[dict]:
    """Targeting search for cities / zips / regions. Returns Meta's raw rows
    (key, name, type, region, region_id, country_code, ...)."""
    params: dict[str, Any] = {"type": "adgeolocation", "q": q, "location_types": location_types, "limit": limit}
    if country_code:
        params["country_code"] = country_code
    if region_id:
        params["region_id"] = region_id
    return graph_get("search", params).get("data") or []


def search_interests(q: str, limit: int = 25) -> list[dict]:
    """Detailed-targeting interest search. Rows: id, name, audience_size_*, path, topic."""
    return graph_get("search", {"type": "adinterest", "q": q, "limit": limit}).get("data") or []


def list_custom_audiences(ad_account_id: str | None = None) -> list[dict]:
    acct = normalize_account_id(ad_account_id)
    return graph_get_all(
        f"{acct}/customaudiences",
        {"fields": "id,name,subtype,approximate_count_lower_bound,approximate_count_upper_bound,delivery_status", "limit": 200},
    )


def list_pages() -> list[dict]:
    """Pages the token can act as. Falls back to business-owned pages if /me/accounts is empty."""
    rows = graph_get_all("me/accounts", {"fields": "id,name,category", "limit": 100})
    if rows:
        return rows
    biz = os.environ.get("BUSINESS_ID")
    if biz:
        rows = graph_get_all(f"{biz}/owned_pages", {"fields": "id,name,category", "limit": 100})
        rows += graph_get_all(f"{biz}/client_pages", {"fields": "id,name,category", "limit": 100})
    return rows


def list_pixels(ad_account_id: str | None = None) -> list[dict]:
    acct = normalize_account_id(ad_account_id)
    return graph_get_all(f"{acct}/adspixels", {"fields": "id,name,last_fired_time", "limit": 100})


def instagram_accounts_for_page(page_id: str) -> list[dict]:
    """Instagram actors connected to a Page (for `instagram_actor_id`)."""
    rows: list[dict] = []
    for edge in ("instagram_accounts", "page_backed_instagram_accounts"):
        try:
            rows += graph_get_all(f"{page_id}/{edge}", {"fields": "id,username", "limit": 50})
        except GraphApiError:
            continue
    return rows


def ad_preview_url(ad_account_id: str, campaign_id: str | None = None) -> str:
    acct = normalize_account_id(ad_account_id).removeprefix("act_")
    url = f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={acct}"
    if campaign_id:
        url += f"&selected_campaign_ids={campaign_id}"
    return url
