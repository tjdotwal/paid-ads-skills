"""FastMCP server exposing Meta's `meta ads` CLI as structured tools.

Add new tools by writing a function decorated with `@mcp.tool()`. The function
signature becomes the JSON schema; the body should `return run_meta([...])`.
See the existing tools for the pattern.

Two backends:
  * `run_meta(...)`  — Meta's official `meta ads` CLI. Used for everything it
    does well: list/get/update/delete, insights, single-asset creatives.
  * `graph.*`        — direct Marketing API calls (same ACCESS_TOKEN) for what
    the CLI cannot do: full ad-set targeting (radius / cities / zips /
    interests / custom audiences / placements / Advantage+ audience),
    carousel + DCO creatives, asset uploads, and the spreadsheet-driven
    campaign builder in `build.py`.

Coverage status (as of v0.6.0):
  Campaigns          : list, get, create (Graph), update, delete          [DONE]
  Ad Sets            : list, get, create (CLI + Graph full), update, del  [DONE]
  Ads                : list, get, create, update, delete                  [DONE]
  Creatives          : list, get, create (image/video/carousel/dco), del  [DONE]
  Assets             : image_upload, video_upload                         [DONE]
  Lookups            : page_list, pixel_list, custom_audience_list,
                       geo_search, interest_search                        [DONE]
  Campaign builder   : campaign_sheet_template, campaign_build (dry-run)  [DONE]
  Insights           : get (with date ranges + breakdowns)                [DONE]
  Catalogs / Product Items / Product Sets / Datasets                      [meta_raw]
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from . import build as _build
from . import graph as _graph
from .cli import MetaCliError, run_meta

mcp = FastMCP("meta-ads")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _flag(name: str, value: Any) -> list[str]:
    """Build a CLI flag pair if the value is non-empty. Skips None / '' / []."""
    if value is None or value == "" or value == []:
        return []
    if isinstance(value, bool):
        return [name] if value else []
    if isinstance(value, list):
        return [name, ",".join(str(v) for v in value)]
    return [name, str(value)]


def _account_env(ad_account_id: str | None) -> dict[str, str] | None:
    """Build an extra_env dict that overrides AD_ACCOUNT_ID for one call.

    Returns None when no override is requested, so run_meta falls through to
    the inherited env (preserves existing behavior for legacy callers).
    """
    if not ad_account_id:
        return None
    if not ad_account_id.startswith("act_"):
        ad_account_id = f"act_{ad_account_id}"
    return {"AD_ACCOUNT_ID": ad_account_id}


# ---------------------------------------------------------------------------
# Ad Accounts
# ---------------------------------------------------------------------------


@mcp.tool()
def ad_account_list() -> Any:
    """List all ad accounts the authenticated user has access to."""
    return run_meta(["adaccount", "list"])


@mcp.tool()
def ad_account_current() -> Any:
    """Return the currently selected default ad account (from AD_ACCOUNT_ID)."""
    return run_meta(["adaccount", "current"])


@mcp.tool()
def ad_account_get(ad_account_id: str) -> Any:
    """Get details for a specific ad account.

    Args:
        ad_account_id: Format `act_XXXXXXXXX`.
    """
    return run_meta(["adaccount", "get", ad_account_id])


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------


@mcp.tool()
def campaign_list(
    limit: int = 25,
    ad_account_id: str | None = None,
) -> Any:
    """List campaigns in an ad account.

    Args:
        limit: Max campaigns to return (default 25).
        ad_account_id: Override the default ad account (format: act_XXXXXXXXX).
            If omitted, uses AD_ACCOUNT_ID from the inherited env.

    Note: the underlying `meta ads campaign list` CLI does not support a
    status filter. Filter client-side on `effective_status` if needed.
    """
    argv = ["campaign", "list", *_flag("--limit", limit)]
    return run_meta(argv, extra_env=_account_env(ad_account_id))


@mcp.tool()
def campaign_get(campaign_id: str) -> Any:
    """Get full details for a single campaign."""
    return run_meta(["campaign", "get", campaign_id])


@mcp.tool()
def campaign_create(
    name: str,
    objective: str,
    daily_budget: int | None = None,
    lifetime_budget: int | None = None,
    special_ad_categories: list[str] | None = None,
    bid_strategy: str | None = None,
    ad_account_id: str | None = None,
) -> Any:
    """Create a new campaign. Resource is created in PAUSED status.

    Goes through the Graph API rather than the CLI: the CLI's `campaign create`
    has no flags for special ad categories or bid strategy, and the API
    requires `special_ad_categories` on every create (empty list = none).

    Args:
        name: Campaign name. Follow your naming convention (see the naming-conventions skill).
        objective: One of OUTCOME_AWARENESS, OUTCOME_TRAFFIC, OUTCOME_ENGAGEMENT,
            OUTCOME_LEADS, OUTCOME_SALES, OUTCOME_APP_PROMOTION.
        daily_budget: Daily budget in account currency MINOR units (cents for USD).
            Setting a campaign budget turns on CBO (Advantage+ campaign budget).
        lifetime_budget: Lifetime budget in MINOR units. Mutually exclusive with daily.
        special_ad_categories: e.g. ["HOUSING"], ["EMPLOYMENT"], ["CREDIT"], ["ISSUES_ELECTIONS_POLITICS"].
        bid_strategy: LOWEST_COST_WITHOUT_CAP | LOWEST_COST_WITH_BID_CAP | COST_CAP | LOWEST_COST_WITH_MIN_ROAS.
            Only meaningful with a campaign-level budget.
        ad_account_id: act_XXXXXXXXX. Falls back to AD_ACCOUNT_ID env.
    """
    if daily_budget and lifetime_budget:
        raise ValueError("Pass daily_budget or lifetime_budget, not both.")
    body: dict[str, Any] = {
        "name": name,
        "objective": objective.upper(),
        "status": "PAUSED",
        "special_ad_categories": [s.upper() for s in (special_ad_categories or [])],
        "buying_type": "AUCTION",
    }
    if daily_budget:
        body["daily_budget"] = daily_budget
    if lifetime_budget:
        body["lifetime_budget"] = lifetime_budget
    if bid_strategy:
        body["bid_strategy"] = bid_strategy.upper()
    acct = _graph.normalize_account_id(ad_account_id)
    return _graph.graph_post(f"{acct}/campaigns", body)


@mcp.tool()
def campaign_update(
    campaign_id: str,
    name: str | None = None,
    status: str | None = None,
    daily_budget: int | None = None,
    lifetime_budget: int | None = None,
) -> Any:
    """Update a campaign. Pass `status="ACTIVE"` to launch a paused campaign."""
    argv = [
        "campaign",
        "update",
        campaign_id,
        *_flag("--name", name),
        *_flag("--status", status),
        *_flag("--daily-budget", daily_budget),
        *_flag("--lifetime-budget", lifetime_budget),
    ]
    return run_meta(argv)


@mcp.tool()
def campaign_delete(campaign_id: str) -> Any:
    """Delete a campaign. Irreversible. Confirm with the user before calling."""
    return run_meta(["campaign", "delete", campaign_id, "--force"])


# ---------------------------------------------------------------------------
# Ad Sets
# ---------------------------------------------------------------------------


@mcp.tool()
def adset_list(
    campaign_id: str | None = None,
    limit: int = 25,
    ad_account_id: str | None = None,
) -> Any:
    """List ad sets, optionally scoped to one campaign.

    Args:
        campaign_id: If set, only return adsets within this campaign.
        limit: Max adsets to return (default 25).
        ad_account_id: Override the default ad account.

    Note: the underlying CLI does not support a status filter. Filter
    client-side on `effective_status` if needed.
    """
    # CLI signature: `meta ads adset list [CAMPAIGN_ID] --limit N` (positional, no flag).
    argv = ["adset", "list", *([campaign_id] if campaign_id else []), *_flag("--limit", limit)]
    return run_meta(argv, extra_env=_account_env(ad_account_id))


@mcp.tool()
def adset_get(adset_id: str) -> Any:
    """Get full details for a single ad set."""
    return run_meta(["adset", "get", adset_id])


@mcp.tool()
def adset_create(
    campaign_id: str,
    name: str,
    optimization_goal: str,
    billing_event: str = "IMPRESSIONS",
    bid_amount: int | None = None,
    daily_budget: int | None = None,
    targeting_countries: list[str] | None = None,
) -> Any:
    """Create a new ad set under a campaign. Created in PAUSED status.

    Args:
        campaign_id: Parent campaign ID.
        name: Ad set name. Follow your naming convention.
        optimization_goal: e.g. LINK_CLICKS, OFFSITE_CONVERSIONS, LANDING_PAGE_VIEWS, REACH.
        billing_event: IMPRESSIONS | LINK_CLICKS (default IMPRESSIONS).
        bid_amount: Bid in MINOR currency units. Required for bid_cap / cost_cap strategies.
        daily_budget: Daily budget in MINOR units (ad-set-level budget, if not using CBO).
        targeting_countries: ISO country codes, e.g. ["US"], ["US", "CA"].
    """
    argv = [
        "adset",
        "create",
        campaign_id,
        *_flag("--name", name),
        *_flag("--optimization-goal", optimization_goal),
        *_flag("--billing-event", billing_event),
        *_flag("--bid-amount", bid_amount),
        *_flag("--daily-budget", daily_budget),
        *_flag("--targeting-countries", targeting_countries),
    ]
    return run_meta(argv)


@mcp.tool()
def adset_create_full(
    campaign_id: str,
    name: str,
    optimization_goal: str,
    targeting: dict[str, Any],
    billing_event: str = "IMPRESSIONS",
    daily_budget: int | None = None,
    lifetime_budget: int | None = None,
    bid_strategy: str | None = None,
    bid_amount: int | None = None,
    pixel_id: str | None = None,
    conversion_event: str = "LEAD",
    start_time: str | None = None,
    end_time: str | None = None,
    is_dynamic_creative: bool = False,
    ad_account_id: str | None = None,
) -> Any:
    """Create an ad set with FULL targeting via the Graph API. Created PAUSED.

    Use this instead of `adset_create` whenever targeting goes beyond a country
    list. `targeting` is the Marketing API targeting spec. Build it with
    `targeting_from_sheet_row` (recommended) or hand-write it. Common shape:

        {
          "geo_locations": {
            "custom_locations": [{"address_string": "1200 Broadway, Nashville, TN", "radius": 25, "distance_unit": "mile"}],
            "cities": [{"key": "2490299", "radius": 15, "distance_unit": "mile"}],
            "zips": [{"key": "US:37203"}],
            "countries": ["US"],
            "location_types": ["home", "recent"]
          },
          "age_min": 25, "age_max": 65, "genders": [1],
          "flexible_spec": [{"interests": [{"id": "6003...", "name": "Carpet cleaning"}]}],
          "custom_audiences": [{"id": "1234"}], "excluded_custom_audiences": [{"id": "5678"}],
          "targeting_automation": {"advantage_audience": 1},
          "publisher_platforms": ["facebook", "instagram"], "facebook_positions": ["feed"], "instagram_positions": ["stream", "reels"]
        }

    Resolve city keys with `geo_search`, interest ids with `interest_search`,
    audience ids with `custom_audience_list`.

    Args:
        campaign_id: Parent campaign.
        name: Ad set name (follow your naming convention).
        optimization_goal: OFFSITE_CONVERSIONS | LANDING_PAGE_VIEWS | LINK_CLICKS | REACH | THRUPLAY | ...
        targeting: Targeting spec dict (see above).
        billing_event: IMPRESSIONS (default) | LINK_CLICKS | THRUPLAY.
        daily_budget / lifetime_budget: MINOR units. Leave both None when the campaign uses CBO.
        bid_strategy: Only when the ad set carries the budget. LOWEST_COST_WITHOUT_CAP | COST_CAP | LOWEST_COST_WITH_BID_CAP.
        bid_amount: MINOR units. Required for cost cap / bid cap.
        pixel_id + conversion_event: Required when optimization_goal is OFFSITE_CONVERSIONS.
        start_time / end_time: ISO 8601. end_time required with lifetime_budget.
        is_dynamic_creative: True when the ad set will hold a DCO creative (one ad only).
        ad_account_id: act_XXXXXXXXX. Falls back to AD_ACCOUNT_ID env.
    """
    body: dict[str, Any] = {
        "campaign_id": campaign_id,
        "name": name,
        "optimization_goal": optimization_goal.upper(),
        "billing_event": billing_event.upper(),
        "targeting": targeting,
        "status": "PAUSED",
    }
    if daily_budget:
        body["daily_budget"] = daily_budget
    if lifetime_budget:
        body["lifetime_budget"] = lifetime_budget
        if not end_time:
            raise ValueError("lifetime_budget requires end_time.")
    if bid_strategy:
        body["bid_strategy"] = bid_strategy.upper()
    if bid_amount:
        body["bid_amount"] = bid_amount
    if start_time:
        body["start_time"] = start_time
    if end_time:
        body["end_time"] = end_time
    if is_dynamic_creative:
        body["is_dynamic_creative"] = True
    if body["optimization_goal"] == "OFFSITE_CONVERSIONS":
        if not pixel_id:
            raise ValueError("OFFSITE_CONVERSIONS needs pixel_id.")
        body["promoted_object"] = {"pixel_id": pixel_id, "custom_event_type": conversion_event.upper()}
        body["destination_type"] = "WEBSITE"
    elif body["optimization_goal"] in {"LANDING_PAGE_VIEWS", "LINK_CLICKS"}:
        body["destination_type"] = "WEBSITE"
    acct = _graph.normalize_account_id(ad_account_id)
    return _graph.graph_post(f"{acct}/adsets", body)


@mcp.tool()
def targeting_from_sheet_row(
    geo_type: str,
    geo_value: str,
    ad_account_id: str | None = None,
    age_min: int = 18,
    age_max: int = 65,
    genders: str = "all",
    interests: str = "",
    custom_audiences: str = "",
    excluded_audiences: str = "",
    advantage_audience: str = "",
    placements: str = "auto",
    excluded_geo_type: str = "",
    excluded_geo_value: str = "",
    default_country: str = "US",
) -> Any:
    """Turn human targeting inputs into a Marketing API targeting spec.

    Same column semantics as the AdSets sheet used by `campaign_build`, so
    you can build one ad set ad hoc without a workbook. Resolves cities,
    zips, interests, and audience names against Meta and returns both the
    spec and a list of what each input resolved to (check those).

    geo_type / geo_value formats:
        countries  → "US;CA"
        radius     → "1200 Broadway, Nashville, TN 37203 | 25mi; 36.16,-86.78 | 10mi"
        cities     → "Nashville, TN | 15mi; Franklin, TN"      (radius optional, 10-50mi)
        zips       → "37203; 37204"
        regions    → "Tennessee; KY"
    interests / custom_audiences / excluded_audiences: semicolon-separated names (or audience IDs).
    advantage_audience: "Y" | "N" | "" (default: on unless interests/audiences are given).
    placements: "auto" or "facebook:feed,story,reels; instagram:stream,reels".
    """
    acct = _graph.normalize_account_id(ad_account_id)
    resolver = _build.Resolver(acct, default_country.upper())
    row = {
        "geo_type": geo_type, "geo_value": geo_value, "age_min": str(age_min), "age_max": str(age_max),
        "genders": genders, "interests": interests, "custom_audiences": custom_audiences,
        "excluded_audiences": excluded_audiences, "advantage_audience": advantage_audience,
        "placements": placements, "excluded_geo_type": excluded_geo_type, "excluded_geo_value": excluded_geo_value,
    }
    try:
        spec = _build.build_targeting(row, resolver)
    except _build.BuildError as e:
        return {"error": str(e), "resolutions": resolver.notes}
    return {"targeting": spec, "resolutions": resolver.notes}


@mcp.tool()
def adset_update(
    adset_id: str,
    status: str | None = None,
    daily_budget: int | None = None,
    lifetime_budget: int | None = None,
    bid_amount: int | None = None,
    end_time: str | None = None,
    name: str | None = None,
) -> Any:
    """Update an ad set. Pass status="ACTIVE" to launch a paused ad set."""
    argv = [
        "adset",
        "update",
        adset_id,
        *_flag("--name", name),
        *_flag("--status", status),
        *_flag("--daily-budget", daily_budget),
        *_flag("--lifetime-budget", lifetime_budget),
        *_flag("--bid-amount", bid_amount),
        *_flag("--end-time", end_time),
    ]
    return run_meta(argv)


@mcp.tool()
def adset_delete(adset_id: str) -> Any:
    """Delete an ad set and its ads. Irreversible. Confirm with the user first."""
    return run_meta(["adset", "delete", adset_id, "--force"])


# ---------------------------------------------------------------------------
# Ads
# ---------------------------------------------------------------------------


@mcp.tool()
def ad_list(
    adset_id: str | None = None,
    campaign_id: str | None = None,
    limit: int = 25,
    ad_account_id: str | None = None,
) -> Any:
    """List ads, optionally scoped to an ad set or campaign.

    Args:
        adset_id / campaign_id: Optional scoping filters.
        limit: Max ads to return (default 25).
        ad_account_id: Override the default ad account.

    Note: the underlying CLI does not support a status filter. Filter
    client-side on `effective_status` if needed.
    """
    # CLI signature: `meta ads ad list [ADSET_ID] --limit N`. There is no
    # campaign filter on the CLI, so campaign_id goes through the Graph API.
    if campaign_id and not adset_id:
        return _graph.graph_get_all(
            f"{campaign_id}/ads",
            {"fields": "id,name,effective_status,adset_id,campaign_id,created_time", "limit": min(limit, 100)},
        )[:limit]
    argv = ["ad", "list", *([adset_id] if adset_id else []), *_flag("--limit", limit)]
    return run_meta(argv, extra_env=_account_env(ad_account_id))


@mcp.tool()
def ad_get(ad_id: str) -> Any:
    """Get full details for a single ad."""
    return run_meta(["ad", "get", ad_id])


@mcp.tool()
def ad_create(adset_id: str, name: str, creative_id: str, pixel_id: str | None = None) -> Any:
    """Attach an existing creative to an ad set as a new ad. Created in PAUSED status.

    Args:
        pixel_id: Attach offsite-conversion tracking for this pixel (recommended
            on every conversion campaign so Ads Manager reports results).
    """
    argv = [
        "ad", "create", adset_id,
        *_flag("--name", name),
        *_flag("--creative-id", creative_id),
        *_flag("--pixel-id", pixel_id),
    ]
    return run_meta(argv)


@mcp.tool()
def ad_update(
    ad_id: str,
    status: str | None = None,
    name: str | None = None,
    creative_id: str | None = None,
) -> Any:
    """Update an ad — most often used to flip PAUSED to ACTIVE, or swap its creative."""
    argv = [
        "ad", "update", ad_id,
        *_flag("--status", status),
        *_flag("--name", name),
        *_flag("--creative-id", creative_id),
    ]
    return run_meta(argv)


@mcp.tool()
def ad_delete(ad_id: str) -> Any:
    """Delete an ad. Irreversible. Confirm with the user first."""
    return run_meta(["ad", "delete", ad_id, "--force"])


# ---------------------------------------------------------------------------
# Ad Creatives
# ---------------------------------------------------------------------------


@mcp.tool()
def creative_list(limit: int = 25, ad_account_id: str | None = None) -> Any:
    """List ad creatives in an ad account.

    Args:
        limit: Max creatives to return (default 25).
        ad_account_id: Override the default ad account.
    """
    return run_meta(
        ["creative", "list", *_flag("--limit", limit)],
        extra_env=_account_env(ad_account_id),
    )


@mcp.tool()
def creative_get(creative_id: str) -> Any:
    """Get full details for a single creative."""
    return run_meta(["creative", "get", creative_id])


@mcp.tool()
def creative_create(
    name: str,
    page_id: str,
    body: str,
    title: str,
    link_url: str,
    image_path: str | None = None,
    video_path: str | None = None,
    description: str | None = None,
    call_to_action: str = "LEARN_MORE",
    instagram_actor_id: str | None = None,
    ad_account_id: str | None = None,
) -> Any:
    """Create a single-image or single-video ad creative via the CLI.

    For carousel, DCO, UTM url_tags, or a display link, use `creative_create_full`.

    Args:
        name: Creative name.
        page_id: Facebook Page ID running the ad.
        body: Primary text (ad copy).
        title: Headline.
        link_url: Destination URL.
        image_path: Local image file. Pass this OR video_path.
        video_path: Local video file. The CLI uploads it and waits for processing.
        description: Link description shown under the headline.
        call_to_action: CTA button (e.g. LEARN_MORE, SHOP_NOW, SIGN_UP, GET_QUOTE).
        instagram_actor_id: Instagram account for IG placements.
        ad_account_id: Override the default ad account.
    """
    if bool(image_path) == bool(video_path):
        raise ValueError("Pass exactly one of image_path or video_path.")
    argv = [
        "creative",
        "create",
        *_flag("--name", name),
        *_flag("--page-id", page_id),
        *_flag("--body", body),
        *_flag("--title", title),
        *_flag("--link-url", link_url),
        *_flag("--image", image_path),
        *_flag("--video", video_path),
        *_flag("--description", description),
        *_flag("--call-to-action", call_to_action),
        *_flag("--instagram-actor-id", instagram_actor_id),
    ]
    return run_meta(argv, timeout=600, extra_env=_account_env(ad_account_id))


@mcp.tool()
def creative_create_full(
    name: str,
    page_id: str,
    format: str,
    asset_paths: list[str],
    primary_text: str,
    destination_url: str,
    headline: str | None = None,
    description: str | None = None,
    cta: str = "LEARN_MORE",
    url_tags: str | None = None,
    display_link: str | None = None,
    instagram_user_id: str | None = None,
    ad_account_id: str | None = None,
) -> Any:
    """Create an image, video, carousel, or DCO creative via the Graph API. PAUSED.

    Uploads the assets first (images → hash, videos → chunked upload + wait
    for processing), then posts the creative. Same copy conventions as the
    Ads sheet in `campaign_build`:

      * carousel: `asset_paths` in card order (2-10). `headline`, `description`,
        `destination_url` accept one value per card separated by `||`, or a
        single value reused on every card.
      * dco: up to 10 images OR videos; `primary_text`, `headline`,
        `description`, `cta` accept up to 5 variants separated by `||`.
        The target ad set must be created with is_dynamic_creative=True.
      * url_tags: appended to every link, e.g.
        "utm_source=facebook&utm_medium=ppc&utm_campaign={{campaign.name}}&utm_content={{ad.name}}"

    Args:
        format: image | video | carousel | dco
        asset_paths: Local file paths.
        ad_account_id: act_XXXXXXXXX. Falls back to AD_ACCOUNT_ID env.
    """
    from pathlib import Path

    acct = _graph.normalize_account_id(ad_account_id)
    fmt = format.lower()
    paths = [Path(p).expanduser() for p in asset_paths]
    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(f"Asset not found: {p}")
    images: dict[str, str] = {}
    videos: dict[str, dict[str, Any]] = {}
    for p in paths:
        if p.suffix.lower() in _build._VIDEO_EXT:
            videos[p.name] = _graph.upload_video(p, acct, title=p.name)
        else:
            images[p.name] = _graph.upload_image(p, acct)["hash"]
    ad = {
        "name": name, "format": fmt, "assets": [p.name for p in paths],
        "row": {
            "primary_text": primary_text, "headline": headline or "", "description": description or "",
            "destination_url": destination_url, "cta": cta, "url_tags": url_tags or "",
            "display_link": display_link or "",
        },
    }
    campaign = {"_page_id": page_id, "_instagram_user_id": instagram_user_id, "_url_tags": None}
    body = _build.creative_payload(ad, campaign, images, videos)
    resp = _graph.graph_post(f"{acct}/adcreatives", body)
    return {"creative": resp, "uploaded_images": images, "uploaded_videos": videos}


@mcp.tool()
def creative_delete(creative_id: str) -> Any:
    """Delete a creative (fails if an active ad uses it). Confirm with the user first."""
    return run_meta(["creative", "delete", creative_id, "--force"])


# ---------------------------------------------------------------------------
# Asset uploads + lookups (Graph API)
# ---------------------------------------------------------------------------


@mcp.tool()
def image_upload(path: str, ad_account_id: str | None = None) -> Any:
    """Upload an image to the ad account's library. Returns {hash, url, name}.
    Meta dedupes by content, so re-uploading is harmless."""
    return _graph.upload_image(path, ad_account_id)


@mcp.tool()
def video_upload(path: str, ad_account_id: str | None = None, wait_ready: bool = True) -> Any:
    """Chunked-upload a video to the ad account. Returns {id, status, thumbnail_url}.
    With wait_ready (default) this blocks until Meta finishes processing, which
    a creative needs before it can reference the video."""
    return _graph.upload_video(path, ad_account_id, wait_ready=wait_ready)


@mcp.tool()
def page_list() -> Any:
    """Facebook Pages the token can run ads as (id, name, category). Use the id as page_id."""
    return _graph.list_pages()


@mcp.tool()
def pixel_list(ad_account_id: str | None = None) -> Any:
    """Pixels / datasets on the ad account (id, name, last_fired_time)."""
    return _graph.list_pixels(ad_account_id)


@mcp.tool()
def custom_audience_list(ad_account_id: str | None = None) -> Any:
    """Custom + lookalike audiences on the ad account with approximate sizes and delivery status."""
    return _graph.list_custom_audiences(ad_account_id)


@mcp.tool()
def geo_search(query: str, location_type: str = "city", country_code: str = "US") -> Any:
    """Look up a targeting location key. location_type: city | zip | region | country.
    Returns Meta's rows (key, name, region, country_code, supports_region/city...)."""
    return _graph.search_geo(query, [location_type], country_code=country_code)


@mcp.tool()
def interest_search(query: str) -> Any:
    """Detailed-targeting interest search. Returns id, name, audience size bounds, path."""
    return _graph.search_interests(query)


# ---------------------------------------------------------------------------
# Spreadsheet-driven campaign builder
# ---------------------------------------------------------------------------


@mcp.tool()
def campaign_sheet_template(folder: str) -> Any:
    """Write a blank `campaign.xlsx` (sheets: Campaign / AdSets / Ads) into `folder`.

    Row 2 of AdSets and Ads is a help row (starts with #, ignored on build);
    row 3 is an example to overwrite. Drop the image/video files the Ads sheet
    references into the same folder (subfolders are fine), then run
    `campaign_build` with dry_run=True.
    """
    p = _build.write_template(folder)
    return {"template": str(p), "campaign_keys": _build.CAMPAIGN_KEYS,
            "adset_columns": _build.ADSET_COLUMNS, "ad_columns": _build.AD_COLUMNS}


@mcp.tool()
def campaign_build(workbook_path: str, dry_run: bool = True) -> Any:
    """Build a full Meta campaign (campaign → ad sets → creatives → ads), all PAUSED,
    from a brief spreadsheet plus the assets beside it.

    `workbook_path` accepts any of:
      * `campaign.xlsx` with sheets Campaign / AdSets / Ads (the shipped template,
        or a Google Sheet downloaded as Excel — all tabs come through);
      * a folder containing one CSV per tab, named like Google Sheets exports
        them: `<anything> - Campaign.csv`, `<anything> - AdSets.csv`,
        `<anything> - Ads.csv`;
      * any one of those CSVs (its folder is used).
    Assets are found anywhere under the same folder.

    ALWAYS run with dry_run=True first and show the operator the plan. It
    validates every row, resolves cities / zips / interests / audiences against
    Meta, and returns the exact payloads that would be sent — without creating
    or uploading anything. Only after the operator approves the plan, call
    again with dry_run=False.

    Execution is resumable: created IDs are written to
    `<workbook>.build-state.json` as they happen, so a mid-build failure
    (bad asset, API hiccup) can be fixed in the sheet and rerun without
    duplicating what already exists. Results land in
    `<workbook>-build-results.csv` with every ID.

    Nothing is ever set ACTIVE by this tool. The operator launches from Ads Manager.
    """
    try:
        plan_ = _build.plan(workbook_path)
    except _build.BuildError as e:
        return {"ok": False, "error": str(e)}
    except _graph.GraphApiError as e:
        return {"ok": False, "error": f"Meta rejected a lookup while planning: {e}"}

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "summary": plan_.summary(),
            "campaign_payload": {k: v for k, v in plan_.campaign.items() if not k.startswith("_")},
            "adset_payloads": [a["payload"] for a in plan_.adsets],
            "ads": [{"name": a["name"], "adset": a["adset_name"], "format": a["format"], "assets": a["assets"]} for a in plan_.ads],
            "warnings": plan_.warnings,
            "resolutions": plan_.notes,
        }

    progress: list[str] = []
    try:
        result = _build.execute(plan_, progress.append)
    except _graph.GraphApiError as e:
        return {
            "ok": False,
            "error": str(e),
            "progress": progress,
            "hint": "Fix the cause (sheet value, asset, or permissions) and rerun with dry_run=False. "
                    "Already-created objects are recorded in the state file and will not be duplicated.",
            "state_file": str(_build._state_path(plan_)),
        }
    return {"ok": True, "dry_run": False, **result, "progress": progress, "warnings": plan_.warnings}


# ---------------------------------------------------------------------------
# Creative Images (the visual layer for creative-theme-mining)
# ---------------------------------------------------------------------------
#
# Meta's creative schema is a maze — image URLs hide in several places depending
# on creative type (single-image vs. carousel vs. Advantage+ asset feed). These
# helpers walk the common paths and download whatever they find so Claude can
# see the actual creative as inline ImageContent. This is the prerequisite for
# the creative-theme-mining skill: Claude needs to literally see on-image copy
# and identify visual format before it can cluster creatives by theme.


def _coerce_to_dict(response: Any, what: str = "response") -> dict:
    """Normalize varied CLI response shapes to a dict.

    The Meta CLI sometimes returns:
      - a dict (the expected case)
      - a list of one dict (single-get wrapped in a list)
      - a string like '<AdCreative> { "id": "..." }' (a Python object repr leaked
        into the JSON output, observed on `ad get` for the `creative` field)
    """
    import json
    import re

    if isinstance(response, dict):
        return response
    if isinstance(response, list) and response and isinstance(response[0], dict):
        return response[0]
    if isinstance(response, str):
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            blob = match.group(0)
            try:
                return json.loads(blob)
            except json.JSONDecodeError:
                try:
                    return json.loads(blob.replace("'", '"'))
                except json.JSONDecodeError:
                    pass
    raise RuntimeError(
        f"Could not coerce {what} response to dict; "
        f"got {type(response).__name__}: {str(response)[:200]!r}"
    )


def _meta_graph_api_get(path: str, params: dict[str, Any]) -> Any:
    """Direct GET against graph.facebook.com using ACCESS_TOKEN from env.

    Used only for endpoints the Meta CLI doesn't expose. Currently the sole
    caller is `_resolve_image_hashes_to_urls`, which needs `/act_X/adimages`
    to turn image hashes into full-resolution CDN URLs.

    Kept as a thin alias over `graph.graph_get` so existing callers (image
    hash resolution, video metadata) share one client + API version.
    """
    return _graph.graph_get(path, params, timeout=30)


def _resolve_image_hashes_to_urls(
    hashes: list[str], ad_account_id: str | None = None
) -> dict[str, str]:
    """Look up full-res CDN URLs for image hashes via /act_X/adimages.

    Asset-feed-spec creatives (most modern Meta ads) reference images by hash,
    not URL. The CLI doesn't expose this lookup, so we hit the Graph API
    directly. Returns a `{hash: url}` mapping for whatever resolved; failures
    silently drop out so callers can fall back to other URL sources.

    `ad_account_id` scopes the lookup; hashes only resolve against the account
    that owns them, so cross-account calls MUST pass it (the env default is
    wrong for every other client and the lookup returns empty → callers fall
    back to a 64px thumbnail).
    """
    import json as _json
    import os

    if not hashes:
        return {}
    ad_account_id = ad_account_id or os.environ.get("AD_ACCOUNT_ID", "")
    if not ad_account_id:
        return {}
    if not ad_account_id.startswith("act_"):
        ad_account_id = f"act_{ad_account_id}"

    params = {
        "hashes": _json.dumps(hashes),
        "fields": "hash,url,permalink_url",
        "limit": str(len(hashes)),
    }
    try:
        data = _meta_graph_api_get(f"{ad_account_id}/adimages", params)
    except Exception:
        return {}

    out: dict[str, str] = {}
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            for item in data["data"]:
                if isinstance(item, dict):
                    h = item.get("hash")
                    u = item.get("url") or item.get("permalink_url")
                    if h and u:
                        out[h] = u
        else:
            for k, v in data.items():
                if isinstance(v, dict):
                    u = v.get("url") or v.get("permalink_url")
                    if u:
                        out[k] = u
    return out


def _safe_dict(value: Any) -> dict:
    """Best-effort coerce; never raise. Used inside the extractor where missing
    fields should silently fall through to the next candidate path."""
    if not value:
        return {}
    try:
        return _coerce_to_dict(value)
    except RuntimeError:
        return {}


def _extract_image_urls_from_creative(
    creative: dict, ad_account_id: str | None = None
) -> list[str]:
    """Return image URLs in a creative, walking common nesting paths.

    Priority: direct URLs > full-res URLs resolved from image hashes via the
    Graph API > small thumbnail as last resort. Asset-feed-spec creatives
    (most modern Meta ads) only expose image hashes, not URLs, so the
    hash-resolution step is what unlocks reading on-image copy at full fidelity.

    Robust to Meta CLI's habit of returning nested objects as string reprs
    (e.g. `object_story_spec` may arrive as '<ObjectStorySpec> {...}').
    """
    direct_urls: list[str] = []
    hashes: list[str] = []

    if creative.get("image_url"):
        direct_urls.append(creative["image_url"])
    if creative.get("image_hash"):
        hashes.append(creative["image_hash"])

    oss = _safe_dict(creative.get("object_story_spec"))
    link_data = _safe_dict(oss.get("link_data"))
    if link_data.get("picture"):
        direct_urls.append(link_data["picture"])
    if link_data.get("image_hash"):
        hashes.append(link_data["image_hash"])

    for child in link_data.get("child_attachments") or []:
        c = _safe_dict(child)
        if c.get("picture"):
            direct_urls.append(c["picture"])
        if c.get("image_hash"):
            hashes.append(c["image_hash"])

    afs = _safe_dict(creative.get("asset_feed_spec"))
    for img in afs.get("images") or []:
        i = _safe_dict(img)
        if i.get("url"):
            direct_urls.append(i["url"])
        elif i.get("permalink_url"):
            direct_urls.append(i["permalink_url"])
        elif i.get("hash"):
            hashes.append(i["hash"])

    resolved_urls: list[str] = []
    if hashes:
        unique_hashes = list(dict.fromkeys(hashes))
        resolved = _resolve_image_hashes_to_urls(unique_hashes, ad_account_id)
        for h in unique_hashes:
            if h in resolved:
                resolved_urls.append(resolved[h])

    candidates = direct_urls + resolved_urls
    if not candidates and creative.get("thumbnail_url"):
        candidates.append(creative["thumbnail_url"])

    seen: set[str] = set()
    deduped: list[str] = []
    for u in candidates:
        if u and u not in seen:
            seen.add(u)
            deduped.append(u)
    return deduped
def _download_image(url: str) -> tuple[bytes, str]:
    """Fetch URL bytes and return (raw_bytes, format_suffix).

    Uses stdlib urllib so we don't add a dependency. fbcdn.net is public — no
    auth header needed. The MCP server runs locally on the operator's Mac so
    network egress is whatever the Mac allows (open internet in practice).
    """
    import urllib.request

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "meta-ads/0.1.3"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        ctype = (resp.headers.get("Content-Type") or "image/jpeg").split(";")[0].strip()
    fmt = ctype.split("/")[-1] if "/" in ctype else "jpeg"
    if fmt == "jpg":
        fmt = "jpeg"
    return raw, fmt


def _strip_thumbnail_downscale(url: str) -> str | None:
    """Drop the `stp=` transform param from an fbcdn URL to request the
    original-size asset instead of the 64px thumbnail crop. The oh/oe
    signature covers the path, so the transform hint can usually be removed.
    Returns None when the URL has no stp param (nothing to strip)."""
    from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

    parts = urlparse(url)
    q = parse_qsl(parts.query, keep_blank_values=True)
    q2 = [(k, v) for (k, v) in q if k != "stp"]
    if len(q2) == len(q):
        return None
    return urlunparse(parts._replace(query=urlencode(q2)))


def _download_image_best(url: str) -> tuple[bytes, str]:
    """Download the highest-fidelity variant of `url`: if it carries a
    thumbnail downscale transform, try the stripped (full-size) URL first and
    fall back to the original on any failure."""
    stripped = _strip_thumbnail_downscale(url)
    if stripped:
        try:
            return _download_image(stripped)
        except Exception:
            pass
    return _download_image(url)


@mcp.tool()
def creative_image_get(creative_id: str, ad_account_id: str | None = None) -> Any:
    """Fetch the primary image attached to a creative as inline ImageContent.

    Returns the image so Claude can SEE it — read on-image copy, identify
    creative format (testimonial / product shot / bold-text-on-photo /
    UGC-style / etc.), and assess visual themes. Foundation for performance
    attribution by creative cluster.

    For carousel or Advantage+ creatives with multiple images, returns the
    first/primary one. (Use creative_get to inspect all image hashes.)

    Args:
        creative_id: Meta creative ID (numeric string).
        ad_account_id: The ad account that owns the creative (act_XXXXXXXXX).
            REQUIRED for full-resolution images on any account other than the
            AD_ACCOUNT_ID env default — image-hash lookups are account-scoped,
            and without the right account this silently degrades to a 64px
            thumbnail.
    """
    from mcp.server.fastmcp import Image

    raw = run_meta(["creative", "get", creative_id])
    creative = _coerce_to_dict(raw, what=f"creative {creative_id}")
    urls = _extract_image_urls_from_creative(creative, ad_account_id)
    if not urls:
        raise RuntimeError(
            f"No image URLs found in creative {creative_id}. "
            f"Response keys: {sorted(creative.keys())}"
        )
    raw, fmt = _download_image_best(urls[0])
    return Image(data=raw, format=fmt)


@mcp.tool()
def ad_image_get(ad_id: str, ad_account_id: str | None = None) -> Any:
    """Fetch the primary creative image for an ad as inline ImageContent.

    Resolves the ad to its creative, then returns the image so Claude can
    see it directly. Use this when asked to "look at the creative" or "see
    what an ad looks like" — Claude reads on-image copy and identifies
    format/theme natively from the returned image.

    Args:
        ad_id: Meta ad ID (numeric string).
        ad_account_id: The ad account that owns the ad (act_XXXXXXXXX).
            Pass it whenever working outside the env-default account so
            image hashes resolve to full-resolution URLs; falls back to the
            ad's own account_id field when the ad object exposes one.
    """
    ad_raw = run_meta(["ad", "get", ad_id])
    ad = _coerce_to_dict(ad_raw, what=f"ad {ad_id}")
    if not ad_account_id and ad.get("account_id"):
        ad_account_id = f"act_{ad['account_id']}".replace("act_act_", "act_")
    creative_field = ad.get("creative")
    creative_id: str | None = None
    if creative_field:
        try:
            creative_dict = _coerce_to_dict(creative_field, what="ad.creative")
            creative_id = creative_dict.get("id")
        except RuntimeError:
            creative_id = None
    if not creative_id:
        raise RuntimeError(
            f"Ad {ad_id} has no resolvable creative ID. "
            f"creative field: {str(creative_field)[:200]!r}"
        )
    return creative_image_get(creative_id, ad_account_id)

# ---------------------------------------------------------------------------
# Video creative analysis
# ---------------------------------------------------------------------------
#
# A video ad can't be diagnosed from body copy alone: the hook lives in the
# first ~3 seconds of spoken script, which appears nowhere in the creative's
# text fields. `ad_video_get` reads the ad's video and returns the transcript
# so Claude can analyze the actual script — theme, hook, and messaging.
#
# Nothing is written to disk. ffmpeg reads the video over HTTP and emits only
# the decoded audio (or a single frame) to a pipe, so the video itself is never
# stored anywhere — it streams through memory and is gone when the call ends.
# This is both cleaner and faster than downloading: pulling just the audio
# stream takes ~1s versus ~7s to fetch the whole file.
#
# Two rules carried over from the local video-analysis workflow this was
# ported from:
#   1. Never use a `.en` whisper model unless the audio is confirmed English —
#      `.en` models TRANSLATE non-English audio instead of transcribing it,
#      silently destroying the original language. Default is `small`.
#   2. When frames are requested, weight them toward the opening. Three of the
#      five land inside the 3-second hook window.

_FFMPEG_HINT = (
    "ffmpeg was not found on PATH, but video analysis requires it (it's what "
    "reads the video and extracts the audio).\n"
    "  macOS:  brew install ffmpeg\n"
    "  Linux:  sudo apt install ffmpeg\n"
    "Then restart the MCP server (or Claude Code) so it inherits the updated "
    "PATH. To confirm: `ffmpeg -version`."
)

_UA = "meta-ads/0.5.0"


def _require_binary(name: str, hint: str) -> str:
    """Locate a system binary, falling back to the standard Homebrew prefixes.

    The MCP server is launched by Claude Code rather than an interactive
    shell, so its inherited PATH may omit /opt/homebrew/bin even when the
    binary is installed. Check those explicitly before failing.
    """
    import shutil
    from pathlib import Path

    found = shutil.which(name)
    if found:
        return found
    for candidate in (f"/opt/homebrew/bin/{name}", f"/usr/local/bin/{name}"):
        if Path(candidate).is_file():
            return candidate
    raise RuntimeError(hint)


def _extract_video_id_from_creative(creative: dict) -> str | None:
    """Find the video id in a creative, walking the common nesting paths.

    Mirrors `_extract_image_urls_from_creative`: `object_story_spec.video_data`
    is the standard placement, `asset_feed_spec.videos` covers Advantage+ /
    dynamic creatives, and a bare `video_id` shows up on some legacy ones.
    """
    if creative.get("video_id"):
        return str(creative["video_id"])

    oss = _safe_dict(creative.get("object_story_spec"))
    video_data = _safe_dict(oss.get("video_data"))
    if video_data.get("video_id"):
        return str(video_data["video_id"])

    afs = _safe_dict(creative.get("asset_feed_spec"))
    for entry in afs.get("videos") or []:
        v = _safe_dict(entry)
        if v.get("video_id"):
            return str(v["video_id"])
    return None


def _video_source_denied(video_id: str, reason: str) -> RuntimeError:
    """Build the actionable error for a withheld `source` field.

    `source` is permission-sensitive: for page-owned videos Meta often
    withholds it from a system-user token and requires a Page access token.
    That's a credentials problem, not a bug, so say so and give the operator
    both the fix and the degraded path.
    """
    return RuntimeError(
        f"Could not get a readable source URL for video {video_id}: "
        f"{reason}\n\n"
        "The `source` field is permission-gated. For page-owned videos Meta "
        "usually requires a PAGE access token (scopes: pages_read_engagement, "
        "pages_show_list) rather than the system-user token in ACCESS_TOKEN.\n\n"
        "Options:\n"
        "  1. Generate a Page access token for the ad's page and set it as "
        "ACCESS_TOKEN, then retry.\n"
        "  2. Proceed without the video: call ad_image_get for the video "
        "thumbnail and diagnose the copy layer only. If you do this, flag the "
        'output "(creative unverified — copy-layer diagnosis only)" so nobody '
        "mistakes a copy-only read for a full creative diagnosis."
    )


def _fetch_video_meta(video_id: str) -> dict:
    """Fetch the source URL + duration for a video via the Graph API.

    The `meta ads` CLI doesn't expose /{video_id}, so this is a legitimate
    direct-Graph case (same justification as the adimages hash lookup).
    """
    import json as _json
    import urllib.error

    fields = "source,length,title,created_time,permalink_url"
    try:
        data = _meta_graph_api_get(video_id, {"fields": fields})
    except urllib.error.HTTPError as e:
        try:
            err = _json.loads(e.read()).get("error", {})
        except Exception:
            err = {}
        reason = err.get("message") or f"HTTP {e.code} from the Graph API"
        raise _video_source_denied(video_id, reason) from e
    except Exception as e:
        raise _video_source_denied(video_id, f"{type(e).__name__}: {e}") from e

    if not isinstance(data, dict):
        raise _video_source_denied(video_id, "unexpected Graph API response shape")
    if not data.get("source"):
        raise _video_source_denied(
            video_id,
            "the Graph API returned the video object but omitted `source` "
            f"(fields present: {sorted(data.keys())})",
        )
    return data


def _stream_audio(ffmpeg: str, source_url: str) -> bytes:
    """Return decoded mono 16 kHz WAV audio for a remote video.

    ffmpeg reads the video over HTTP and writes only the audio to a pipe, so
    the video never touches disk. `-vn` drops the video stream, which is why
    this is faster than downloading the file: ffmpeg fetches what it needs to
    demux audio and stops.
    """
    import subprocess

    proc = subprocess.run(
        [
            ffmpeg, "-v", "error", "-user_agent", _UA,
            "-i", source_url,
            "-vn", "-ac", "1", "-ar", "16000",
            "-f", "wav", "pipe:1",
        ],
        capture_output=True,
        check=False,
        timeout=300,
    )
    if proc.returncode != 0 or not proc.stdout:
        detail = (proc.stderr or b"").decode("utf-8", "replace").strip()[:300]
        raise RuntimeError(
            "ffmpeg could not read an audio track from the video "
            f"({detail or 'no stderr'}). The ad may be silent or video-only — "
            "if so, diagnose it from the on-screen copy instead "
            "(include_keyframes=True)."
        )
    return proc.stdout


def _transcribe_audio(
    audio: bytes, model_size: str, language: str | None
) -> dict:
    """Transcribe in-memory WAV audio with faster-whisper.

    Returns `language`, `timestamped` display lines, and a flat `text` script.
    A silent video is a real and diagnosable case, so no-speech comes back as
    empty segments rather than an error.
    """
    import io

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        # Not installed on this platform (Intel Macs — see pyproject.toml).
        # Degrade rather than raise so the rest of the call still returns.
        return {
            "unavailable": True,
            "error": (
                "Local transcription isn't available on this machine "
                "(faster-whisper needs onnxruntime, which has no macOS "
                "x86_64 build). Run this from an Apple silicon Mac or Linux "
                "to read video scripts."
            ),
            "timestamped": [],
            "text": "",
        }

    # int8 on CPU: the accuracy cost is negligible for ad voiceover and it
    # keeps a 30s clip at a few seconds on Apple silicon.
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        io.BytesIO(audio),
        word_timestamps=True,
        vad_filter=True,
        language=language,
    )

    timestamped: list[str] = []
    plain: list[str] = []
    for seg in segments:
        text = (seg.text or "").strip()
        if not text:
            continue
        timestamped.append(f"[{seg.start:6.2f}s → {seg.end:6.2f}s] {text}")
        plain.append(text)

    return {
        "language": getattr(info, "language", None),
        "timestamped": timestamped,
        "text": " ".join(plain),
    }


def _keyframe_plan(duration: float) -> list[tuple[float, str]]:
    """Choose keyframe timestamps, weighted toward the hook.

    0s / 1s / 3s cover the scroll-stop window, then midpoint and final frame
    cover the payoff and the end card. Timestamps are clamped to the clip and
    deduped, so a 2-second video returns fewer than five frames instead of
    five copies of the same one.
    """
    last = max(duration - 0.15, 0.0)
    wanted: list[tuple[float, str]] = [
        (0.0, "opening frame (hook)"),
        (1.0, "hook"),
        (3.0, "end of hook window"),
        (duration / 2, "midpoint"),
        (last, "final frame (end card / CTA)"),
    ]

    plan: list[tuple[float, str]] = []
    seen: set[float] = set()
    for ts, role in wanted:
        ts = min(max(ts, 0.0), last)
        key = round(ts, 1)
        if key in seen:
            continue
        seen.add(key)
        plan.append((ts, f"{ts:.1f}s — {role}"))

    # Sort by timestamp: on very short clips the clamp above can push a later
    # role (e.g. "hook" at 1.0s) below an earlier one, and the frames are read
    # as a sequence, so they must come back in chronological order.
    plan.sort(key=lambda item: item[0])
    return plan


def _extract_keyframes(
    ffmpeg: str, source_url: str, plan: list[tuple[float, str]], width: int = 768
) -> list[tuple[str, bytes]]:
    """Grab one JPEG per planned timestamp, straight from the URL to a pipe.

    ffmpeg seeks with HTTP range requests, so this reads only the bytes around
    each timestamp and writes nothing to disk. Frames that fail are skipped.
    Downscaled to `width` because on-screen ad copy stays legible well below
    native resolution.
    """
    import subprocess

    frames: list[tuple[str, bytes]] = []
    for ts, label in plan:
        proc = subprocess.run(
            [
                ffmpeg, "-v", "error", "-user_agent", _UA,
                "-ss", f"{ts:.3f}", "-i", source_url,
                "-frames:v", "1", "-vf", f"scale={width}:-2",
                "-f", "image2", "-c:v", "mjpeg", "pipe:1",
            ],
            capture_output=True,
            check=False,
            timeout=120,
        )
        if proc.returncode == 0 and proc.stdout:
            frames.append((label, proc.stdout))
    return frames


def _probe_duration(source_url: str) -> float | None:
    """Read a remote video's duration with ffprobe. None if unavailable."""
    import subprocess

    try:
        ffprobe = _require_binary("ffprobe", _FFMPEG_HINT)
    except RuntimeError:
        return None
    proc = subprocess.run(
        [
            ffprobe, "-v", "error", "-user_agent", _UA,
            "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1", source_url,
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if proc.returncode != 0:
        return None
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return None


@mcp.tool()
def ad_video_get(
    ad_id: str,
    ad_account_id: str | None = None,
    whisper_model: str = "small",
    language: str | None = None,
    include_keyframes: bool = False,
) -> Any:
    """Read a video ad's spoken script so Claude can diagnose the creative.

    The video counterpart to `ad_image_get`. Resolves the ad to its creative
    and video, then returns the transcript with timestamps — the theme, hook,
    and messaging of the ad as actually spoken. Use this whenever the creative
    is a video; body copy alone can't tell you what the hook was.

    Nothing is downloaded or saved. ffmpeg streams the audio out of the video
    over the network and it's transcribed in memory, so no files are left
    behind. A 30-second ad takes a few seconds.

    First call downloads the whisper model (~500 MB for `small`) and takes
    ~30-60s; later calls reuse the cache. Requires `ffmpeg` on PATH.

    If the creative is a static image, this raises and tells you to use
    `ad_image_get` instead.

    Args:
        ad_id: Meta ad ID (numeric string).
        ad_account_id: The ad account that owns the ad (act_XXXXXXXXX).
            Pass it whenever working outside the env-default account; falls
            back to the ad's own account_id when the ad object exposes one.
        whisper_model: tiny / base / small (default) / medium / large-v3.
            NEVER pass a `.en` model unless you know the audio is English —
            `.en` models translate non-English audio instead of transcribing
            it, silently losing the original language.
        language: ISO code (e.g. "es") to skip auto-detection. Leave unset to
            let whisper detect; pair a non-English language with a non-`.en`
            model.
        include_keyframes: Off by default — the transcript is what carries the
            script. Set True to also get 5 still frames (0s / 1s / 3s /
            midpoint / final) when the *visual* matters: judging scroll-stop
            from the opening frame, or reading on-screen text in an ad whose
            message is carried visually rather than spoken. Costs noticeably
            more context, so leave it off for bulk script analysis.
    """
    from mcp.server.fastmcp import Image

    ffmpeg = _require_binary("ffmpeg", _FFMPEG_HINT)

    ad_raw = run_meta(["ad", "get", ad_id])
    ad = _coerce_to_dict(ad_raw, what=f"ad {ad_id}")
    if not ad_account_id and ad.get("account_id"):
        ad_account_id = f"act_{ad['account_id']}".replace("act_act_", "act_")

    creative_field = ad.get("creative")
    creative_id: str | None = None
    if creative_field:
        try:
            creative_dict = _coerce_to_dict(creative_field, what="ad.creative")
            creative_id = creative_dict.get("id")
        except RuntimeError:
            creative_id = None
    if not creative_id:
        raise RuntimeError(
            f"Ad {ad_id} has no resolvable creative ID. "
            f"creative field: {str(creative_field)[:200]!r}"
        )

    creative_raw = run_meta(["creative", "get", creative_id])
    creative = _coerce_to_dict(creative_raw, what=f"creative {creative_id}")
    video_id = _extract_video_id_from_creative(creative)
    if not video_id:
        raise RuntimeError(
            f"Creative {creative_id} on ad {ad_id} has no video_id — this is "
            "most likely a static image or carousel creative. Use "
            "ad_image_get(ad_id) instead. "
            f"(Creative keys: {sorted(creative.keys())})"
        )

    meta = _fetch_video_meta(video_id)
    source_url = meta["source"]
    duration = float(meta.get("length") or 0.0)

    audio = _stream_audio(ffmpeg, source_url)
    transcript = _transcribe_audio(audio, whisper_model, language)
    del audio  # released now rather than held while frames are pulled

    frames: list[tuple[str, bytes]] = []
    if include_keyframes:
        if duration <= 0:
            # Graph omitted `length`; ask ffprobe so the plan has a real
            # duration to work from.
            duration = _probe_duration(source_url) or 0.0
        frames = _extract_keyframes(ffmpeg, source_url, _keyframe_plan(duration))

    lines = [
        f"# Video creative — ad {ad_id}",
        "",
        f"- Ad name: {ad.get('name') or '(unnamed)'}",
        f"- Creative: {creative_id}  |  Video: {video_id}",
        f"- Ad account: {ad_account_id or '(env default)'}",
        f"- Video title: {meta.get('title') or '(untitled)'}",
        f"- Duration: {duration:.2f}s" if duration else "- Duration: unknown",
    ]
    if transcript.get("language"):
        lines.append(
            f"- Detected language: {transcript['language']}"
            f" (whisper model: {whisper_model})"
        )
    lines.append("")

    if transcript.get("unavailable"):
        lines += [
            "## Transcript — unavailable on this machine",
            "",
            f"_{transcript['error']}_",
            "",
            "Diagnose from the on-screen copy instead (re-run with "
            "include_keyframes=True) and flag the result "
            "**(creative unverified — copy-layer diagnosis only)**.",
        ]
    elif not transcript["timestamped"]:
        lines += [
            "## Transcript",
            "",
            "_No speech detected — likely a music-only or text-on-screen "
            "creative. Re-run with include_keyframes=True to read the "
            "on-screen copy._",
        ]
    else:
        lines += ["## Transcript (timestamped)", ""]
        lines += transcript["timestamped"]
        lines += ["", "## Script (flat)", "", transcript["text"]]

    if include_keyframes:
        lines += [
            "",
            f"## Keyframes ({len(frames)})",
            "",
            "Frames follow as images. The first three sit inside the "
            "3-second hook window — judge scroll-stop from those.",
        ]

    out: list[Any] = ["\n".join(lines)]
    for label, data in frames:
        out.append(f"Keyframe — {label}")
        out.append(Image(data=data, format="jpeg"))
    return out

# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------


@mcp.tool()
def insights_get(
    campaign_id: str | None = None,
    adset_id: str | None = None,
    ad_id: str | None = None,
    date_preset: str | None = "last_7d",
    since: str | None = None,
    until: str | None = None,
    fields: list[str] | None = None,
    breakdown: str | None = None,
    sort: str | None = None,
    limit: int = 50,
    ad_account_id: str | None = None,
) -> Any:
    """Pull performance insights.

    Pass one of `campaign_id`, `adset_id`, `ad_id`, or none for account-level.
    For account-level insights, scope with `ad_account_id` (no per-call
    object id flag exists on the underlying CLI — account is set via env).

    Args:
        campaign_id / adset_id / ad_id: Scope to one object. Mutually exclusive.
        date_preset: today, yesterday, last_3d, last_7d, last_14d, last_30d,
            last_90d, this_month, last_month. Default last_7d.
        since, until: Custom date range (YYYY-MM-DD). Override date_preset when both set.
        fields: Metrics to return. Common: spend, impressions, clicks, ctr, cpc,
            cpm, reach, frequency, actions, conversions, cost_per_action_type.
            Default if omitted: spend, impressions, clicks, ctr, cpc, reach.
        breakdown: One of age, gender, country, publisher_platform,
            device_platform, platform_position, impression_device. CLI accepts
            one at a time.
        sort: e.g. "spend_descending".
        limit: Max rows. Default 50.
        ad_account_id: Override the default ad account for this call.
    """
    argv = ["insights", "get"]
    argv += _flag("--campaign-id", campaign_id)
    argv += _flag("--adset-id", adset_id)
    argv += _flag("--ad-id", ad_id)
    if since and until:
        argv += _flag("--since", since)
        argv += _flag("--until", until)
    else:
        argv += _flag("--date-preset", date_preset)
    argv += _flag("--fields", fields)
    argv += _flag("--breakdown", breakdown)
    argv += _flag("--sort", sort)
    argv += _flag("--limit", limit)
    return run_meta(argv, extra_env=_account_env(ad_account_id))


# ---------------------------------------------------------------------------
# Catalog / Product / Dataset / Page surfaces — TODO
# ---------------------------------------------------------------------------
#
# These are intentionally not implemented in v0.1.0. The CLI calls follow the
# same pattern: define a function with typed args, build an argv list with
# `_flag`, and `return run_meta(argv)`.
#
# Reference (from Meta's CLI docs):
#   meta ads catalog create --name "My Catalog"
#   meta ads product-item create --catalog-id ID --retailer-id sku --name "..." --url ... --price ... --currency USD --image-url ...
#   meta ads product-set list --catalog-id ID
#   meta ads dataset create --name "Website Pixel"
#   meta ads dataset connect DATASET_ID --ad-account-id ID --catalog-id ID
#   meta ads page list
#
# Add these as you hit real client workflows that need them.


# ---------------------------------------------------------------------------
# Generic escape hatch — call the raw CLI when no typed tool exists yet
# ---------------------------------------------------------------------------


@mcp.tool()
def meta_raw(args: list[str], output: str = "json") -> Any:
    """Escape hatch: run any `meta ads <args...>` command not yet wrapped above.

    Prefer typed tools. Use this only when prototyping a surface that doesn't
    have a dedicated tool yet (e.g. catalog operations in v0.1.0).

    Args:
        args: Arguments to pass after `meta ads`. Example: ["catalog", "list"].
        output: json (default), table, or plain.
    """
    try:
        return run_meta(args, output=output)
    except MetaCliError as e:
        return {"error": str(e), "returncode": e.returncode}


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
