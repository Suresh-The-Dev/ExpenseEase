from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def create_database():
    connection = sqlite3.connect("expenses.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    # Get all expenses
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    # Total expenses
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expense = cursor.fetchone()[0] or 0

    # Today's expenses
    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE date = DATE('now')
    """)
    today_expense = cursor.fetchone()[0] or 0

    # Current month's expenses
    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """)
    monthly_expense = cursor.fetchone()[0] or 0

    # Category-wise expenses
    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
    """)
    category_expenses = cursor.fetchall()

    connection.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total_expense=total_expense,
        today_expense=today_expense,
        monthly_expense=monthly_expense,
        category_expenses=category_expenses
    )


@app.route("/add")
def add_expense():
    return render_template("add_expense.html")

@app.route("/add", methods=["POST"])
def save_expense():

    amount = request.form["amount"]
    category = request.form["category"]
    description = request.form["description"]
    date = request.form["date"]

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses (amount, category, description, date)
        VALUES (?, ?, ?, ?)
    """, (amount, category, description, date))

    connection.commit()
    connection.close()

    return redirect("/")

# This function is responsible for selecting the expense to edit
@app.route("/edit/<int:id>")
def edit_expense(id):

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (id,)
    )

    expense = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_expense.html",
        expense=expense
    )

# Thie below funcrion is responsible for updating the selected expense with all fields
@app.route("/edit/<int:id>", methods=["POST"])
def update_expense(id):

    amount = request.form["amount"]
    category = request.form["category"]
    description = request.form["description"]
    date = request.form["date"]

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE expenses
        SET amount = ?, category = ?, description = ?, date = ?
        WHERE id = ?
    """, (amount, category, description, date, id))

    connection.commit()
    connection.close()

    return redirect("/")

# To delete the given expense with id {id}
@app.route("/delete/<int:id>")
def delete_expense(id):

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/")

if __name__ == "__main__":
    create_database()
    app.run(debug=True)