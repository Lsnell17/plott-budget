import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).with_name("plott_budget.db")

# Based on the user's Sept 26 budget sheet.
# Categories that were marked VOID or had non-numeric budgets are omitted from spendable tracking.
DEFAULT_BUDGETS = {
    "Mortgage": 3500.00,
    "Solar": 300.00,
    "Water": 180.00,
    "Electricity/Gas": 100.00,
    "Trash": 170.00,
    "WiFi": 100.00,
    "Household Supplies": 100.00,
    "Home Maintenance": 200.00,
    "Ford Payment": 377.00,
    "Subaru Payment": 640.00,
    "Car Insurance (Geico)": 175.00,
    "Car Insurance USAA": 102.71,
    "Gas": 150.00,
    "Vehicle Maintenance": 100.00,
    "Groceries": 500.00,
    "DoorDash": 100.00,
    "Restaurants/Coffee": 150.00,
    "Animal": 500.00,
    "Pet Supplies": 100.00,
    "Routine Vet/Medication": 50.00,
    "Capital One Card #1": 200.00,
    "Capital One Card #2": 193.00,
    "Mercury Card": 54.00,
    "Student Loan Payment": 161.00,
    "USAA Credit Card": 50.00,
    "Wedding Ring (Ideal)": 140.00,
    "Lainey Vet Bill": 500.00,
    "ADT": 64.99,
    "Amazon Prime": 16.23,
    "Audible": 14.95,
    "DoorDash Subscription": 9.99,
    "Grammarly": 60.00,
    "Hulu": 89.99,
    "Netflix": 19.99,
    "Nintendo": 3.99,
    "Open AI": 40.00,
    "Paramount": 13.99,
    "Kindle Unlimited": 11.99,
    "Rocket Money": 8.00,
    "Spotify": 31.98,
    "AT&T": 177.99,
    "Google Fi": 102.00,
    "iPhone Upgrade": 40.79,
    "Shopping / Personal": 700.00,
    "Entertainment / Activities": 150.00,
    "Travel": 0.00,
    "Gifts": 100.00,
    "Health and Wellness": 50.00,
    "Misc.": 100.00,
    "Household Misc.": 150.00,
    "Savings": 4000.00,
}

CATEGORY_GROUPS = {
    "Mortgage": "🏠 Household / Housing", "Solar": "🏠 Household / Housing", "Water": "🏠 Household / Housing",
    "Electricity/Gas": "🏠 Household / Housing", "Trash": "🏠 Household / Housing", "WiFi": "🏠 Household / Housing",
    "Household Supplies": "🏠 Household / Housing", "Home Maintenance": "🏠 Household / Housing",
    "Ford Payment": "🚙 Transportation", "Subaru Payment": "🚙 Transportation", "Car Insurance (Geico)": "🚙 Transportation",
    "Car Insurance USAA": "🚙 Transportation", "Gas": "🚙 Transportation", "Vehicle Maintenance": "🚙 Transportation",
    "Groceries": "🍕 Food", "DoorDash": "🍕 Food", "Restaurants/Coffee": "🍕 Food",
    "Animal": "🐾 Pets", "Pet Supplies": "🐾 Pets", "Routine Vet/Medication": "🐾 Pets",
    "Capital One Card #1": "💳 Debt Payments", "Capital One Card #2": "💳 Debt Payments", "Mercury Card": "💳 Debt Payments",
    "Student Loan Payment": "💳 Debt Payments", "USAA Credit Card": "💳 Debt Payments", "Wedding Ring (Ideal)": "💳 Debt Payments",
    "Lainey Vet Bill": "💊 Lainey Vet Bill",
    "ADT": "💰 Utilities / Subscriptions", "Amazon Prime": "💰 Utilities / Subscriptions", "Audible": "💰 Utilities / Subscriptions",
    "DoorDash Subscription": "💰 Utilities / Subscriptions", "Grammarly": "💰 Utilities / Subscriptions", "Hulu": "💰 Utilities / Subscriptions",
    "Netflix": "💰 Utilities / Subscriptions", "Nintendo": "💰 Utilities / Subscriptions", "Open AI": "💰 Utilities / Subscriptions",
    "Paramount": "💰 Utilities / Subscriptions", "Kindle Unlimited": "💰 Utilities / Subscriptions", "Rocket Money": "💰 Utilities / Subscriptions",
    "Spotify": "💰 Utilities / Subscriptions", "AT&T": "💰 Utilities / Subscriptions", "Google Fi": "💰 Utilities / Subscriptions",
    "iPhone Upgrade": "💰 Utilities / Subscriptions",
    "Shopping / Personal": "👜 Lifestyle / Personal", "Entertainment / Activities": "👜 Lifestyle / Personal", "Travel": "👜 Lifestyle / Personal",
    "Gifts": "👜 Lifestyle / Personal", "Health and Wellness": "👜 Lifestyle / Personal", "Misc.": "👜 Lifestyle / Personal",
    "Household Misc.": "👜 Lifestyle / Personal", "Savings": "💰 Savings",
}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                group_name TEXT NOT NULL,
                monthly_budget REAL NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM budgets").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO budgets(category, group_name, monthly_budget) VALUES (?, ?, ?)",
                [(cat, CATEGORY_GROUPS.get(cat, "Other"), amt) for cat, amt in DEFAULT_BUDGETS.items()]
            )


def get_budgets():
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM budgets ORDER BY group_name, category", conn)


def get_purchases():
    with get_conn() as conn:
        return pd.read_sql_query(
            "SELECT id, purchase_date, description, amount, category, notes FROM purchases ORDER BY purchase_date DESC, id DESC",
            conn,
        )


def add_purchase(purchase_date, description, amount, category, notes):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO purchases(purchase_date, description, amount, category, notes) VALUES (?, ?, ?, ?, ?)",
            (purchase_date.isoformat(), description.strip(), float(amount), category, notes.strip()),
        )


def delete_purchase(purchase_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM purchases WHERE id = ?", (int(purchase_id),))


def update_budget(category, amount):
    with get_conn() as conn:
        conn.execute("UPDATE budgets SET monthly_budget = ? WHERE category = ?", (float(amount), category))


def status_color(remaining_pct, remaining):
    if remaining < 0 or remaining_pct <= 0.20:
        return "#dc2626"  # red
    if remaining_pct <= 0.50:
        return "#f59e0b"  # orange
    return "#16a34a"      # green


st.set_page_config(page_title="PLOTT Budget", page_icon="💵", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px;}
.budget-card {background: white; border: 1px solid #e5e7eb; border-radius: 14px; padding: 15px 17px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,.04);}
.budget-name {font-size: .95rem; font-weight: 650; color: #111827;}
.budget-sub {font-size: .82rem; color: #6b7280; margin-top: 2px;}
.budget-number {font-size: 1.4rem; font-weight: 800; margin-top: 7px;}
.small-label {font-size: .75rem; color: #6b7280; text-transform: uppercase; letter-spacing: .05em;}
</style>
""", unsafe_allow_html=True)

init_db()
budgets = get_budgets()
purchases = get_purchases()

st.title("💵 PLOTT Budget")
st.caption("Quick purchase entry + live monthly category balances")

left, right = st.columns([1, 1.8], gap="large")

with left:
    st.subheader("Add a purchase")
    with st.form("purchase_form", clear_on_submit=True):
        purchase_date = st.date_input("Date", value=date.today())
        description = st.text_input("What did you buy?", placeholder="Notebooks")
        amount = st.number_input("Amount", min_value=0.01, step=1.00, format="%.2f")
        category = st.selectbox("Category", budgets["category"].tolist())
        notes = st.text_input("Notes (optional)", placeholder="School supplies")
        submitted = st.form_submit_button("Save purchase", use_container_width=True, type="primary")
        if submitted:
            if not description.strip():
                st.error("Please enter what you bought.")
            else:
                add_purchase(purchase_date, description, amount, category, notes)
                st.success(f"Saved {description} — ${amount:,.2f} to {category}.")
                st.rerun()

    st.divider()
    st.subheader("Budget settings")
    with st.expander("Change a monthly category budget"):
        edit_category = st.selectbox("Category to change", budgets["category"].tolist(), key="edit_cat")
        current = float(budgets.loc[budgets["category"] == edit_category, "monthly_budget"].iloc[0])
        new_budget = st.number_input("Monthly budget", min_value=0.0, value=current, step=10.0, format="%.2f")
        if st.button("Update budget", use_container_width=True):
            update_budget(edit_category, new_budget)
            st.success("Budget updated.")
            st.rerun()

with right:
    st.subheader("This month's budget")
    month_prefix = date.today().strftime("%Y-%m")
    month_purchases = purchases[purchases["purchase_date"].str.startswith(month_prefix)] if not purchases.empty else purchases
    spent = month_purchases.groupby("category")["amount"].sum() if not month_purchases.empty else pd.Series(dtype=float)

    dashboard = budgets.copy()
    dashboard["spent"] = dashboard["category"].map(spent).fillna(0.0)
    dashboard["remaining"] = dashboard["monthly_budget"] - dashboard["spent"]
    dashboard["remaining_pct"] = dashboard.apply(
        lambda r: (r["remaining"] / r["monthly_budget"]) if r["monthly_budget"] > 0 else (0 if r["spent"] > 0 else 1), axis=1
    )

    total_budget = dashboard["monthly_budget"].sum()
    total_spent = dashboard["spent"].sum()
    total_remaining = total_budget - total_spent
    m1, m2, m3 = st.columns(3)
    m1.metric("Tracked budget", f"${total_budget:,.2f}")
    m2.metric("Spent this month", f"${total_spent:,.2f}")
    m3.metric("Remaining", f"${total_remaining:,.2f}")

    group_filter = st.selectbox("Show", ["All categories"] + sorted(dashboard["group_name"].unique().tolist()))
    shown = dashboard if group_filter == "All categories" else dashboard[dashboard["group_name"] == group_filter]

    for _, row in shown.iterrows():
        color = status_color(row["remaining_pct"], row["remaining"])
        pct_used = 0 if row["monthly_budget"] <= 0 else min(max(row["spent"] / row["monthly_budget"] * 100, 0), 100)
        over_text = " • OVER BUDGET" if row["remaining"] < 0 else ""
        st.markdown(
            f"""
            <div class="budget-card">
                <div class="budget-name">{row['category']}</div>
                <div class="budget-sub">{row['group_name']} • ${row['spent']:,.2f} spent of ${row['monthly_budget']:,.2f}{over_text}</div>
                <div class="budget-number" style="color:{color}">${row['remaining']:,.2f} left</div>
                <div style="height:8px;background:#e5e7eb;border-radius:99px;margin-top:8px;overflow:hidden;">
                    <div style="width:{pct_used:.1f}%;height:100%;background:{color};"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()
st.subheader("Purchase history")
if purchases.empty:
    st.info("No purchases yet. Add your first one above.")
else:
    display = purchases.copy()
    display["amount"] = display["amount"].map(lambda x: f"${x:,.2f}")
    display = display.rename(columns={"purchase_date":"Date", "description":"Purchase", "amount":"Amount", "category":"Category", "notes":"Notes", "id":"ID"})
    st.dataframe(display, use_container_width=True, hide_index=True)

    with st.expander("Delete a purchase"):
        delete_id = st.selectbox(
            "Purchase",
            purchases["id"].tolist(),
            format_func=lambda x: f"#{x} — {purchases.loc[purchases['id']==x, 'description'].iloc[0]} (${purchases.loc[purchases['id']==x, 'amount'].iloc[0]:,.2f})"
        )
        if st.button("Delete selected purchase", type="secondary"):
            delete_purchase(delete_id)
            st.success("Purchase deleted.")
            st.rerun()

st.caption("Google Sheets sync can be added next without changing the purchase-entry workflow.")
