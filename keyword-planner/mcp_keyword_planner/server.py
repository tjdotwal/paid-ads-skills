"""MCP server exposing Google Ads Keyword Planner.

Talks to the Google Ads API directly rather than wrapping a third-party binary.
The binary this replaced (ncosentino/google-keyword-planner-mcp v0.1.0) shipped
two payloads that v23 rejects: it sent `campaignForecastSpec` where v23 expects
`campaign`, and it dropped the historical-metrics response on the floor. Both
are fixed here and covered by the shapes below.

Credentials come from ~/.env, the same source as the sibling Google Ads plugin.
"""

from typing import Any, Dict, List, Optional
from datetime import date, timedelta
import logging
import os

import requests

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("keyword_planner_server")

mcp = FastMCP(
    "keyword-planner",
    dependencies=["google-auth", "requests", "python-dotenv"],
)

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - dotenv is a declared dependency
    logger.warning("python-dotenv not installed, skipping .env file loading")

SCOPES = ["https://www.googleapis.com/auth/adwords"]
API_VERSION = "v23"
BASE_URL = f"https://googleads.googleapis.com/{API_VERSION}"
TOKEN_URI = "https://oauth2.googleapis.com/token"

GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
GOOGLE_ADS_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "")
GOOGLE_ADS_CREDENTIALS_PATH = os.environ.get("GOOGLE_ADS_CREDENTIALS_PATH")
GOOGLE_ADS_AUTH_TYPE = os.environ.get("GOOGLE_ADS_AUTH_TYPE", "oauth")

# Keyword Planner takes numeric constant IDs. Accepting friendly codes here
# keeps callers from having to look them up; anything unrecognised is passed
# through so a raw ID or full resource name still works.
LANGUAGE_IDS = {
    "en": "1000", "de": "1001", "fr": "1002", "es": "1003", "it": "1004",
    "nl": "1010", "pt": "1014", "sv": "1015", "da": "1009", "no": "1013",
    "fi": "1011", "pl": "1030", "ja": "1005", "zh": "1017", "ko": "1012",
}

GEO_IDS = {
    "US": "2840", "CA": "2124", "GB": "2826", "UK": "2826", "AU": "2036",
    "NZ": "2554", "IE": "2372", "DE": "2276", "FR": "2250", "ES": "2724",
    "IT": "2380", "MX": "2484", "BR": "2076", "IN": "2356",
}


def format_customer_id(customer_id: Any) -> str:
    """Normalise a customer ID to 10 digits, no dashes."""
    digits = "".join(c for c in str(customer_id) if c.isdigit())
    if not digits:
        raise ValueError(f"Customer ID {customer_id!r} contains no digits")
    return digits.zfill(10)


def language_resource(language: Optional[str]) -> str:
    """Accept 'en', '1000', or 'languageConstants/1000'."""
    if not language:
        return "languageConstants/1000"
    value = str(language).strip()
    if value.startswith("languageConstants/"):
        return value
    resolved = LANGUAGE_IDS.get(value.lower(), value)
    return f"languageConstants/{resolved}"


def geo_resources(geo_targets: Optional[List[str]]) -> List[str]:
    """Accept ['US'], ['2840'], or ['geoTargetConstants/2840']."""
    if not geo_targets:
        return []
    out = []
    for geo in geo_targets:
        value = str(geo).strip()
        if value.startswith("geoTargetConstants/"):
            out.append(value)
            continue
        resolved = GEO_IDS.get(value.upper(), value)
        out.append(f"geoTargetConstants/{resolved}")
    return out


def get_credentials():
    """Build credentials from ~/.env.

    A refresh token is preferred because it needs no browser and no cached
    token file, which is what makes this work when Claude launches the server
    headless. The credentials-path and service-account paths mirror the
    sibling Google Ads plugin so an existing setup keeps working.
    """
    if GOOGLE_ADS_AUTH_TYPE.lower() == "service_account":
        if not GOOGLE_ADS_CREDENTIALS_PATH:
            raise ValueError(
                "GOOGLE_ADS_AUTH_TYPE=service_account requires GOOGLE_ADS_CREDENTIALS_PATH"
            )
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_ADS_CREDENTIALS_PATH, scopes=SCOPES
        )
        impersonate = os.environ.get("GOOGLE_ADS_IMPERSONATION_EMAIL")
        if impersonate:
            creds = creds.with_subject(impersonate)
        return creds

    refresh_token = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")

    if refresh_token and client_id and client_secret:
        return Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri=TOKEN_URI,
            scopes=SCOPES,
        )

    if GOOGLE_ADS_CREDENTIALS_PATH and os.path.exists(GOOGLE_ADS_CREDENTIALS_PATH):
        return Credentials.from_authorized_user_file(
            GOOGLE_ADS_CREDENTIALS_PATH, SCOPES
        )

    raise ValueError(
        "No usable credentials. Set GOOGLE_ADS_REFRESH_TOKEN with "
        "GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET in ~/.env, or point "
        "GOOGLE_ADS_CREDENTIALS_PATH at an authorized-user token file."
    )


def get_headers(login_customer_id: Optional[str] = None) -> Dict[str, str]:
    if not GOOGLE_ADS_DEVELOPER_TOKEN:
        raise ValueError("GOOGLE_ADS_DEVELOPER_TOKEN is not set. Add it to ~/.env.")

    creds = get_credentials()
    if not creds.valid:
        creds.refresh(Request())

    headers = {
        "Authorization": f"Bearer {creds.token}",
        "developer-token": GOOGLE_ADS_DEVELOPER_TOKEN,
        "content-type": "application/json",
    }

    effective_mcc = login_customer_id or GOOGLE_ADS_LOGIN_CUSTOMER_ID
    if effective_mcc:
        headers["login-customer-id"] = format_customer_id(effective_mcc)
    return headers


def resolve_customer_id(customer_id: Optional[str]) -> str:
    target = customer_id or GOOGLE_ADS_CUSTOMER_ID
    if not target:
        raise ValueError(
            "No customer_id given and GOOGLE_ADS_CUSTOMER_ID is not set in ~/.env."
        )
    return format_customer_id(target)


def call_api(
    endpoint: str,
    payload: Dict[str, Any],
    customer_id: Optional[str],
    login_customer_id: Optional[str],
) -> Dict[str, Any]:
    cid = resolve_customer_id(customer_id)
    url = f"{BASE_URL}/customers/{cid}:{endpoint}"
    response = requests.post(
        url, headers=get_headers(login_customer_id), json=payload, timeout=120
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Google Ads API returned HTTP {response.status_code} for {endpoint} "
            f"on customer {cid}:\n{response.text}"
        )
    return response.json()


def micros_to_amount(micros: Any) -> Optional[float]:
    if micros in (None, ""):
        return None
    return int(micros) / 1_000_000


def format_money(micros: Any) -> str:
    amount = micros_to_amount(micros)
    return "—" if amount is None else f"{amount:,.2f}"


def format_int(value: Any) -> str:
    if value in (None, ""):
        return "—"
    return f"{int(float(value)):,}"


def render_keyword_table(rows: List[Dict[str, Any]], title: str) -> str:
    """Render keyword metrics as an aligned table.

    Costs are left unlabelled because Keyword Planner reports them in the
    account's own currency, which varies across the MCCs this runs against.
    """
    if not rows:
        return f"{title}\n\nNo keywords returned."

    header = ["Keyword", "Avg monthly", "Competition", "Low bid", "High bid"]
    table = [header] + [
        [
            r["text"],
            format_int(r.get("avg_monthly_searches")),
            r.get("competition") or "—",
            format_money(r.get("low_bid_micros")),
            format_money(r.get("high_bid_micros")),
        ]
        for r in rows
    ]
    widths = [max(len(row[i]) for row in table) for i in range(len(header))]
    lines = [
        "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(table[0])),
        "  ".join("-" * widths[i] for i in range(len(header))),
    ]
    lines += [
        "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))
        for row in table[1:]
    ]
    return (
        f"{title}\n\n"
        + "\n".join(lines)
        + f"\n\n{len(rows)} keyword(s). Bid columns are top-of-page estimates "
        "in the account's currency."
    )


def scope_line(
    customer_id: Optional[str],
    login_customer_id: Optional[str],
    language: str,
    geos: List[str],
) -> str:
    cid = resolve_customer_id(customer_id)
    mcc = login_customer_id or GOOGLE_ADS_LOGIN_CUSTOMER_ID or "none"
    where = ", ".join(g.split("/")[-1] for g in geos) if geos else "all locations"
    return (
        f"Account {cid} (MCC {mcc}) · language {language.split('/')[-1]} · {where}"
    )


@mcp.tool()
async def generate_keyword_ideas(
    seed_keywords: Optional[List[str]] = None,
    page_url: Optional[str] = None,
    language: str = "en",
    geo_targets: Optional[List[str]] = None,
    network: str = "GOOGLE_SEARCH",
    page_size: int = 200,
    customer_id: Optional[str] = None,
    login_customer_id: Optional[str] = None,
) -> str:
    """Discover new keyword ideas with search volume, competition, and bid estimates.

    Give seed_keywords, a page_url, or both. Results are sorted by average
    monthly searches, highest first.

    Args:
        seed_keywords: Seed terms to expand, e.g. ["managed it services"].
        page_url: A landing page to mine for ideas.
        language: "en", "1000", or "languageConstants/1000".
        geo_targets: Country codes or geo IDs, e.g. ["CA"] or ["2124"].
            Omit for worldwide volume, which is usually far higher than a
            local advertiser will actually see.
        network: GOOGLE_SEARCH or GOOGLE_SEARCH_AND_PARTNERS.
        page_size: Maximum ideas to return.
        customer_id: Account to bill the request against. Defaults to
            GOOGLE_ADS_CUSTOMER_ID in ~/.env.
        login_customer_id: MCC override. Defaults to
            GOOGLE_ADS_LOGIN_CUSTOMER_ID in ~/.env.
    """
    if not seed_keywords and not page_url:
        return "Error: provide seed_keywords, page_url, or both."

    lang = language_resource(language)
    geos = geo_resources(geo_targets)

    payload: Dict[str, Any] = {
        "language": lang,
        "keywordPlanNetwork": network,
        "pageSize": page_size,
    }
    if geos:
        payload["geoTargetConstants"] = geos

    if seed_keywords and page_url:
        payload["keywordAndUrlSeed"] = {"url": page_url, "keywords": seed_keywords}
    elif seed_keywords:
        payload["keywordSeed"] = {"keywords": seed_keywords}
    else:
        payload["urlSeed"] = {"url": page_url}

    try:
        data = call_api(
            "generateKeywordIdeas", payload, customer_id, login_customer_id
        )
    except Exception as exc:
        return f"Error generating keyword ideas: {exc}"

    rows = []
    for result in data.get("results", []):
        metrics = result.get("keywordIdeaMetrics") or {}
        rows.append(
            {
                "text": result.get("text", ""),
                "avg_monthly_searches": metrics.get("avgMonthlySearches"),
                "competition": metrics.get("competition"),
                "low_bid_micros": metrics.get("lowTopOfPageBidMicros"),
                "high_bid_micros": metrics.get("highTopOfPageBidMicros"),
            }
        )
    rows.sort(key=lambda r: int(r["avg_monthly_searches"] or 0), reverse=True)

    seeds = ", ".join(seed_keywords) if seed_keywords else page_url
    title = (
        f"Keyword ideas for: {seeds}\n"
        f"{scope_line(customer_id, login_customer_id, lang, geos)}"
    )
    return render_keyword_table(rows, title)


@mcp.tool()
async def get_historical_metrics(
    keywords: List[str],
    language: str = "en",
    geo_targets: Optional[List[str]] = None,
    network: str = "GOOGLE_SEARCH",
    include_monthly_breakdown: bool = False,
    customer_id: Optional[str] = None,
    login_customer_id: Optional[str] = None,
) -> str:
    """Pull search volume and competition for keywords you already have.

    Use this to validate an existing keyword list. For discovering new
    keywords, use generate_keyword_ideas instead.

    Args:
        keywords: The exact keywords to look up.
        language: "en", "1000", or "languageConstants/1000".
        geo_targets: Country codes or geo IDs, e.g. ["CA"]. Omit for worldwide.
        network: GOOGLE_SEARCH or GOOGLE_SEARCH_AND_PARTNERS.
        include_monthly_breakdown: Append month-by-month volume per keyword.
        customer_id: Account to bill the request against.
        login_customer_id: MCC override.
    """
    if not keywords:
        return "Error: provide at least one keyword."

    lang = language_resource(language)
    geos = geo_resources(geo_targets)

    payload: Dict[str, Any] = {
        "keywords": keywords,
        "language": lang,
        "keywordPlanNetwork": network,
        "historicalMetricsOptions": {"includeAverageCpc": True},
    }
    if geos:
        payload["geoTargetConstants"] = geos

    try:
        data = call_api(
            "generateKeywordHistoricalMetrics", payload, customer_id, login_customer_id
        )
    except Exception as exc:
        return f"Error getting historical metrics: {exc}"

    results = data.get("results", [])
    rows = []
    monthly_sections = []
    for result in results:
        metrics = result.get("keywordMetrics") or {}
        text = result.get("text", "")
        rows.append(
            {
                "text": text,
                "avg_monthly_searches": metrics.get("avgMonthlySearches"),
                "competition": metrics.get("competition"),
                "low_bid_micros": metrics.get("lowTopOfPageBidMicros"),
                "high_bid_micros": metrics.get("highTopOfPageBidMicros"),
            }
        )
        if include_monthly_breakdown:
            volumes = metrics.get("monthlySearchVolumes") or []
            if volumes:
                points = ", ".join(
                    f"{v.get('month','')[:3].title()} {v.get('year','')}: "
                    f"{format_int(v.get('monthlySearches'))}"
                    for v in volumes
                )
                monthly_sections.append(f"  {text} — {points}")

    rows.sort(key=lambda r: int(r["avg_monthly_searches"] or 0), reverse=True)

    title = (
        f"Historical metrics for {len(keywords)} keyword(s)\n"
        f"{scope_line(customer_id, login_customer_id, lang, geos)}"
    )
    output = render_keyword_table(rows, title)

    missing = {k.lower() for k in keywords} - {
        r.get("text", "").lower() for r in results
    }
    if missing:
        output += "\n\nNo data returned for: " + ", ".join(sorted(missing))
    if monthly_sections:
        output += "\n\nMonthly breakdown:\n" + "\n".join(monthly_sections)
    return output


@mcp.tool()
async def get_keyword_forecast(
    keywords: List[str],
    max_cpc: float = 5.0,
    daily_budget: Optional[float] = None,
    forecast_days: int = 30,
    match_type: str = "PHRASE",
    language: str = "en",
    geo_targets: Optional[List[str]] = None,
    network: str = "GOOGLE_SEARCH",
    customer_id: Optional[str] = None,
    login_customer_id: Optional[str] = None,
) -> str:
    """Forecast impressions, clicks, cost, and conversions for a keyword set.

    Models a single ad group bidding manual CPC. The forecast window starts
    tomorrow, since Keyword Planner only forecasts forward.

    Args:
        keywords: Keywords to forecast.
        max_cpc: Max CPC bid in account currency units, not micros.
        daily_budget: Daily budget in account currency units. Defaults to
            10x max_cpc, which is loose enough not to throttle the forecast.
        forecast_days: Length of the forecast window, up to 365.
        match_type: EXACT, PHRASE, or BROAD.
        language: "en", "1000", or "languageConstants/1000".
        geo_targets: Country codes or geo IDs, e.g. ["CA"].
        network: GOOGLE_SEARCH or GOOGLE_SEARCH_AND_PARTNERS.
        customer_id: Account to bill the request against.
        login_customer_id: MCC override.
    """
    if not keywords:
        return "Error: provide at least one keyword."
    if forecast_days < 1 or forecast_days > 365:
        return "Error: forecast_days must be between 1 and 365."
    if match_type.upper() not in {"EXACT", "PHRASE", "BROAD"}:
        return "Error: match_type must be EXACT, PHRASE, or BROAD."

    lang = language_resource(language)
    geos = geo_resources(geo_targets)
    max_cpc_micros = int(round(max_cpc * 1_000_000))
    budget_micros = int(
        round((daily_budget if daily_budget is not None else max_cpc * 10) * 1_000_000)
    )

    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=forecast_days - 1)

    campaign: Dict[str, Any] = {
        "keywordPlanNetwork": network,
        "biddingStrategy": {
            "manualCpcBiddingStrategy": {
                "maxCpcBidMicros": str(max_cpc_micros),
                "dailyBudgetMicros": str(budget_micros),
            }
        },
        "languageConstants": [lang],
        "adGroups": [
            {
                "maxCpcBidMicros": str(max_cpc_micros),
                "biddableKeywords": [
                    {
                        "keyword": {"text": kw, "matchType": match_type.upper()},
                        "maxCpcBidMicros": str(max_cpc_micros),
                    }
                    for kw in keywords
                ],
            }
        ],
    }
    if geos:
        campaign["geoModifiers"] = [
            {"geoTargetConstant": geo, "bidModifier": 1.0} for geo in geos
        ]

    payload = {
        "campaign": campaign,
        "forecastPeriod": {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
        },
    }

    try:
        data = call_api(
            "generateKeywordForecastMetrics", payload, customer_id, login_customer_id
        )
    except Exception as exc:
        return f"Error getting keyword forecast: {exc}"

    m = data.get("campaignForecastMetrics") or {}
    if not m:
        return "No forecast returned. The keywords may have too little volume to model."

    impressions = m.get("impressions")
    clicks = m.get("clicks")
    conversions = m.get("conversions")
    ctr = m.get("clickThroughRate")
    conv_rate = m.get("conversionRate")

    lines = [
        f"Forecast for {len(keywords)} keyword(s), {match_type.upper()} match",
        scope_line(customer_id, login_customer_id, lang, geos),
        f"{start.isoformat()} to {end.isoformat()} ({forecast_days} days) · "
        f"max CPC {max_cpc:,.2f} · daily budget {budget_micros / 1_000_000:,.2f}",
        "",
        f"  Impressions   {format_int(impressions)}",
        f"  Clicks        {format_int(clicks)}",
        f"  CTR           {ctr * 100:.2f}%" if ctr is not None else "  CTR           —",
        f"  Avg CPC       {format_money(m.get('averageCpcMicros'))}",
        f"  Total cost    {format_money(m.get('costMicros'))}",
    ]
    if conversions is not None:
        lines.append(f"  Conversions   {float(conversions):,.1f}")
    if conv_rate is not None:
        lines.append(f"  Conv. rate    {conv_rate * 100:.2f}%")
    if m.get("averageCpaMicros"):
        lines.append(f"  Avg CPA       {format_money(m.get('averageCpaMicros'))}")

    lines.append("")
    lines.append(
        "Costs are in the account's currency. Conversion figures assume the "
        "account's existing conversion rates and are the softest number here."
    )
    return "\n".join(lines)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
