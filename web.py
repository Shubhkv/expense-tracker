from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_connection

app = Flask(__name__)
app.secret_key = "expense-tracker-dev"

@app.template_filter('money')
def money_filter(value):
    return f"{float(value):,.2f}"

@app.template_filter('dateformat')
def date_filter(value):
    from datetime import date
    if isinstance(value, date):
        return value.strftime("%d %b %Y")
    return str(value)

@app.route("/")
def index():
    month = request.args.get("month", "")
    category = request.args.get("category", "")
    success = request.args.get("success", "")
    
    query = "SELECT id, date, category, description, amount FROM expenses WHERE 1=1"
    params = []
    
    if month:
        query += " AND TO_CHAR(date, 'YYYY-MM') = %s"
        params.append(month)
    if category:
        query += " AND category = %s"
        params.append(category)
    
    query += " ORDER BY date DESC"
    
    with get_connection() as conn:
        expenses = conn.execute(query, params).fetchall()
        summary = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses GROUP BY category ORDER BY total DESC"
        ).fetchall()
        total = conn.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0
        categories = conn.execute("SELECT DISTINCT category FROM expenses ORDER BY category").fetchall()
        
        # Filtered total
        if month or category:
            filter_query = "SELECT SUM(amount) FROM expenses WHERE 1=1"
            filter_params = []
            if month:
                filter_query += " AND TO_CHAR(date, 'YYYY-MM') = %s"
                filter_params.append(month)
            if category:
                filter_query += " AND category = %s"
                filter_params.append(category)
            filtered_total = conn.execute(filter_query, filter_params).fetchone()[0] or 0
        else:
            filtered_total = total
    
    is_filtered = bool(month or category)
    return render_template("index.html", expenses=expenses, summary=summary,
                         total=total, filtered_total=filtered_total,
                         categories=categories, month=month, category=category,
                         is_filtered=is_filtered, success=success)

@app.route("/add", methods=["POST"])
def add():
    category = request.form["category"]
    description = request.form["description"]
    amount = request.form["amount"]
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO expenses (category, description, amount) VALUES (%s, %s, %s)",
            (category, description, amount)
        )
    return redirect(url_for("index", success=f"Added ₹{float(amount):,.2f} for {description}"))

@app.route("/delete/<int:id>")
def delete(id):
    with get_connection() as conn:
        conn.execute("DELETE FROM expenses WHERE id = %s", (id,))
    return redirect(url_for("index", success="Expense deleted"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "POST":
        category = request.form["category"]
        description = request.form["description"]
        amount = request.form["amount"]
        with get_connection() as conn:
            conn.execute(
                "UPDATE expenses SET category=%s, description=%s, amount=%s WHERE id=%s",
                (category, description, amount, id)
            )
        return redirect(url_for("index", success="Expense updated"))
    with get_connection() as conn:
        expense = conn.execute("SELECT id, date, category, description, amount FROM expenses WHERE id=%s", (id,)).fetchone()
    return render_template("edit.html", expense=expense)

@app.route("/export")
def export():
    import csv, io
    from flask import Response
    with get_connection() as conn:
        expenses = conn.execute("SELECT date, category, description, amount FROM expenses ORDER BY date DESC").fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Category", "Description", "Amount"])
    for e in expenses:
        writer.writerow(e)
    return Response(output.getvalue(), mimetype="text/csv",
                   headers={"Content-Disposition": "attachment;filename=expenses.csv"})

if __name__ == "__main__":
    app.run(debug=True)
