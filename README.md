# PLOTT Budget App

A local Streamlit web app for quickly entering purchases, assigning categories, and seeing remaining monthly category balances.

## Mac setup

1. Install Python 3 from https://www.python.org/downloads/ if you do not already have it.
2. Open Terminal.
3. Go to this folder, for example:
   ```bash
   cd ~/Downloads/plott_budget_app
   ```
4. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```
5. Activate it:
   ```bash
   source .venv/bin/activate
   ```
6. Install the app packages:
   ```bash
   pip install -r requirements.txt
   ```
7. Start the app:
   ```bash
   streamlit run app.py
   ```
8. Your browser should open automatically. If it does not, Terminal will show a Local URL such as http://localhost:8501.

## Where the data is saved

The app automatically creates `plott_budget.db` in the same folder. Do not delete that file unless you want to erase the app's saved purchases.

## Stop the app

Go back to Terminal and press Control+C.

## Start it again later

```bash
cd ~/Downloads/plott_budget_app
source .venv/bin/activate
streamlit run app.py
```

## Google Sheets later

The next version can add Google Sheets sync using the Google Sheets API. SQLite should stay as the app's local database, while new/edited purchases are mirrored to a Google Sheet.
