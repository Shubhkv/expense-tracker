# Expense Tracker

A command-line expense tracker built with Python and PostgreSQL.

## Features
- Add expenses by category
- View all expenses in a formatted table
- Summary of spending by category
- SQL queries for insights

## Tech Stack
- Python 3.15
- PostgreSQL 17
- psycopg (database driver)
- rich (terminal formatting)

## Setup
```bash
git clone https://github.com/Shubhkv/expense-tracker.git
cd expense-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install "psycopg[binary]" rich
createdb expenses
python3 models.py
python3 app.py
```

## Author
Shubham Kumar
