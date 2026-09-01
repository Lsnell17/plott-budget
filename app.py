import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

APP_TITLE = "PLOTT Budget"
DB_PATH = Path(__file__).with_name("plott_budget.db")

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
.donut::after{content:"";width:82px;height:82px;border-radius:50%;background:var(--background-color,#fff);position:absolute}
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

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = conn()
    c.execute("CREATE TABLE IF NOT EXISTS budgets(category TEXT PRIMARY KEY,group_name TEXT NOT NULL,monthly_budget REAL NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS purchases(id INTEGER PRIMARY KEY AUTOINCREMENT,purchase_date TEXT NOT NULL,description TEXT NOT NULL,amount REAL NOT NULL,category TEXT NOT NULL,notes TEXT DEFAULT '')")
    c.execute("CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value REAL NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS savings_entries(id INTEGER PRIMARY KEY AUTOINCREMENT,entry_date TEXT NOT NULL,amount REAL NOT NULL,note TEXT DEFAULT '')")
    if c.execute("SELECT COUNT(*) FROM budgets").fetchone()[0] == 0:
        c.executemany("INSERT INTO budgets(category,group_name,monthly_budget) VALUES(?,?,?)", DEFAULT_BUDGETS)
    for k, v in {
        "monthly_income": 0.0,
        "first_half_savings_goal": 3000.0,
        "second_half_savings_goal": 3000.0,
        "total_savings_goal": 20000.0,
    }.items():
        c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (k, v))
    c.commit()
    c.close()

def get_setting(key):
    c = conn()
    row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    c.close()
    return float(row["value"]) if row else 0.0

def set_setting(key, value):
    c = conn()
    c.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, float(value)))
    c.commit()
    c.close()

def get_budgets():
    c = conn()
    df = pd.read_sql_query("SELECT category,group_name,monthly_budget FROM budgets ORDER BY group_name,category", c)
    c.close()
    return df

def get_month_purchases(year, month):
    prefix = f"{year:04d}-{month:02d}"
    c = conn()
    df = pd.read_sql_query("SELECT * FROM purchases WHERE purchase_date LIKE ? ORDER BY purchase_date DESC,id DESC", c, params=(prefix + "%",))
    c.close()
    return df

def get_savings_total():
    c = conn()
    total = c.execute("SELECT COALESCE(SUM(amount),0) FROM savings_entries").fetchone()[0]
    c.close()
    return float(total or 0)

init_db()

today = date.today()
year, month = today.year, today.month
budgets = get_budgets()
purchases = get_month_purchases(year, month)
spent_by_category = purchases.groupby("category")["amount"].sum().to_dict() if not purchases.empty else {}
spent_month = float(purchases["amount"].sum()) if not purchases.empty else 0.0
monthly_income = get_setting("monthly_income")
income_left = monthly_income - spent_month

st.markdown('<div class="hero"><div style="font-size:2.2rem;font-weight:900">💵 PLOTT Budget</div><div style="opacity:.68;margin-top:.2rem">Quick purchase entry + two-week spending + savings goals</div></div>', unsafe_allow_html=True)

st.markdown("## This month's plan")
st.markdown(
    f'<div class="summary-grid">'
    f'<div class="summary-card"><div class="summary-label">Monthly income</div><div class="summary-value">${monthly_income:,.2f}</div><div class="summary-sub">Editable anytime</div></div>'
    f'<div class="summary-card"><div class="summary-label">Spent this month</div><div class="summary-value">${spent_month:,.2f}</div><div class="summary-sub">All logged purchases</div></div>'
    f'<div class="summary-card"><div class="summary-label">Income left after spending</div><div class="summary-value">${income_left:,.2f}</div><div class="summary-sub">Before future purchases</div></div>'
    f'</div>', unsafe_allow_html=True
)

with st.expander("✏️ Edit income & two-week savings targets"):
    c1, c2, c3 = st.columns(3)
    with c1:
        new_income = st.number_input("Monthly income", min_value=0.0, value=float(monthly_income), step=100.0, format="%.2f")
    with c2:
        first_goal_input = st.number_input("Days 1–14 savings target", min_value=0.0, value=float(get_setting("first_half_savings_goal")), step=100.0, format="%.2f")
    with c3:
        second_goal_input = st.number_input("Days 15–end savings target", min_value=0.0, value=float(get_setting("second_half_savings_goal")), step=100.0, format="%.2f")
    if st.button("Save monthly plan", use_container_width=True):
        set_setting("monthly_income", new_income)
        set_setting("first_half_savings_goal", first_goal_input)
        set_setting("second_half_savings_goal", second_goal_input)
        st.success("Monthly plan updated.")
        st.rerun()

first_goal = get_setting("first_half_savings_goal")
second_goal = get_setting("second_half_savings_goal")
first_half_income = monthly_income / 2
second_half_income = monthly_income / 2

first_spent = second_spent = 0.0
if not purchases.empty:
    parsed_dates = pd.to_datetime(purchases["purchase_date"], errors="coerce")
    first_spent = float(purchases.loc[parsed_dates.dt.day <= 14, "amount"].sum())
    second_spent = float(purchases.loc[parsed_dates.dt.day >= 15, "amount"].sum())

first_safe = first_half_income - first_goal - first_spent
second_safe = second_half_income - second_goal - second_spent

st.markdown("### Two-week spending & saving")
st.markdown(
    f'<div class="payperiod-wrap">'
    f'<div class="payperiod-card"><div class="pp-title">📆 Days 1–14</div><div class="pp-big">${first_safe:,.2f} safe to spend</div><div class="pp-small">Income allocated: ${first_half_income:,.2f}<br>Savings target: ${first_goal:,.2f}<br>Spent so far: ${first_spent:,.2f}</div></div>'
    f'<div class="payperiod-card"><div class="pp-title">📆 Days 15–end</div><div class="pp-big">${second_safe:,.2f} safe to spend</div><div class="pp-small">Income allocated: ${second_half_income:,.2f}<br>Savings target: ${second_goal:,.2f}<br>Spent so far: ${second_spent:,.2f}</div></div>'
    f'</div>', unsafe_allow_html=True
)

savings_total = get_savings_total()
vault_goal = get_setting("total_savings_goal")
vault_progress = 0 if vault_goal <= 0 else min(max(savings_total / vault_goal, 0), 1)
vault_remaining = max(vault_goal - savings_total, 0)

st.markdown("### Savings Vault")
st.markdown(
    f'<div class="savings-vault"><div class="vault-top"><div><div class="vault-title">🔐 Total saved</div><div class="vault-total">${savings_total:,.2f}</div><div class="vault-sub">{vault_progress*100:.1f}% of your vault target</div></div>'
    f'<div><div class="vault-goal">🎯 Target: ${vault_goal:,.2f}</div><div class="vault-sub">${vault_remaining:,.2f} to go</div></div></div>'
    f'<div class="vault-track"><div class="vault-fill" style="width:{vault_progress*100:.1f}%"></div></div></div>',
    unsafe_allow_html=True
)

v1, v2 = st.columns(2)
with v1:
    with st.expander("🎯 Change Savings Vault target"):
        new_vault_goal = st.number_input("Vault target amount", min_value=0.0, value=float(vault_goal), step=500.0, format="%.2f", key="vault_target_amount")
        if st.button("Update vault target", use_container_width=True):
            set_setting("total_savings_goal", new_vault_goal)
            st.success("Savings Vault target updated.")
            st.rerun()
with v2:
    with st.expander("💰 Add money to Savings Vault"):
        saving_date = st.date_input("Date saved", value=today, key="saving_date")
        saving_amount = st.number_input("Amount saved", min_value=0.0, step=50.0, format="%.2f", key="saving_amount")
        saving_note = st.text_input("Savings note", placeholder="First-half savings", key="saving_note")
        if st.button("Add to Savings Vault", use_container_width=True):
            if saving_amount <= 0:
                st.error("Enter an amount greater than $0.")
            else:
                c = conn()
                c.execute("INSERT INTO savings_entries(entry_date,amount,note) VALUES(?,?,?)", (saving_date.isoformat(), float(saving_amount), saving_note.strip()))
                c.commit()
                c.close()
                st.success("Added to Savings Vault.")
                st.rerun()

left, right = st.columns([0.36, 0.64], gap="large")
with left:
    st.markdown("## Add a purchase")
    with st.form("purchase_form", clear_on_submit=True):
        purchase_date = st.date_input("Date", value=today)
        description = st.text_input("What did you buy?", placeholder="Notebooks")
        amount = st.number_input("Amount", min_value=0.01, step=1.0, format="%.2f")
        category = st.selectbox("Category", budgets["category"].tolist())
        notes = st.text_input("Notes (optional)", placeholder="School supplies")
        save = st.form_submit_button("Save purchase", use_container_width=True)
    if save:
        if not description.strip():
            st.error("Please enter what you bought.")
        else:
            c = conn()
            c.execute("INSERT INTO purchases(purchase_date,description,amount,category,notes) VALUES(?,?,?,?,?)",
                      (purchase_date.isoformat(), description.strip(), float(amount), category, notes.strip()))
            c.commit()
            c.close()
            st.success("Purchase saved.")
            st.rerun()

with right:
    st.markdown("## Category breakdown")
    groups = ["All categories"] + sorted(budgets["group_name"].unique().tolist())
    selected_group = st.selectbox("Show", groups)
    shown = budgets if selected_group == "All categories" else budgets[budgets["group_name"] == selected_group]

    cards = []
    for _, row in shown.iterrows():
        category = row["category"]
        group_name = row["group_name"]
        budget = float(row["monthly_budget"])
        spent = float(spent_by_category.get(category, 0.0))
        remaining = budget - spent
        pct = (100 if spent > 0 else 0) if budget <= 0 else min(max((spent / budget) * 100, 0), 100)
        if remaining < 0 or (budget > 0 and remaining / budget <= 0.20):
            status = "#ef4444"
        elif budget > 0 and remaining / budget <= 0.50:
            status = "#f59e0b"
        else:
            status = "#22c55e"
        emoji = GROUP_EMOJI.get(group_name, "•")
        circle_bg = f"conic-gradient({status} 0 {pct:.2f}%,rgba(128,128,128,.20) {pct:.2f}% 100%)"
        cards.append(
            f'<div class="meter-card"><div class="meter-name">{category}</div><div class="meter-group">{emoji} {group_name}</div>'
            f'<div class="donut" style="background:{circle_bg}"><div class="donut-center"><div class="donut-pct">{pct:.0f}%</div><div class="donut-label">used</div></div></div>'
            f'<div class="meter-left" style="color:{status}">${remaining:,.2f} left</div><div class="meter-sub">${spent:,.2f} spent of ${budget:,.2f}</div></div>'
        )
    st.markdown('<div class="meter-grid">' + ''.join(cards) + '</div>', unsafe_allow_html=True)

st.divider()

with st.expander("⚙️ Edit category budgets"):
    editable = budgets.copy()
    editable["monthly_budget"] = editable["monthly_budget"].astype(float)
    edited = st.data_editor(
        editable, use_container_width=True, hide_index=True, disabled=["category", "group_name"],
        column_config={
            "category": "Category",
            "group_name": "Group",
            "monthly_budget": st.column_config.NumberColumn("Monthly budget", format="$%.2f"),
        }
    )
    if st.button("Save category budgets"):
        c = conn()
        for _, r in edited.iterrows():
            c.execute("UPDATE budgets SET monthly_budget=? WHERE category=?", (float(r["monthly_budget"]), r["category"]))
        c.commit()
        c.close()
        st.success("Category budgets updated.")
        st.rerun()

with st.expander("🧾 Purchase history"):
    if purchases.empty:
        st.info("No purchases logged this month yet.")
    else:
        show_cols = purchases[["id","purchase_date","description","amount","category","notes"]].copy()
        show_cols.columns = ["ID","Date","Purchase","Amount","Category","Notes"]
        st.dataframe(show_cols, use_container_width=True, hide_index=True,
                     column_config={"Amount": st.column_config.NumberColumn(format="$%.2f")})
        delete_id = st.selectbox("Delete purchase", options=show_cols["ID"].tolist(),
                                 format_func=lambda x: f"#{x} — {show_cols.loc[show_cols['ID']==x,'Purchase'].iloc[0]}")
        if st.button("Delete selected purchase"):
            c = conn()
            c.execute("DELETE FROM purchases WHERE id=?", (int(delete_id),))
            c.commit()
            c.close()
            st.success("Purchase deleted.")
            st.rerun()

with st.expander("🏦 Savings Vault history"):
    c = conn()
    savings_df = pd.read_sql_query("SELECT id,entry_date,amount,note FROM savings_entries ORDER BY entry_date DESC,id DESC", c)
    c.close()
    if savings_df.empty:
        st.info("No Savings Vault entries yet.")
    else:
        savings_df.columns = ["ID","Date","Amount","Note"]
        st.dataframe(savings_df, use_container_width=True, hide_index=True,
                     column_config={"Amount": st.column_config.NumberColumn(format="$%.2f")})

st.caption("Important: this version still uses SQLite on Streamlit Community Cloud. Connect Google Sheets next so your data is permanent.")
