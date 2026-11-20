from flask import Flask, render_template, request, redirect, url_for
from db import get_connection
from datetime import datetime, date

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

def get_user():
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key='user_name'").fetchone()
        return row[0] if row else None

def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

@app.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        name = request.form["name"].strip()
        if name:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO settings (key, value) VALUES ('user_name', %s) "
                    "ON CONFLICT (key) DO UPDATE SET value = %s",
                    (name, name)
                )
            return redirect(url_for("index", success="Welcome, " + name + "!"))
    return render_template("setup.html")

@app.route("/")
def index():
    user = get_user()
    if not user:
        return redirect(url_for("setup"))

    filter_date = request.args.get("date", "")
    category = request.args.get("category", "")
    success = request.args.get("success", "")
    
    query = "SELECT id, date, category, description, amount FROM expenses WHERE 1=1"
    params = []
    
    if filter_date:
        query += " AND date = %s"
        params.append(filter_date)
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
        
        if filter_date or category:
            filter_query = "SELECT SUM(amount) FROM expenses WHERE 1=1"
            filter_params = []
            if filter_date:
                filter_query += " AND date = %s"
                filter_params.append(filter_date)
            if category:
                filter_query += " AND category = %s"
                filter_params.append(category)
            filtered_total = conn.execute(filter_query, filter_params).fetchone()[0] or 0
        else:
            filtered_total = total
    
    is_filtered = bool(filter_date or category)
    greeting = get_greeting()
    today_str = date.today().isoformat()
    return render_template("index.html", expenses=expenses, summary=summary,
                         total=total, filtered_total=filtered_total,
                         categories=categories, date=filter_date, category=category,
                         is_filtered=is_filtered, success=success,
                         user=user, greeting=greeting, today=today_str)

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
    user = get_user()
    return render_template("edit.html", expense=expense, user=user)

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
