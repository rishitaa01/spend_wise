import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

FILE_NAME = "expenses.csv"

# ---------------------------------------------------
# Create file if it does not exist
# ---------------------------------------------------
if not os.path.exists(FILE_NAME):
    pd.DataFrame(columns=["Date", "Category", "SubCategory", "Amount"]).to_csv(FILE_NAME, index=False)


# ---------------------------------------------------
# Load Data
# ---------------------------------------------------
def load_data():
    return pd.read_csv(FILE_NAME)


# ---------------------------------------------------
# Category & SubCategory Menu
# ---------------------------------------------------
def choose_category():

    categories = {
        "Food & Dining": ["Groceries", "Restaurants", "Snacks", "Cafeteria"],
        "Travelling": ["Bus", "Train", "Fuel", "Cab"],
        "Shopping": ["Clothes", "Electronics", "Accessories"],
        "Utilities": ["Electricity", "Water Bill", "Internet", "Rent"],
        "Miscellaneous": ["Subscriptions", "Entertainment", "Medical"]
    }

    print("\nSelect Expense Category:")
    category_list = list(categories.keys())

    for i, category in enumerate(category_list, 1):
        print(f"{i}. {category}")

    try:
        category_choice = int(input("Enter category number: "))
        selected_category = category_list[category_choice - 1]
    except:
        print("Invalid category choice.")
        return None, None

    print(f"\nSelect Sub-Category under '{selected_category}':")
    subcategories = categories[selected_category]

    for i, sub in enumerate(subcategories, 1):
        print(f"{i}. {sub}")

    try:
        sub_choice = int(input("Enter sub-category number: "))
        selected_subcategory = subcategories[sub_choice - 1]
    except:
        print("Invalid sub-category choice.")
        return None, None

    return selected_category, selected_subcategory


# ---------------------------------------------------
# Add Expense
# ---------------------------------------------------
def add_expense():

    date = input("Enter date (YYYY-MM-DD): ")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    category, subcategory = choose_category()
    if category is None:
        return

    try:
        amount = float(input("Enter amount spent: "))
        if amount <= 0:
            raise ValueError
    except:
        print("Amount must be a positive number.")
        return

    df = load_data()

    df.loc[len(df)] = [date, category, subcategory, amount]

    df.to_csv(FILE_NAME, index=False)

    print("Expense added successfully!")


# ---------------------------------------------------
# View All Expenses
# ---------------------------------------------------
def view_expenses():
    df = load_data()
    if df.empty:
        print("No expenses recorded yet.")
    else:
        print("\nHere are all your recorded expenses:\n")
        print(df.to_string(index=False))


# ---------------------------------------------------
# Calculate Total Spending
# ---------------------------------------------------
def calculate_total():
    df = load_data()
    total = df["Amount"].sum()
    print(f"\nTotal money spent so far: {total:.2f}")


# ---------------------------------------------------
# Monthly Summary
# ---------------------------------------------------
def monthly_summary():

    month = input("Enter month (YYYY-MM): ")

    try:
        datetime.strptime(month, "%Y-%m")
    except:
        print("Invalid month format.")
        return

    df = load_data()

    filtered = df[df["Date"].str.startswith(month)]

    if filtered.empty:
        print("No expenses found for this month.")
    else:
        print(f"\nTotal spending for {month}: {filtered['Amount'].sum():.2f}")


# ---------------------------------------------------
# Show Category-wise Graph
# ---------------------------------------------------
def show_graph():

    df = load_data()

    if df.empty:
        print("No data available to plot.")
        return

    grouped = df.groupby("Category")["Amount"].sum()

    grouped.plot(kind="bar")
    plt.title("Expenses by Category")
    plt.xlabel("Category")
    plt.ylabel("Total Amount Spent")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------
# Main Menu
# ---------------------------------------------------
def main():

    while True:
        print("\n====== Personal Expense Tracker ======")
        print("1. Add a New Expense Entry")
        print("2. View All Recorded Expenses")
        print("3. Calculate Total Money Spent")
        print("4. Show Category-wise Spending Graph")
        print("5. View Monthly Spending Summary")
        print("6. Exit the Application")
        print("======================================")

        choice = input("Select an option (1-6): ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            calculate_total()
        elif choice == "4":
            show_graph()
        elif choice == "5":
            monthly_summary()
        elif choice == "6":
            print("Exiting... Take care of your finances 😉")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()