# build_partitioned_parquet.py
import pandas as pd
from pathlib import Path

CSV_PATH = "export.csv"            # <- change if needed
OUT_DIR = Path("health_parquet")   # output dataset root

def main():
    print("Loading CSV...")
    # Keep all columns exactly as-is
    df = pd.read_csv(CSV_PATH, low_memory=False)

    # Parse timestamps (keep rows that have a valid @startDate)
    if "@startDate" not in df.columns:
        raise ValueError("Column '@startDate' not found in CSV.")
    df["@startDate"] = pd.to_datetime(df["@startDate"], utc=True, errors="coerce")
    df = df.dropna(subset=["@startDate"])

    # Derive time partitions
    df["year"] = df["@startDate"].dt.year.astype("int32")
    df["month"] = df["@startDate"].dt.month.astype("int16")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Writing partitioned Parquet (Snappy) to {OUT_DIR} ...")

    # Partition only by time (year/month). No mapping, no schema changes.
    df.to_parquet(
        OUT_DIR,
        engine="pyarrow",
        compression="snappy",
        partition_cols=["year", "month"],
        index=False,
    )

    print("Done ✅")
    # Optional: quick summary
    print("Partitions created (sample):")
    print(df.groupby(["year", "month"]).size().head(12))

if __name__ == "__main__":
    main()
