from db import get_connection
from rich.console import Console

console = Console()

with get_connection() as conn:
    # Total spent today
    total = conn.execute("SELECT SUM(amount) FROM expenses WHERE date = CURRENT_DATE").fetchone()[0]
    console.print(f"[bold]Total spent today:[/bold] ₹{total}")

    # Most expensive item
    row = conn.execute("SELECT description, amount FROM expenses ORDER BY amount DESC LIMIT 1").fetchone()
    console.print(f"[bold]Most expensive:[/bold] {row[0]} - ₹{row[1]}")

    # Count of expenses per category
    rows = conn.execute("SELECT category, COUNT(*) FROM expenses GROUP BY category").fetchall()
    console.print("\n[bold]Expense count by category:[/bold]")
    for r in rows:
        console.print(f"  {r[0]}: {r[1]} items")
