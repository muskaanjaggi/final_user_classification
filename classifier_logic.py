"""
classifier_logic.py
====================
Core user-segmentation logic for CoverSure.

This module contains the business rules originally encoded as Excel
formulas in Power_User_Categorized_v3.xlsx, exposed as:

  - classify_user(...)      -> classify a single user profile
  - classify_dataframe(df)  -> batch-classify a pandas DataFrame
  - CATEGORY_INFO            -> display metadata (color/icon/description)
                                 for each category, used by the UI
"""

from datetime import date, datetime
import pandas as pd


# ─── Category Metadata (for UI display) ──────────────────────────────────────

CATEGORY_INFO = {
    "Power User": {
        "color": "#22c55e",
        "icon": "🚀",
        "description": "High-value, highly engaged, long-tenured user. "
                        "Top priority for retention and upsell.",
    },
    "Active User": {
        "color": "#3b82f6",
        "icon": "✅",
        "description": "High-value user with healthy activity, but not yet "
                        "showing enough signals to be a Power User.",
    },
    "Normal User": {
        "color": "#06b6d4",
        "icon": "🙂",
        "description": "Newer account already showing engagement signals. "
                        "Good candidate for nurture campaigns.",
    },
    "Dormant User": {
        "color": "#eab308",
        "icon": "💤",
        "description": "Installed but low value and low engagement. "
                        "Candidate for re-activation campaigns.",
    },
    "Repitch User": {
        "color": "#f97316",
        "icon": "🔁",
        "description": "Uninstalled, but retains policy/premium history and "
                        "engagement signals. Strong win-back target.",
    },
    "Lapsed User": {
        "color": "#ef4444",
        "icon": "📉",
        "description": "Uninstalled with prior policy/premium value but no "
                        "engagement signals. Lower win-back priority.",
    },
    "Inactive User": {
        "color": "#6b7280",
        "icon": "🚫",
        "description": "Uninstalled and never built up any policy/premium "
                        "value. Lowest priority segment.",
    },
}


# ─── Core Classification ──────────────────────────────────────────────────────

def classify_user(
    uninstalled: bool,
    active_policies: float,
    annual_premium: float,
    bbps_transactions: float,
    phc_transactions: float,
    lead: bool,
    cpro: bool,
    ioc: bool,
    has_partner: bool,
    signup_date,
    today: date = None,
) -> str:
    """
    Classify a single user profile into one of seven categories.

    Decision tree:
    1. Uninstalled?
       YES -> Has policies or premium?
               YES -> Has any activity / transactions? -> Repitch User
                                                        -> Lapsed User
               NO  -> Inactive User
       NO  -> High value (policies>3 OR premium>100k)?
              YES -> Mature account (>90 days) AND 2+ engagement signals?
                       -> Power User
                       -> Active User
              NO  -> Recent signup (<=90 days) AND has any activity?
                       -> Normal User
                       -> Dormant User
    """
    if today is None:
        today = date.today()

    active_policies = active_policies or 0
    annual_premium = annual_premium or 0
    bbps_transactions = bbps_transactions or 0
    phc_transactions = phc_transactions or 0

    has_activity = bool(lead or cpro or ioc)
    has_transactions = bbps_transactions > 0 or phc_transactions > 0

    days_since_signup = _days_since(signup_date, today)

    # ── Branch: Uninstalled ───────────────────────────────────────────────
    if uninstalled:
        if active_policies > 0 or annual_premium > 0:
            if has_activity or has_transactions:
                return "Repitch User"
            return "Lapsed User"
        return "Inactive User"

    # ── Branch: Installed ─────────────────────────────────────────────────
    if active_policies > 3 or annual_premium > 100_000:
        engagement_count = int(bool(has_partner)) + int(has_activity) + int(has_transactions)
        if days_since_signup > 90 and engagement_count >= 2:
            return "Power User"
        return "Active User"

    if days_since_signup <= 90 and (has_activity or has_transactions):
        return "Normal User"
    return "Dormant User"


# ─── Batch Classification ──────────────────────────────────────────────────────

REQUIRED_COLUMNS = [
    "uninstalled", "active_policies", "annual_premium",
    "bbps_transactions", "phc_transactions",
    "lead", "cpro", "ioc", "partner_code", "signup",
]


def classify_dataframe(df: pd.DataFrame, today: date = None) -> pd.DataFrame:
    """
    Batch-classify a DataFrame using the original spreadsheet column schema:

      uninstalled        : 'uninstalled' or 'na'
      active_policies    : number (may be blank)
      annual_premium     : number (may be blank)
      bbps_transactions  : number (may be blank)
      phc_transactions   : number (may be blank)
      lead               : 'lead' or 'na'
      cpro               : 'did cpro' or 'na'
      ioc                : 'used ioc' or 'na'
      partner_code       : text (may be blank)
      signup             : date (may be blank)

    Returns a copy of df with a new 'user_category' column appended.
    """
    if today is None:
        today = date.today()

    def _row(row):
        return classify_user(
            uninstalled=str(row.get("uninstalled", "na")).strip().lower() == "uninstalled",
            active_policies=_to_float(row.get("active_policies")),
            annual_premium=_to_float(row.get("annual_premium")),
            bbps_transactions=_to_float(row.get("bbps_transactions")),
            phc_transactions=_to_float(row.get("phc_transactions")),
            lead=str(row.get("lead", "na")).strip().lower() == "lead",
            cpro=str(row.get("cpro", "na")).strip().lower() == "did cpro",
            ioc=str(row.get("ioc", "na")).strip().lower() == "used ioc",
            has_partner=_has_partner(row.get("partner_code")),
            signup_date=_parse_date(row.get("signup")),
            today=today,
        )

    out = df.copy()
    out["user_category"] = out.apply(_row, axis=1)
    return out


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _to_float(value) -> float:
    try:
        v = float(value)
        return v if v == v else 0.0   # filter NaN
    except (TypeError, ValueError):
        return 0.0


def _has_partner(value) -> bool:
    if value is None:
        return False
    s = str(value).strip()
    return s not in ("", "nan", "NaN", "None")


def _parse_date(value):
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.date() if isinstance(value, datetime) else value
    try:
        ts = pd.to_datetime(value)
        if pd.isna(ts):
            return None
        return ts.date()
    except Exception:
        return None


def _days_since(signup_date, today: date) -> int:
    if signup_date is None or (isinstance(signup_date, float) and signup_date != signup_date):
        return 9999  # unknown -> treat as old account
    if isinstance(signup_date, datetime):
        signup_date = signup_date.date()
    try:
        return (today - signup_date).days
    except Exception:
        return 9999
