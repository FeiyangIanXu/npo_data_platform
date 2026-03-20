from __future__ import annotations

from typing import Any


CANONICAL_COLUMNS = [
    "source",
    "ein",
    "organization_name",
    "tax_year",
    "filing_date",
    "tax_prd",
    "form_type",
    "total_revenue",
    "total_expenses",
    "total_assets",
    "net_assets",
    "employee_count",
    "is_latest_filing_for_ein",
    "raw_available",
]


def clean_number(value: Any) -> int | float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip().replace(",", "").replace("$", "")
    if text == "":
        return None
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return None


def normalize_year(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        year = int(str(value)[:4])
    except ValueError:
        return None
    return year if 1900 <= year <= 2100 else None


def extract_filings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    filings = payload.get("filings_with_data", [])
    return filings if isinstance(filings, list) else []


def infer_organization_name(payload: dict[str, Any], filing: dict[str, Any]) -> str:
    organization = payload.get("organization", {})
    if isinstance(organization, dict):
        value = organization.get("name")
        if value:
            return str(value)
    for key in ("name", "organization_name", "organization", "org_name"):
        value = payload.get(key)
        if value:
            return str(value)
    for key in ("organization_name", "name"):
        value = filing.get(key)
        if value:
            return str(value)
    return ""


def infer_form_type(filing: dict[str, Any]) -> str:
    for key in ("formtype", "form_type", "form"):
        value = filing.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def infer_filing_date(filing: dict[str, Any]) -> str:
    for key in ("filing_date", "date", "received_date", "updated"):
        value = filing.get(key)
        if value:
            return str(value)
    return ""


def map_filing_to_canonical(
    ein: str,
    payload: dict[str, Any],
    filing: dict[str, Any],
    latest_tax_year: int | None,
) -> dict[str, Any]:
    tax_year = normalize_year(filing.get("tax_prd_yr"))
    if tax_year is None:
        tax_year = normalize_year(filing.get("tax_year"))
    if tax_year is None:
        tax_year = normalize_year(filing.get("tax_prd"))
    return {
        "source": "propublica",
        "ein": ein,
        "organization_name": infer_organization_name(payload, filing),
        "tax_year": tax_year,
        "filing_date": infer_filing_date(filing),
        "tax_prd": str(filing.get("tax_prd", "") or ""),
        "form_type": infer_form_type(filing),
        "total_revenue": clean_number(filing.get("totrevenue", filing.get("total_revenue"))),
        "total_expenses": clean_number(filing.get("totfuncexpns", filing.get("total_expenses"))),
        "total_assets": clean_number(filing.get("totassetsend", filing.get("total_assets"))),
        "net_assets": clean_number(filing.get("totnetassetend", filing.get("net_assets"))),
        "employee_count": clean_number(filing.get("noemployees", filing.get("employee_count"))),
        "is_latest_filing_for_ein": bool(latest_tax_year is not None and tax_year == latest_tax_year),
        "raw_available": True,
    }


def payload_to_canonical_rows(ein: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    filings = extract_filings(payload)
    tax_years = []
    for filing in filings:
        year = normalize_year(filing.get("tax_prd_yr"))
        if year is None:
            year = normalize_year(filing.get("tax_year"))
        if year is None:
            year = normalize_year(filing.get("tax_prd"))
        tax_years.append(year)
    available_years = [year for year in tax_years if year is not None]
    latest_tax_year = max(available_years) if available_years else None

    rows = [map_filing_to_canonical(ein, payload, filing, latest_tax_year) for filing in filings]
    if rows:
        return rows
    return [
        {
            "source": "propublica",
            "ein": ein,
            "organization_name": infer_organization_name(payload, {}),
            "tax_year": None,
            "filing_date": "",
            "tax_prd": "",
            "form_type": "",
            "total_revenue": None,
            "total_expenses": None,
            "total_assets": None,
            "net_assets": None,
            "employee_count": None,
            "is_latest_filing_for_ein": False,
            "raw_available": False,
        }
    ]


def summarize_payload(ein: str, payload: dict[str, Any]) -> dict[str, Any]:
    filings = extract_filings(payload)
    years = sorted(
        {
            year
            for year in (
                normalize_year(filing.get("tax_prd_yr"))
                or normalize_year(filing.get("tax_year"))
                or normalize_year(filing.get("tax_prd"))
                for filing in filings
            )
            if year is not None
        },
        reverse=True,
    )
    latest_filing = None
    if years:
        latest_year = years[0]
        for filing in filings:
            year = (
                normalize_year(filing.get("tax_prd_yr"))
                or normalize_year(filing.get("tax_year"))
                or normalize_year(filing.get("tax_prd"))
            )
            if year == latest_year:
                latest_filing = filing
                break
    else:
        latest_year = None

    return {
        "ein": ein,
        "filing_count": len(filings),
        "latest_tax_year": latest_year,
        "latest_form_type": infer_form_type(latest_filing or {}),
        "has_2024_plus": any(year >= 2024 for year in years),
        "has_2025_plus": any(year >= 2025 for year in years),
    }
