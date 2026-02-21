import { useEffect, useState } from "react";
import axios from "axios";

const API = "https://spendwise-backend.onrender.com";

function App() {

  const categories = {
    "Food & Dining": ["Groceries", "Restaurants", "Snacks","Lunch","Dinner","Breakfast"],
    "Travelling": ["Bus", "Train", "Fuel"],
    "Shopping": ["Clothes", "Electronics"],
    "Utilities": ["Electricity", "Water Bill", "Internet"],
    "Miscellaneous": ["Subscriptions", "Medical"]
  };

  const [expenses, setExpenses] = useState([]);
  const [total, setTotal] = useState(0);
  const [monthlyTotals, setMonthlyTotals] = useState([]);

  const [selectedMonth, setSelectedMonth] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");

  const [summaryMonth, setSummaryMonth] = useState("");
  const [monthlySummary, setMonthlySummary] = useState(null);

  const [budgetMonth, setBudgetMonth] = useState("");
  const [budgetAmount, setBudgetAmount] = useState("");
  const [budgetStatus, setBudgetStatus] = useState(null);

  const [formData, setFormData] = useState({
    date: "",
    category: "",
    subcategory: "",
    amount: ""
  });

  // ================= FETCH FUNCTIONS =================

  const fetchExpenses = async () => {
    const res = await axios.get("http://127.0.0.1:5000//expenses");

    const normalized = res.data.map(item => ({
      Date: item.Date || item.date,
      Category: item.Category || item.category,
      SubCategory: item.SubCategory || item.subcategory,
      Amount: item.Amount || item.amount
    }));

    setExpenses(normalized);
  };

  const fetchTotal = async () => {
    const res = await axios.get("http://127.0.0.1:5000//total");
    setTotal(res.data.total);
  };

  const fetchMonthlyTotals = async () => {
    const res = await axios.get("http://127.0.0.1:5000//monthly-totals");
    setMonthlyTotals(res.data);
  };

  useEffect(() => {
    fetchExpenses();
    fetchTotal();
    fetchMonthlyTotals();
  }, []);

  // ================= MONTHLY SUMMARY =================

  const fetchMonthlySummary = async () => {
    if (!summaryMonth) return;

    const res = await axios.get(
      `http://127.0.0.1:5000//monthly-summary/${summaryMonth}`
    );

    setMonthlySummary(res.data);
  };

  // ================= BUDGET SYSTEM =================

  const setBudget = async () => {
    if (!budgetMonth || !budgetAmount) return;

    await axios.post("http://127.0.0.1:5000//set-budget", {
      month: budgetMonth,
      budget: budgetAmount
    });

    alert("Budget Set Successfully!");
  };

  const fetchBudgetStatus = async () => {
    if (!budgetMonth) return;

    const res = await axios.get(
      `http://127.0.0.1:5000//budget-status/${budgetMonth}`
    );

    setBudgetStatus(res.data);
  };

  // ================= FORM HANDLING =================

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === "category") {
      setFormData({
        ...formData,
        category: value,
        subcategory: ""
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    await axios.post("http://127.0.0.1:5000//add-expense", formData);

    fetchExpenses();
    fetchTotal();
    fetchMonthlyTotals();

    setFormData({
      date: "",
      category: "",
      subcategory: "",
      amount: ""
    });
  };

  // ================= UI =================

  return (
    <div className="container">
      <h1>Expense Tracker</h1>

      {/* ADD EXPENSE */}
      <div className="card">
        <h2>Add Expense</h2>
        <form onSubmit={handleSubmit} className="form">
          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            required
          />

          <select
            name="category"
            value={formData.category}
            onChange={handleChange}
            required
          >
            <option value="">Select Category</option>
            {Object.keys(categories).map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>

          <select
            name="subcategory"
            value={formData.subcategory}
            onChange={handleChange}
            required
            disabled={!formData.category}
          >
            <option value="">Select SubCategory</option>
            {formData.category &&
              categories[formData.category].map((sub) => (
                <option key={sub} value={sub}>{sub}</option>
              ))}
          </select>

          <input
            type="number"
            name="amount"
            value={formData.amount}
            placeholder="Amount"
            onChange={handleChange}
            required
          />

          <button type="submit">Add Expense</button>
        </form>
      </div>

      {/* TOTAL */}
      <div className="card">
        <h2>Total: ₹{total}</h2>
      </div>

      {/* MONTHLY TOTALS */}
      <div className="card">
        <h2>Monthly Totals</h2>
        <ul>
          {monthlyTotals.map((item, index) => (
            <li key={index}>
              {item.Month} : ₹{item.Amount}
            </li>
          ))}
        </ul>
      </div>

      {/* MONTHLY SUMMARY */}
      <div className="card">
        <h2>Monthly Summary</h2>
        <input
          type="month"
          value={summaryMonth}
          onChange={(e) => setSummaryMonth(e.target.value)}
        />
        <button onClick={fetchMonthlySummary}>Get Summary</button>

        {monthlySummary && (
          <div>
            <p>Total: ₹{monthlySummary.total}</p>
            <h4>Category Breakdown:</h4>
            <ul>
              {Object.entries(monthlySummary.categories).map(([cat, amt]) => (
                <li key={cat}>
                  {cat}: ₹{amt}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* BUDGET SYSTEM */}
      <div className="card">
        <h2>Budget System</h2>

        <input
          type="month"
          value={budgetMonth}
          onChange={(e) => setBudgetMonth(e.target.value)}
        />

        <input
          type="number"
          placeholder="Enter Budget Amount"
          value={budgetAmount}
          onChange={(e) => setBudgetAmount(e.target.value)}
        />

        <div>
          <button onClick={setBudget}>Set Budget</button>
          <button onClick={fetchBudgetStatus} style={{ marginLeft: "10px" }}>
            Check Budget
          </button>
        </div>

        {budgetStatus && (
          <div>
            <p>Budget: ₹{budgetStatus.budget}</p>
            <p>Spent: ₹{budgetStatus.spent}</p>
            <p>Remaining: ₹{budgetStatus.remaining}</p>

            {budgetStatus.remaining < 0 && (
              <p style={{ color: "red", fontWeight: "bold" }}>
                ⚠ Budget Exceeded!
              </p>
            )}
          </div>
        )}
      </div>

      {/* CATEGORY BAR CHART */}
      <div className="card">
        <h2>Category Chart</h2>
        <img
          src="http://127.0.0.1:5000//chart"
          alt="Category Chart"
          style={{ width: "100%", maxWidth: "700px" }}
        />
      </div>

      {/* MONTHLY LINE CHART */}
      <div className="card">
        <h2>Monthly Comparison</h2>
        <img
          src="http://127.0.0.1:5000//line-chart"
          alt="Line Chart"
          style={{ width: "100%", maxWidth: "700px" }}
        />
      </div>

      {/* PIE CHART */}
      <div className="card">
        <h2>Pie Chart (Month + Category)</h2>

        <div style={{ display: "flex", gap: "10px" }}>
          <input
            type="month"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
          />

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="">Select Category</option>
            {Object.keys(categories).map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {selectedMonth && selectedCategory ? (
          <img
            src={`http://127.0.0.1:5000//pie-chart/${selectedMonth}/${encodeURIComponent(selectedCategory)}`}
            alt="Pie Chart"
            style={{ width: "100%", maxWidth: "600px" }}
          />
        ) : (
          <p style={{ opacity: 0.6 }}>
            Select month and category to view chart
          </p>
        )}
      </div>

    </div>
  );
}

export default App;