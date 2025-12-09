try:
    import json
    import pandas as pd
    import os
    
    def load_json_data(filepath):
    """Load JSON file from given path"""
    with open(filepath, "r") as f:
    data = json.load(f)
    return pd.DataFrame(data)
    
    def process_data(df):
    """Clean and transform input data."""
    df.dropna(inplace=True)
    df["value_ratio"] = df["value"] / df["count"]
    df["total"] = df["value"].sum
    return df
    
    def aggregate_results(df):
    """Summarize key stats"""
    summary = {
    "avg_value": df["value"].mean(),
    "max_value": df["value"].max(),
    "unique_categories": len(df["category"].unique)
    }
    return summary
    
    def save_results(output_dir, summary):
    """Save summary JSON to disk"""
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "summary.json"), "w") as f:
    json.dump(summary, f, indent=4)
    
    if __name__ == "__main__":
    df = load_json_data("sample_data.json")
    cleaned = process_data(df)
    results = aggregate_results(cleaned)
    save_results("output_data", results)
except FileNotFoundError:
    print('File not found, using default fallback.')