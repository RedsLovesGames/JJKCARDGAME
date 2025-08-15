import pandas as pd
import os

def test_load_characters():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'characters.csv')
    
    print(f"Trying to load characters.csv from: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        print("Loaded characters.csv successfully!")
        print(df.head())  # Print the first few rows
    except FileNotFoundError:
        print("Error: characters.csv not found.")

if __name__ == "__main__":
    test_load_characters() 