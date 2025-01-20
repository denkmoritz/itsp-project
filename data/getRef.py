import pandas as pd

csv_path = 'data/keys.csv'

# Function to get all road names and states
def get_ref_list():
    try:
        df = pd.read_csv(csv_path)
        df['ref'] = df['ref'].astype(str).fillna('').str.strip()
        df['ISO_1'] = df['ISO_1'].astype(str).fillna('').str.strip()
        grouped = df.groupby('ISO_1')['ref'].apply(list).to_dict()
        return grouped
    except Exception as e:
        print(f"Error: Failed to load refs and ISO_1 from CSV: {e}")
        return {}