
import requests
import pandas as pd
import sqlite3

API_KEY = 'YOUR_API_KEY'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

def fetch_data(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def clean_dataframe(df):
    for col in df.columns:
        if isinstance(df[col].iloc[0], (dict, list)):
            df[col] = df[col].apply(lambda x: str(x) if x is not None else None)
    return df

def get_competitions():
    data = fetch_data("competitions")
    if data:
        competitions = data.get("competitions", [])
        df = pd.DataFrame(competitions)
        return clean_dataframe(df)
    return None

def get_matches(competition_id):
    data = fetch_data(f"competitions/{competition_id}/matches")
    if data:
        matches = data.get("matches", [])
        df = pd.DataFrame(matches)
        return clean_dataframe(df)
    return None

def save_to_database(df, table_name, database="football_data.db"):
    if df is not None and not df.empty:
        conn = sqlite3.connect(database)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        print(f"Data saved to table '{table_name}' in {database}.")
    else:
        print(f"No data to save for table '{table_name}'.")

def main():
    competitions_df = get_competitions()
    save_to_database(competitions_df, "competitions")

    premier_league_id = 2021
    matches_df = get_matches(premier_league_id)
    save_to_database(matches_df, "matches")

if __name__ == "__main__":
    main()
