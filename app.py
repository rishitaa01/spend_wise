from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd

app = Flask(__name__)
CORS(app)

FILE_NAME = "expenses.csv"
BUDGET_FILE = "budgets.csv"

# ================= INITIALIZE FILES =================
def initialize_files():
    if not os.path.exists(FILE_NAME):
        pd.DataFrame(columns=["Date", "Category", "SubCategory", "Amount"]).to_csv(FILE_NAME, index=False)

    if not os.path.exists(BUDGET_FILE):
        pd.DataFrame(columns=["Month", "Budget"]).to_csv(BUDGET_FILE, index=False)

initialize_files()


# ================= LOAD EXPENSES =================
def load_expenses():
    df = pd.read_csv(FILE_NAME)

    if df.empty:
        return df

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df = df.dropna(subset=["Amount"])

    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    return df


# ================= ADD EXPENSE =================
@app.route("/add-expense", methods=["POST"])
def add_expense():
    data = request.json

    new_row = pd.DataFrame([[data["date"], data["category"], data["subcategory"], data["amount"]]],
                           columns=["Date", "Category", "SubCategory", "Amount"])

    new_row.to_csv(FILE_NAME, mode='a', header=False, index=False)

    return jsonify({"message": "Expense added successfully"})


# ================= GET ALL =================
@app.route("/expenses", methods=["GET"])
def get_expenses():
    return jsonify(pd.read_csv(FILE_NAME).to_dict(orient="records"))


# ================= TOTAL =================
@app.route("/total", methods=["GET"])
def get_total():
    df = load_expenses()
    return jsonify({"total": float(df["Amount"].sum()) if not df.empty else 0})


# ================= MONTHLY TOTALS =================
@app.route("/monthly-totals", methods=["GET"])
def monthly_totals():
    df = load_expenses()
    if df.empty:
        return jsonify([])

    monthly = df.groupby("Month")["Amount"].sum().reset_index()
    return jsonify(monthly.to_dict(orient="records"))


# ================= MONTHLY SUMMARY (SPECIFIC MONTH) =================
@app.route("/monthly-summary/<month>", methods=["GET"])
def monthly_summary(month):
    df = load_expenses()

    filtered = df[df["Month"] == month]

    if filtered.empty:
        return jsonify({"total": 0, "categories": {}})

    total = float(filtered["Amount"].sum())
    category_breakdown = filtered.groupby("Category")["Amount"].sum().to_dict()

    return jsonify({
        "total": total,
        "categories": category_breakdown
    })


# ================= CATEGORY CHART =================
@app.route("/chart", methods=["GET"])
def category_chart():
    df = load_expenses()

    if df.empty:
        return jsonify({"error": "No data"})

    grouped = df.groupby("Category")["Amount"].sum()

    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(grouped.index, grouped.values)
    ax.set_title("Expenses by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = BytesIO()
    fig.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)

    return send_file(img, mimetype="image/png")


# ================= MONTHLY LINE CHART =================
@app.route("/line-chart", methods=["GET"])
def line_chart():
    df = load_expenses()

    if df.empty:
        return jsonify({"error": "No data"})

    monthly = df.groupby("Month")["Amount"].sum().sort_index()

    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(monthly.index, monthly.values, marker="o")
    ax.set_title("Monthly Expense Comparison")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = BytesIO()
    fig.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)

    return send_file(img, mimetype="image/png")


# ================= PIE CHART =================
@app.route("/pie-chart/<month>/<category>", methods=["GET"])
def pie_chart(month, category):
    df = load_expenses()

    filtered = df[(df["Month"] == month) & (df["Category"] == category)]

    if filtered.empty:
        return jsonify({"error": "No data"})

    grouped = filtered.groupby("SubCategory")["Amount"].sum()

    fig, ax = plt.subplots(figsize=(6,6))
    ax.pie(grouped.values, labels=grouped.index, autopct="%1.1f%%")
    ax.set_title(f"{month} - {category}")

    img = BytesIO()
    fig.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)

    return send_file(img, mimetype="image/png")


# ================= BUDGET SYSTEM =================
@app.route("/set-budget", methods=["POST"])
def set_budget():
    data = request.json
    month = data["month"]
    budget_value = float(data["budget"])

    budgets = pd.read_csv(BUDGET_FILE)
    budgets = budgets[budgets["Month"] != month]

    new_row = pd.DataFrame([[month, budget_value]], columns=["Month", "Budget"])
    budgets = pd.concat([budgets, new_row], ignore_index=True)
    budgets.to_csv(BUDGET_FILE, index=False)

    return jsonify({"message": "Budget set successfully"})


@app.route("/budget-status/<month>", methods=["GET"])
def budget_status(month):
    df = load_expenses()
    budgets = pd.read_csv(BUDGET_FILE)

    if month not in budgets["Month"].values:
        return jsonify({"budget": 0, "spent": 0, "remaining": 0})

    budget_value = float(budgets[budgets["Month"] == month]["Budget"].values[0])
    spent = df[df["Month"] == month]["Amount"].sum() if not df.empty else 0
    remaining = budget_value - spent

    return jsonify({
        "budget": budget_value,
        "spent": float(spent),
        "remaining": float(remaining)
    })


if __name__ == "__main__":
    app.run(debug=True)