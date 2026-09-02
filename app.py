from datetime import date
from uuid import uuid4

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from gspread.exceptions import WorksheetNotFound

APP_TITLE = "PLOTT Budget"

DEFAULT_BUDGETS = [
    ("Mortgage", "Household / Housing", 3500.00),
    ("Solar", "Household / Housing", 300.00),
    ("Water", "Household / Housing", 180.00),
    ("Electricity/Gas", "Household / Housing", 100.00),
    ("Trash", "Household / Housing", 170.00),
    ("WiFi", "Household / Housing", 100.00),
    ("Household Supplies", "Household / Housing", 100.00),
    ("Home Maintenance", "Household / Housing", 200.00),
    ("Ford Payment", "Transportation", 377.00),
    ("Subaru Payment", "Transportation", 640.00),
    ("Car Insurance (Geico)", "Transportation", 175.00),
    ("Car Insurance USAA", "Transportation", 102.71),
    ("Gas", "Transportation", 150.00),
    ("Vehicle Maintenance", "Transportation", 100.00),
    ("Groceries", "Food", 500.00),
    ("DoorDash", "Food", 100.00),
    ("Restaurants/Coffee", "Food", 150.00),
    ("Animal", "Pets", 500.00),
    ("Pet Supplies", "Pets", 100.00),
    ("Routine Vet/Medication", "Pets", 50.00),
    ("Capital One Card #1", "Debt", 200.00),
    ("Capital One Card #2", "Debt", 193.00),
    ("Mercury Card", "Debt", 54.00),
    ("Student Loan Payment", "Debt", 161.00),
    ("USAA Credit Card", "Debt", 50.00),
    ("Wedding Ring (Ideal)", "Debt", 140.00),
    ("Lainey Vet Bill", "Debt", 500.00),
    ("ADT", "Utilities / Subscriptions", 64.99),
    ("Amazon Prime", "Utilities / Subscriptions", 16.23),
    ("Audible", "Utilities / Subscriptions", 14.95),
    ("DoorDash subscription", "Utilities / Subscriptions", 9.99),
    ("Grammarly", "Utilities / Subscriptions", 60.00),
    ("Hulu", "Utilities / Subscriptions", 89.99),
    ("Netflix", "Utilities / Subscriptions", 19.99),
    ("Nintendo", "Utilities / Subscriptions", 3.99),
    ("Open AI", "Utilities / Subscriptions", 40.00),
    ("Paramount", "Utilities / Subscriptions", 13.99),
    ("Kindle Unlimited", "Utilities / Subscriptions", 11.99),
    ("Rocket Money", "Utilities / Subscriptions", 8.00),
    ("Spotify", "Utilities / Subscriptions", 31.98),
    ("AT&T", "Utilities / Subscriptions", 177.99),
    ("Google Fi", "Utilities / Subscriptions", 102.00),
    ("iPhone Upgrade", "Utilities / Subscriptions", 40.79),
    ("Shopping / Personal", "Lifestyle", 700.00),
    ("Entertainment / Activities", "Lifestyle", 150.00),
    ("Travel", "Lifestyle", 0.00),
    ("Gifts", "Lifestyle", 100.00),
    ("Health and Wellness", "Lifestyle", 50.00),
    ("Misc.", "Lifestyle", 100.00),
    ("Household Misc.", "Lifestyle", 150.00),
    ("Savings", "Savings", 4000.00),
]

GROUP_EMOJI = {
    "Household / Housing": "🏠",
    "Transportation": "🚗",
    "Food": "🍕",
    "Pets": "🐾",
    "Debt": "💳",
    "Utilities / Subscriptions": "📱",
    "Lifestyle": "✨",
    "Savings": "💰",
}

HEADERS = {
    "Budgets": ["category", "group_name", "monthly_budget"],
    "Purchases": ["id", "purchase_date", "description", "amount", "category", "notes"],
    "Settings": ["key", "value"],
    "Savings": ["id", "entry_date", "amount", "note"],
}

st.set_page_config(page_title=APP_TITLE, page_icon="💵", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:1.4rem;padding-bottom:3rem;max-width:1500px}
.hero{padding:1.05rem 1.2rem;border:1px solid rgba(128,128,128,.25);border-radius:20px;margin-bottom:1rem}
.summary-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-bottom:1rem}
.summary-card{border:1px solid rgba(128,128,128,.25);border-radius:18px;padding:16px 18px;min-height:118px}
.summary-label{font-size:.88rem;opacity:.7;margin-bottom:7px}
.summary-value{font-size:2rem;font-weight:800;line-height:1.05}
.summary-sub{font-size:.83rem;opacity:.68;margin-top:8px}
.payperiod-wrap{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:8px 0 18px}
.payperiod-card{border:1px solid rgba(128,128,128,.25);border-radius:18px;padding:18px}
.pp-title{font-size:1.05rem;font-weight:800}
.pp-big{font-size:1.8rem;font-weight:800;margin:.35rem 0 .2rem}
.pp-small{font-size:.84rem;opacity:.72;line-height:1.45}
.savings-vault{border:1px solid rgba(128,128,128,.25);border-radius:22px;padding:20px;margin:10px 0 10px;background:linear-gradient(135deg,rgba(90,170,255,.08),rgba(110,255,170,.06))}
.vault-top{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap}
.vault-title{font-size:1.1rem;font-weight:800}
.vault-total{font-size:2.5rem;font-weight:900;margin:.25rem 0}
.vault-goal{font-size:1rem;font-weight:700;opacity:.85}
.vault-sub{font-size:.86rem;opacity:.72}
.vault-track{height:18px;background:rgba(128,128,128,.18);border-radius:999px;overflow:hidden;margin-top:14px}
.vault-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#4ade80,#22c55e,#14b8a6)}
.meter-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
.meter-card{border:1px solid rgba(128,128,128,.25);border-radius:18px;padding:16px;min-width:0;text-align:center}
.meter-name{font-weight:800;font-size:1rem;text-align:left;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.meter-group{text-align:left;opacity:.67;font-size:.8rem;margin-bottom:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.donut{width:118px;height:118px;border-radius:50%;margin:8px auto 12px;display:grid;place-items:center;position:relative}
.donut::after{content:"";width:82px;height:82px;border-radius:50%;background:#0e1117;position:absolute}
.donut-center{position:relative;z-index:2;text-align:center}
.donut-pct{font-weight:900;font-size:1.4rem;line-height:1}
.donut-label{font-size:.72rem;opacity:.7;margin-top:4px}
.meter-left{font-size:1.2rem;font-weight:900}
.meter-sub{font-size:.78rem;opacity:.7;margin-top:4px}
@media (max-width:1000px){.meter-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:760px){
  .summary-grid{grid-template-columns:1fr}
  .payperiod-wrap{grid-template-columns:1fr}
  .meter-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
  .meter-card{padding:12px}
  .donut{width:96px;height:96px}
  .donut::after{width:66px;height:66px}
  .donut-pct{font-size:1.15rem}
}
</style>
""", unsafe_allow_html=True)


# ---------- Google Sheets connection ----------

@st.cache_resource
def get_spreadsheet():
    info = dict(st.secrets["google"])
    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    client = gspread.authorize(creds)
    return client.open_by_key(st.secrets["sheet"]["spreadsheet_id"])


@st.cache_resource
def get_worksheets():
    """Get worksheet objects once instead of repeatedly asking Google for them."""
    book = get_spreadsheet()
    existing = {ws.title: ws for ws in book.worksheets()}

    result = {}
    for title, headers in HEADERS.items():
        if title in existing:
            ws_obj = existing[title]
        else:
            ws_obj = book.add_worksheet(title=title, rows=1000, cols=12)
            ws_obj.append_row(headers, value_input_option="RAW")
        result[title] = ws_obj

    return result


def ws(name):
    return get_worksheets()[name]


@st.cache_data(ttl=30, show_spinner=False)
def read_budgets():
    records = ws("Budgets").get_all_records()
    if not records:
        return pd.DataFrame(columns=HEADERS["Budgets"])
    df = pd.DataFrame(records)
    for col in HEADERS["Budgets"]:
        if col not in df.columns:
            df[col] = ""
    df = df[HEADERS["Budgets"]]
    df["monthly_budget"] = pd.to_numeric(
        df["monthly_budget"], errors="coerce"
    ).fillna(0.0)
    return df.sort_values(["group_name", "category"]).reset_index(drop=True)


@st.cache_data(ttl=30, show_spinner=False)
def read_purchases():
    records = ws("Purchases").get_all_records()
    if not records:
        return pd.DataFrame(columns=HEADERS["Purchases"])
    df = pd.DataFrame(records)
    for col in HEADERS["Purchases"]:
        if col not in df.columns:
            df[col] = ""
    df = df[HEADERS["Purchases"]]
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df


@st.cache_data(ttl=30, show_spinner=False)
def read_settings():
    records = ws("Settings").get_all_records()
    result = {}
    for row in records:
        key = str(row.get("key", "")).strip()
        if not key:
            continue
        try:
            result[key] = float(row.get("value", 0))
        except (TypeError, ValueError):
            result[key] = 0.0
    return result


@st.cache_data(ttl=30, show_spinner=False)
def read_savings():
    records = ws("Savings").get_all_records()
    if not records:
        return pd.DataFrame(columns=HEADERS["Savings"])
    df = pd.DataFrame(records)
    for col in HEADERS["Savings"]:
        if col not in df.columns:
            df[col] = ""
    df = df[HEADERS["Savings"]]
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df


def clear_sheet_cache():
    st.cache_data.clear()


def initialize_sheets():
    sheets = get_worksheets()

    budgets_df = read_budgets()
    if budgets_df.empty:
        sheets["Budgets"].append_rows(
            [[category, group, budget] for category, group, budget in DEFAULT_BUDGETS],
            value_input_option="USER_ENTERED",
        )
        clear_sheet_cache()

    settings = read_settings()
    if "total_savings_goal" not in settings:
        sheets["Settings"].append_row(
            ["total_savings_goal", 20000.0],
            value_input_option="USER_ENTERED",
        )
        clear_sheet_cache()


def get_budgets():
    df = read_budgets()
    if df.empty:
        return pd.DataFrame(DEFAULT_BUDGETS, columns=HEADERS["Budgets"])
    return df


def get_month_purchases(year, month):
    df = read_purchases()
    if df.empty:
        return df

    parsed = pd.to_datetime(df["purchase_date"], errors="coerce")
    mask = (parsed.dt.year == year) & (parsed.dt.month == month)
    df = df.loc[mask].copy()

    if not df.empty:
        df["_sort_date"] = pd.to_datetime(df["purchase_date"], errors="coerce")
        df = (
            df.sort_values(["_sort_date"], ascending=False)
            .drop(columns=["_sort_date"])
            .reset_index(drop=True)
        )
    return df


def month_key(year, month, name):
    return f"{year:04d}-{month:02d}|{name}"


def get_setting(key, default=0.0):
    return float(read_settings().get(key, default))


def set_setting(key, value):
    sheet = ws("Settings")
    settings_rows = sheet.get_all_values()
    for idx, row in enumerate(settings_rows[1:], start=2):
        if row and row[0] == key:
            sheet.update_cell(idx, 2, float(value))
            clear_sheet_cache()
            return
    sheet.append_row([key, float(value)], value_input_option="USER_ENTERED")
    clear_sheet_cache()


def append_purchase(purchase_date, description, amount, category, notes):
    ws("Purchases").append_row(
        [
            str(uuid4()),
            purchase_date.isoformat(),
            description,
            float(amount),
            category,
            notes,
        ],
        value_input_option="USER_ENTERED",
    )
    clear_sheet_cache()


def delete_purchase(purchase_id):
    sheet = ws("Purchases")
    values = sheet.get_all_values()
    for row_num, row in enumerate(values[1:], start=2):
        if row and row[0] == str(purchase_id):
            sheet.delete_rows(row_num)
            clear_sheet_cache()
            return True
    return False


def save_budgets(df):
    sheet = ws("Budgets")
    payload = [HEADERS["Budgets"]]
    for _, row in df.iterrows():
        payload.append(
            [
                str(row["category"]),
                str(row["group_name"]),
                float(row["monthly_budget"]),
            ]
        )
    sheet.clear()
    sheet.update("A1", payload)
    clear_sheet_cache()


def get_savings_df():
    return read_savings()


def get_savings_total():
    df = read_savings()
    return float(df["amount"].sum()) if not df.empty else 0.0


def append_savings(entry_date, amount, note):
    ws("Savings").append_row(
        [str(uuid4()), entry_date.isoformat(), float(amount), note],
        value_input_option="USER_ENTERED",
    )
    clear_sheet_cache()


def delete_savings(savings_id):
    sheet = ws("Savings")
    values = sheet.get_all_values()
    for row_num, row in enumerate(values[1:], start=2):
        if row and row[0] == str(savings_id):
            sheet.delete_rows(row_num)
            clear_sheet_cache()
            return True
    return False


try:
    initialize_sheets()
except Exception as exc:
    st.error("PLOTT Budget could not connect to Google Sheets.")
    st.code(str(exc))

    if "429" in str(exc) or "Quota exceeded" in str(exc):
        st.warning(
            "Google Sheets temporarily rate-limited the app. "
            "Wait about 60 seconds, then refresh once."
        )
    else:
        st.info(
            "Check that the Streamlit Secrets are saved correctly and that the "
            "Google Sheet is shared with the service-account email as an Editor."
        )
    st.stop()


# ---------- Current month data ----------

today = date.today()
year, month = today.year, today.month

income_key = month_key(year, month, "monthly_income")
first_goal_key = month_key(year, month, "first_half_savings_goal")
second_goal_key = month_key(year, month, "second_half_savings_goal")
first_spend_key = month_key(year, month, "first_half_spending_allowance")
second_spend_key = month_key(year, month, "second_half_spending_allowance")

budgets = get_budgets()
purchases = get_month_purchases(year, month)

spent_by_category = (
    purchases.groupby("category")["amount"].sum().to_dict()
    if not purchases.empty else {}
)
spent_month = float(purchases["amount"].sum()) if not purchases.empty else 0.0

monthly_income = get_setting(income_key, 0.0)
first_goal = get_setting(first_goal_key, 3000.0)
second_goal = get_setting(second_goal_key, 3000.0)

# Default spending allowances are based on income minus savings, but once edited
# they are saved independently for that month.
default_first_allowance = max((monthly_income / 2) - first_goal, 0.0)
default_second_allowance = max((monthly_income / 2) - second_goal, 0.0)
first_spending_allowance = get_setting(first_spend_key, default_first_allowance)
second_spending_allowance = get_setting(second_spend_key, default_second_allowance)

income_left = monthly_income - spent_month


# ---------- Dashboard ----------

st.markdown(
    '<div class="hero">'
    '<div style="font-size:2.2rem;font-weight:900">💵 PLOTT Budget</div>'
    '<div style="opacity:.68;margin-top:.2rem">'
    'Google Sheets synced • two-week spending • savings goals'
    '</div></div>',
    unsafe_allow_html=True,
)

st.success("☁️ Google Sheets connected — changes are saved to your spreadsheet.")

st.markdown("## This month's plan")
st.markdown(
    f'<div class="summary-grid">'
    f'<div class="summary-card"><div class="summary-label">Monthly income</div>'
    f'<div class="summary-value">${monthly_income:,.2f}</div>'
    f'<div class="summary-sub">Saved for {today.strftime("%B %Y")}</div></div>'
    f'<div class="summary-card"><div class="summary-label">Spent this month</div>'
    f'<div class="summary-value">${spent_month:,.2f}</div>'
    f'<div class="summary-sub">All logged purchases</div></div>'
    f'<div class="summary-card"><div class="summary-label">Income left after spending</div>'
    f'<div class="summary-value">${income_left:,.2f}</div>'
    f'<div class="summary-sub">Before future purchases</div></div>'
    f'</div>',
    unsafe_allow_html=True,
)

with st.expander("✏️ Edit monthly plan & two-week spending allowances"):
    st.caption(
        "Changing a spending allowance does not change or erase any purchases. "
        "It only changes how much you want available to spend in that time period."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        new_income = st.number_input(
            "Monthly income",
            min_value=0.0,
            value=float(monthly_income),
            step=100.0,
            format="%.2f",
        )
    with c2:
        first_goal_input = st.number_input(
            "Days 1–14 savings target",
            min_value=0.0,
            value=float(first_goal),
            step=100.0,
            format="%.2f",
        )
    with c3:
        second_goal_input = st.number_input(
            "Days 15–end savings target",
            min_value=0.0,
            value=float(second_goal),
            step=100.0,
            format="%.2f",
        )

    s1, s2 = st.columns(2)
    with s1:
        first_spending_input = st.number_input(
            "Days 1–14 amount available to spend",
            min_value=0.0,
            value=float(first_spending_allowance),
            step=100.0,
            format="%.2f",
            help="This is your spending allowance for Days 1–14. Your purchases stay unchanged.",
        )
    with s2:
        second_spending_input = st.number_input(
            "Days 15–end amount available to spend",
            min_value=0.0,
            value=float(second_spending_allowance),
            step=100.0,
            format="%.2f",
            help="This is your spending allowance for Days 15–end. Your purchases stay unchanged.",
        )

    if st.button("Save monthly plan", use_container_width=True):
        set_setting(income_key, new_income)
        set_setting(first_goal_key, first_goal_input)
        set_setting(second_goal_key, second_goal_input)
        set_setting(first_spend_key, first_spending_input)
        set_setting(second_spend_key, second_spending_input)
        st.success("Monthly plan and spending allowances saved to Google Sheets.")
        st.rerun()


# ---------- Two-week spending ----------

first_half_income = monthly_income / 2
second_half_income = monthly_income / 2

first_spent = 0.0
second_spent = 0.0

if not purchases.empty:
    parsed_dates = pd.to_datetime(purchases["purchase_date"], errors="coerce")
    first_spent = float(purchases.loc[parsed_dates.dt.day <= 14, "amount"].sum())
    second_spent = float(purchases.loc[parsed_dates.dt.day >= 15, "amount"].sum())

# Editable allowance minus actual purchases = amount still safe to spend.
# Existing purchase rows are never changed by editing the allowance.
first_safe = first_spending_allowance - first_spent
second_safe = second_spending_allowance - second_spent


def money(value):
    return f"-${abs(value):,.2f}" if value < 0 else f"${value:,.2f}"


st.markdown("### Two-week spending & saving")
st.markdown(
    f'<div class="payperiod-wrap">'
    f'<div class="payperiod-card"><div class="pp-title">📆 Days 1–14</div>'
    f'<div class="pp-big">{money(first_safe)} safe to spend</div>'
    f'<div class="pp-small">Spending allowance: ${first_spending_allowance:,.2f}<br>'
    f'Savings target: ${first_goal:,.2f}<br>Spent so far: ${first_spent:,.2f}</div></div>'
    f'<div class="payperiod-card"><div class="pp-title">📆 Days 15–end</div>'
    f'<div class="pp-big">{money(second_safe)} safe to spend</div>'
    f'<div class="pp-small">Spending allowance: ${second_spending_allowance:,.2f}<br>'
    f'Savings target: ${second_goal:,.2f}<br>Spent so far: ${second_spent:,.2f}</div></div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ---------- Savings Vault ----------

savings_total = get_savings_total()
vault_goal = get_setting("total_savings_goal", 20000.0)
vault_progress = 0 if vault_goal <= 0 else min(max(savings_total / vault_goal, 0), 1)
vault_remaining = max(vault_goal - savings_total, 0)

st.markdown("### Savings Vault")
st.markdown(
    f'<div class="savings-vault"><div class="vault-top"><div>'
    f'<div class="vault-title">🔐 Total saved</div>'
    f'<div class="vault-total">${savings_total:,.2f}</div>'
    f'<div class="vault-sub">{vault_progress*100:.1f}% of your vault target</div></div>'
    f'<div><div class="vault-goal">🎯 Target: ${vault_goal:,.2f}</div>'
    f'<div class="vault-sub">${vault_remaining:,.2f} to go</div></div></div>'
    f'<div class="vault-track"><div class="vault-fill" '
    f'style="width:{vault_progress*100:.1f}%"></div></div></div>',
    unsafe_allow_html=True,
)

v1, v2 = st.columns(2)

with v1:
    with st.expander("🎯 Change Savings Vault target"):
        new_vault_goal = st.number_input(
            "Vault target amount",
            min_value=0.0,
            value=float(vault_goal),
            step=500.0,
            format="%.2f",
            key="vault_target_amount",
        )
        if st.button("Update vault target", use_container_width=True):
            set_setting("total_savings_goal", new_vault_goal)
            st.success("Savings Vault target saved to Google Sheets.")
            st.rerun()

with v2:
    with st.expander("💰 Add money to Savings Vault"):
        saving_date = st.date_input("Date saved", value=today, key="saving_date")
        saving_amount = st.number_input(
            "Amount saved",
            min_value=0.0,
            step=50.0,
            format="%.2f",
            key="saving_amount",
        )
        saving_note = st.text_input(
            "Savings note",
            placeholder="First-half savings",
            key="saving_note",
        )
        if st.button("Add to Savings Vault", use_container_width=True):
            if saving_amount <= 0:
                st.error("Enter an amount greater than $0.")
            else:
                append_savings(saving_date, saving_amount, saving_note.strip())
                st.success("Savings entry saved to Google Sheets.")
                st.rerun()


# ---------- Purchases and category meters ----------

left, right = st.columns([0.36, 0.64], gap="large")

with left:
    st.markdown("## Add a purchase")
    with st.form("purchase_form", clear_on_submit=True):
        purchase_date = st.date_input("Date", value=today)
        description = st.text_input("What did you buy?", placeholder="Notebooks")
        amount = st.number_input(
            "Amount",
            min_value=0.01,
            step=1.0,
            format="%.2f",
        )
        category = st.selectbox("Category", budgets["category"].tolist())
        notes = st.text_input("Notes (optional)", placeholder="School supplies")
        save = st.form_submit_button("Save purchase", use_container_width=True)

    if save:
        if not description.strip():
            st.error("Please enter what you bought.")
        else:
            append_purchase(
                purchase_date,
                description.strip(),
                amount,
                category,
                notes.strip(),
            )
            st.success("Purchase saved to Google Sheets.")
            st.rerun()

with right:
    st.markdown("## Category breakdown")
    groups = ["All categories"] + sorted(budgets["group_name"].unique().tolist())
    selected_group = st.selectbox("Show", groups)

    shown = (
        budgets
        if selected_group == "All categories"
        else budgets[budgets["group_name"] == selected_group]
    )

    cards = []
    for _, row in shown.iterrows():
        category_name = row["category"]
        group_name = row["group_name"]
        budget = float(row["monthly_budget"])
        spent = float(spent_by_category.get(category_name, 0.0))
        remaining = budget - spent

        if budget <= 0:
            pct = 100 if spent > 0 else 0
        else:
            pct = min(max((spent / budget) * 100, 0), 100)

        if remaining < 0 or (budget > 0 and remaining / budget <= 0.20):
            status = "#ef4444"
        elif budget > 0 and remaining / budget <= 0.50:
            status = "#f59e0b"
        else:
            status = "#22c55e"

        emoji = GROUP_EMOJI.get(group_name, "•")
        circle_bg = (
            f"conic-gradient({status} 0 {pct:.2f}%,"
            f"rgba(128,128,128,.20) {pct:.2f}% 100%)"
        )

        cards.append(
            f'<div class="meter-card">'
            f'<div class="meter-name">{category_name}</div>'
            f'<div class="meter-group">{emoji} {group_name}</div>'
            f'<div class="donut" style="background:{circle_bg}">'
            f'<div class="donut-center"><div class="donut-pct">{pct:.0f}%</div>'
            f'<div class="donut-label">used</div></div></div>'
            f'<div class="meter-left" style="color:{status}">${remaining:,.2f} left</div>'
            f'<div class="meter-sub">${spent:,.2f} spent of ${budget:,.2f}</div>'
            f'</div>'
        )

    st.markdown(
        '<div class="meter-grid">' + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )

st.divider()


# ---------- Editable category budgets ----------

with st.expander("⚙️ Edit category budgets"):
    editable = budgets.copy()
    editable["monthly_budget"] = editable["monthly_budget"].astype(float)

    edited = st.data_editor(
        editable,
        use_container_width=True,
        hide_index=True,
        disabled=["category", "group_name"],
        column_config={
            "category": "Category",
            "group_name": "Group",
            "monthly_budget": st.column_config.NumberColumn(
                "Monthly budget",
                format="$%.2f",
            ),
        },
    )

    if st.button("Save category budgets"):
        save_budgets(edited)
        st.success("Category budgets saved to Google Sheets.")
        st.rerun()


# ---------- Purchase history ----------

with st.expander("🧾 Purchase history"):
    if purchases.empty:
        st.info("No purchases logged this month yet.")
    else:
        show_cols = purchases[
            ["id", "purchase_date", "description", "amount", "category", "notes"]
        ].copy()
        show_cols.columns = ["ID", "Date", "Purchase", "Amount", "Category", "Notes"]

        st.dataframe(
            show_cols,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount": st.column_config.NumberColumn(format="$%.2f")
            },
        )

        delete_id = st.selectbox(
            "Delete purchase",
            options=show_cols["ID"].tolist(),
            format_func=lambda x: (
                f"{show_cols.loc[show_cols['ID'] == x, 'Purchase'].iloc[0]} "
                f"— ${float(show_cols.loc[show_cols['ID'] == x, 'Amount'].iloc[0]):,.2f}"
            ),
        )

        if st.button("Delete selected purchase"):
            if delete_purchase(delete_id):
                st.success("Purchase deleted from Google Sheets.")
                st.rerun()
            else:
                st.error("That purchase could not be found.")


# ---------- Savings history ----------

with st.expander("🏦 Savings Vault history"):
    savings_df = get_savings_df()

    if savings_df.empty:
        st.info("No Savings Vault entries yet.")
    else:
        show_savings = savings_df[["id", "entry_date", "amount", "note"]].copy()
        show_savings.columns = ["ID", "Date", "Amount", "Note"]

        st.dataframe(
            show_savings,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount": st.column_config.NumberColumn(format="$%.2f")
            },
        )

        savings_delete_id = st.selectbox(
            "Delete savings entry",
            options=show_savings["ID"].tolist(),
            format_func=lambda x: (
                f"{show_savings.loc[show_savings['ID'] == x, 'Date'].iloc[0]} "
                f"— ${float(show_savings.loc[show_savings['ID'] == x, 'Amount'].iloc[0]):,.2f}"
            ),
        )

        if st.button("Delete selected savings entry"):
            if delete_savings(savings_delete_id):
                st.success("Savings entry deleted from Google Sheets.")
                st.rerun()
            else:
                st.error("That savings entry could not be found.")

st.caption(
    "☁️ PLOTT Budget is using Google Sheets as its permanent shared database."
)
