import pandas as pd

# === 1️⃣ Load your CSV ===
csv_path = "export.csv"  # <-- change this to your CSV file path
print(f"Loading {csv_path} ...")
df = pd.read_csv(csv_path)

print("\n=== Basic Info ===")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print("\nColumn names:", df.columns.tolist())

# === 2️⃣ Data types ===
print("\n=== Data Types ===")
print(df.dtypes)

# === 3️⃣ Missing values ===
print("\n=== Missing Values ===")
print(df.isna().sum().sort_values(ascending=False).head(20))

# === 4️⃣ Unique counts (cardinality) ===
print("\n=== Unique Values per Column ===")
unique_counts = df.nunique().sort_values(ascending=False)
print(unique_counts)

# === 5️⃣ Basic stats for numeric columns ===
print("\n=== Numeric Column Statistics ===")
print(df.describe().T)

# === 6️⃣ Example values for categorical columns ===
print("\n=== Example Categorical Values ===")
for col in df.select_dtypes(include=['object']).columns:
    unique_vals = df[col].dropna().unique()
    print(f"\n{col} → {len(unique_vals)} unique")
    print("Examples:", unique_vals)

print("\n✅ Exploration complete! Copy this output and paste it back into ChatGPT so I can help you choose partitioning columns.")
