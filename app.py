from db import get_connection
from rich.table import Table
from rich.console import Console

console = Console()

def add_expense(category, description, amount):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO expenses (category, description, amount) VALUES (%s, %s, %s)",
            (category, description, amount)
        )
    print(f"Added: {category} - {description} - ₹{amount}")

def view_expenses():
    with get_connection() as conn:
        rows = conn.execute("SELECT date, category, description, amount FROM expenses ORDER BY date DESC").fetchall()
    
    table = Table(title="My Expenses")
    table.add_column("Date", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Amount (₹)", style="green", justify="right")
    
    for row in rows:
        table.add_row(str(row[0]), row[1], row[2], str(row[3]))
    
    console.print(table)

def summary_by_category():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses GROUP BY category ORDER BY total DESC"
        ).fetchall()
    
    table = Table(title="Spending by Category")
    table.add_column("Category", style="magenta")
    table.add_column("Total (₹)", style="green", justify="right")
    
    for row in rows:
        table.add_row(row[0], str(row[1]))
    
    console.print(table)

if __name__ == "__main__":
    # Add some sample expenses
    add_expense("Food", "Lunch at cafe", 250)
    add_expense("Transport", "Uber to office", 180)
    add_expense("Food", "Groceries", 850)
    add_expense("Entertainment", "Netflix", 499)
    add_expense("Transport", "Metro card recharge", 500)
    
    print()
    view_expenses()
    print()
    summary_by_category()
