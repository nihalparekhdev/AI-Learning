"""
Data Analytics Lab: Sales Performance Analysis
-----------------------------------------------
Pipeline:
  1. Load / generate data
  2. Clean data
  3. Exploratory Data Analysis (EDA)
  4. Visualizations
  5. Predictive model (Linear Regression)
  6. Save report

Run:  python sales_analytics_lab.py
Needs: pandas, numpy, matplotlib, scikit-learn
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # works without a display; remove if you want pop-up windows
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)
np.random.seed(42)


# ---------------------------------------------------------------
# STEP 1: DATA COLLECTION
# (To use your own data instead: df = pd.read_csv("your_file.csv"))
# ---------------------------------------------------------------
def generate_data(n=2000):
    regions = ["North", "South", "East", "West"]
    categories = {"Electronics": 300, "Clothing": 50, "Home": 120, "Sports": 80}

    cat = np.random.choice(list(categories.keys()), n)
    base_price = np.array([categories[c] for c in cat])

    df = pd.DataFrame({
        "order_id": range(1, n + 1),
        "order_date": pd.to_datetime("2025-01-01")
                      + pd.to_timedelta(np.random.randint(0, 365, n), unit="D"),
        "region": np.random.choice(regions, n),
        "category": cat,
        "quantity": np.random.randint(1, 8, n),
        "unit_price": (base_price * np.random.uniform(0.8, 1.2, n)).round(2),
        "discount_pct": np.random.choice([0, 5, 10, 15, 20], n),
        "customer_age": np.random.randint(18, 70, n),
        "marketing_spend": np.random.uniform(10, 200, n).round(2),
    })
    df["revenue"] = (df["quantity"] * df["unit_price"]
                     * (1 - df["discount_pct"] / 100)
                     + df["marketing_spend"] * 0.5).round(2)

    # Inject messy data so the cleaning step is meaningful
    df.loc[np.random.choice(n, 40, replace=False), "customer_age"] = np.nan
    df.loc[np.random.choice(n, 25, replace=False), "region"] = None
    df = pd.concat([df, df.sample(30, random_state=1)], ignore_index=True)  # duplicates
    return df


df = generate_data()
print("=" * 60)
print("STEP 1: DATA LOADED")
print("=" * 60)
print(f"Shape: {df.shape}")
print(df.head(), "\n")


# ---------------------------------------------------------------
# STEP 2: DATA CLEANING
# ---------------------------------------------------------------
print("=" * 60)
print("STEP 2: DATA CLEANING")
print("=" * 60)
print("Missing values before:\n", df.isnull().sum()[df.isnull().sum() > 0], "\n")
print("Duplicate rows before:", df.duplicated().sum())

df = df.drop_duplicates()
df["customer_age"] = df["customer_age"].fillna(df["customer_age"].median())
df["region"] = df["region"].fillna(df["region"].mode()[0])

# Outlier check using the IQR method
q1, q3 = df["revenue"].quantile([0.25, 0.75])
iqr = q3 - q1
outliers = df[(df["revenue"] < q1 - 1.5 * iqr) | (df["revenue"] > q3 + 1.5 * iqr)]
print(f"Revenue outliers detected (kept for analysis): {len(outliers)}")

# Feature engineering
df["month"] = df["order_date"].dt.month
df["month_name"] = df["order_date"].dt.strftime("%b")
df["weekday"] = df["order_date"].dt.day_name()

print("Missing values after:", df.isnull().sum().sum())
print("Clean shape:", df.shape, "\n")


# ---------------------------------------------------------------
# STEP 3: EXPLORATORY DATA ANALYSIS
# ---------------------------------------------------------------
print("=" * 60)
print("STEP 3: EXPLORATORY DATA ANALYSIS")
print("=" * 60)
print(df[["quantity", "unit_price", "discount_pct", "revenue"]].describe().round(2), "\n")

rev_region = df.groupby("region")["revenue"].agg(["sum", "mean", "count"]).round(2)
rev_cat = df.groupby("category")["revenue"].agg(["sum", "mean", "count"]).round(2)
monthly = df.groupby("month")["revenue"].sum()

print("Revenue by region:\n", rev_region, "\n")
print("Revenue by category:\n", rev_cat, "\n")

num_cols = ["quantity", "unit_price", "discount_pct", "customer_age",
            "marketing_spend", "revenue"]
corr = df[num_cols].corr().round(2)
print("Correlation with revenue:\n", corr["revenue"].sort_values(ascending=False), "\n")


# ---------------------------------------------------------------
# STEP 4: VISUALIZATION
# ---------------------------------------------------------------
print("=" * 60)
print("STEP 4: VISUALIZATION")
print("=" * 60)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Sales Analytics Dashboard", fontsize=18, fontweight="bold")

# 1. Monthly revenue trend
axes[0, 0].plot(monthly.index, monthly.values, arker="o", color="#2a6fdb")
axes[0, 0].set(title="Monthly Revenue Trend", xlabel="Month", ylabel="Revenue")
axes[0, 0].grid(alpha=0.3)

# 2. Revenue by region
axes[0, 1].bar(rev_region.index, rev_region["sum"], color="#2aa876")
axes[0, 1].set(title="Total Revenue by Region", ylabel="Revenue")

# 3. Revenue share by category
axes[0, 2].pie(rev_cat["sum"], labels=rev_cat.index, autopct="%1.1f%%", startangle=90)
axes[0, 2].set_title("Revenue Share by Category")

# 4. Revenue distribution
axes[1, 0].hist(df["revenue"], bins=40, color="#e08a1e", edgecolor="white")
axes[1, 0].set(title="Revenue Distribution", xlabel="Revenue", ylabel="Frequency")

# 5. Marketing spend vs revenue
axes[1, 1].scatter(df["marketing_spend"], df["revenue"], alpha=0.3, s=10, color="#8a4fd6")
axes[1, 1].set(title="Marketing Spend vs Revenue", xlabel="Marketing Spend", ylabel="Revenue")

# 6. Correlation heatmap
im = axes[1, 2].imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
axes[1, 2].set_xticks(range(len(num_cols)))
axes[1, 2].set_yticks(range(len(num_cols)))
axes[1, 2].set_xticklabels(num_cols, rotation=45, ha="right")
axes[1, 2].set_yticklabels(num_cols)
axes[1, 2].set_title("Correlation Heatmap")
fig.colorbar(im, ax=axes[1, 2], shrink=0.8)

plt.tight_layout()
dash_path = os.path.join(OUT_DIR, "dashboard.png")
plt.savefig(dash_path, dpi=150)
plt.close()
print(f"Saved: {dash_path}\n")


# ---------------------------------------------------------------
# STEP 5: PREDICTIVE MODEL
# ---------------------------------------------------------------
print("=" * 60)
print("STEP 5: PREDICTIVE MODELING (Linear Regression)")
print("=" * 60)

features = ["quantity", "unit_price", "discount_pct", "marketing_spend"]
X, y = df[features], df["revenue"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression().fit(X_train, y_train)
pred = model.predict(X_test)
r2 = r2_score(y_test, pred)
mae = mean_absolute_error(y_test, pred)

print(f"R2 score : {r2:.3f}")
print(f"MAE      : {mae:.2f}")
for f, c in zip(features, model.coef_):
    print(f"  coefficient[{f}] = {c:.3f}")

plt.figure(figsize=(6, 6))
plt.scatter(y_test, pred, alpha=0.4, s=12)
lims = [y_test.min(), y_test.max()]
plt.plot(lims, lims, "r--", label="Perfect prediction")
plt.xlabel("Actual Revenue")
plt.ylabel("Predicted Revenue")
plt.title("Actual vs Predicted Revenue")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "model_performance.png"), dpi=150)
plt.close()


# ---------------------------------------------------------------
# STEP 6: REPORT
# ---------------------------------------------------------------
best_region = rev_region["sum"].idxmax()
best_cat = rev_cat["sum"].idxmax()
best_month = monthly.idxmax()

report = f"""SALES ANALYTICS LAB: SUMMARY REPORT
{'=' * 45}
Records analysed     : {len(df)}
Total revenue        : {df['revenue'].sum():,.2f}
Average order value  : {df['revenue'].mean():,.2f}

Top region           : {best_region}
Top category         : {best_cat}
Best month           : {best_month}

Strongest driver of revenue: {corr['revenue'].drop('revenue').abs().idxmax()}

Model performance    : R2 = {r2:.3f}, MAE = {mae:.2f}

Conclusions
- Focus marketing on the {best_region} region and {best_cat} category.
- Plan inventory ahead of month {best_month}, the seasonal peak.
- Discounts reduce revenue per order; test whether they lift volume enough.
"""
with open(os.path.join(OUT_DIR, "report.txt"), "w") as f:
    f.write(report)
df.to_csv(os.path.join(OUT_DIR, "cleaned_sales_data.csv"), index=False)

print("\n" + report)
print(f"All outputs saved in the '{OUT_DIR}/' folder.")