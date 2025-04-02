import os
import pandas as pd
from typing import Dict

summary_data = [
    {
        "Sailing Number": "1",
        "Ship Name": "Explorer",
        "Holiday and Ship Experience": 7.546012,
        "Cabins": 7.268293,
        "F&B Quality Overall": 7.032143,
        "F&B Service Overall": 7.708633,
        "F&B Quality Main Dining": 4.419355,
        "Entertainment": 6.976744,
        "Excursions": 4.620253,
        "Sentiment Analysis": 6.689441,
        "Bar Service": 6.716667,
        "Cabin Cleanliness": 8.72549,
        "Crew Friendliness": 8.187179,
        "Drinks Offerings": 6.822917,
        "App Booking": 1.5,
        "Flight": 2.208333,
        "Hotel Accommodation": 7.458333,
        "Prior Customer Care": 6.074074
    },
    {
        "Sailing Number": "1",
        "Ship Name": "Explorer 2",
        "Holiday and Ship Experience": 7.652482,
        "Cabins": 6.708333,
        "F&B Quality Overall": 7.441441,
        "F&B Service Overall": 8.314159,
        "F&B Quality Main Dining": 6.193548,
        "Entertainment": 7.53,
        "Excursions": 5.75,
        "Sentiment Analysis": 6.603571,
        "Bar Service": 7.045455,
        "Cabin Cleanliness": 8.857143,
        "Crew Friendliness": 8.482036,
        "Drinks Offerings": 6.36,
        "App Booking": 3.608696,
        "Flight": 2.95,
        "Hotel Accommodation": 6.2777,
        "Prior Customer Care": 3.857143
    },
    {
        "Sailing Number": "1",
        "Ship Name": "Discovery",
        "Holiday and Ship Experience": 7.4875,
        "Cabins": 6,
        "F&B Quality Overall": 7.239011,
        "F&B Service Overall": 7.497191,
        "F&B Quality Main Dining": 5.2,
        "Entertainment": 7.584416,
        "Excursions": 4.877193,
        "Sentiment Analysis": 6.547009,
        "Bar Service": 6.482143,
        "Cabin Cleanliness": 7.946809,
        "Crew Friendliness": 8.529148,
        "Drinks Offerings": 5.911765,
        "App Booking": 2.826087,
        "Flight": 2.733333,
        "Hotel Accommodation": 7,
        "Prior Customer Care": 5.84375
    },
    {
        "Sailing Number": "1",
        "Ship Name": "Discovery 2",
        "Holiday and Ship Experience": 7.723757,
        "Cabins": 6.840278,
        "F&B Quality Overall": 7.651852,
        "F&B Service Overall": 7.57718,
        "F&B Quality Main Dining": 5.888889,
        "Entertainment": 7.599099,
        "Excursions": 6.188889,
        "Sentiment Analysis": 6.618644,
        "Bar Service": 5.412698,
        "Cabin Cleanliness": 8.794118,
        "Crew Friendliness": 8.716374,
        "Drinks Offerings": 5.822222,
        "App Booking": 3.4,
        "Flight": 3.4,
        "Hotel Accommodation": 7.041667,
        "Prior Customer Care": 5.965517
    },
    {
        "Sailing Number": "12",
        "Ship Name": "Voyager",
        "Holiday and Ship Experience": 7.711462,
        "Cabins": 6.846939,
        "F&B Quality Overall": 7.229268,
        "F&B Service Overall": 7.497573,
        "F&B Quality Main Dining": 5.843137,
        "Entertainment": 7.895706,
        "Excursions": 5.973913,
        "Sentiment Analysis": 6.619565,
        "Bar Service": 5.382022,
        "Cabin Cleanliness": 8.574627,
        "Crew Friendliness": 8.701717,
        "Drinks Offerings": 5.452055,
        "App Booking": 3.333333,
        "Flight": 1.734043,
        "Hotel Accommodation": 6.333333,
        "Prior Customer Care": 4.928571
    },
    {
        "Sailing Number": "1",
        "Ship Name": "Voyager",
        "Holiday and Ship Experience": 7.297674,
        "Cabins": 6.6,
        "F&B Quality Overall": 7.154321,
        "F&B Service Overall": 7.76,
        "F&B Quality Main Dining": 5.176471,
        "Entertainment": 7.460993,
        "Excursions": 4.661017,
        "Sentiment Analysis": 5.773756,
        "Bar Service": 5.152542,
        "Cabin Cleanliness": 8.21875,
        "Crew Friendliness": 8.579787,
        "Drinks Offerings": 6.061224,
        "App Booking": 2.852941,
        "Flight": 2.62963,
        "Hotel Accommodation": 7.090909,
        "Prior Customer Care": 4.690476
    },
    {
        "Sailing Number": "CR352",
        "Ship Name": "Voyager",
        "Holiday and Ship Experience": 7.523364,
        "Cabins": 6.316667,
        "F&B Quality Overall": 7.38255,
        "F&B Service Overall": 7.576923,
        "F&B Quality Main Dining": 5.8617,
        "Entertainment": 7.72314,
        "Excursions": 5.861702,
        "Sentiment Analysis": 6.174528,
        "Bar Service": 5.32,
        "Cabin Cleanliness": 8.384615,
        "Crew Friendliness": 8.742424,
        "Drinks Offerings": 5.851852,
        "App Booking": 3.608696,
        "Flight": 2.433333,
        "Hotel Accommodation": 6.75,
        "Prior Customer Care": 5.538462
    },
    {
        "Sailing Number": "CR353",
        "Ship Name": "Voyager",
        "Holiday and Ship Experience": 7.197115,
        "Cabins": 5.843284,
        "F&B Quality Overall": 6.862179,
        "F&B Service Overall": 7.037267,
        "F&B Quality Main Dining": 4.719512,
        "Entertainment": 7.177778,
        "Excursions": 4.783133,
        "Sentiment Analysis": 5.618421,
        "Bar Service": 4.58427,
        "Cabin Cleanliness": 7.925,
        "Crew Friendliness": 8.26455,
        "Drinks Offerings": 4.840426,
        "App Booking": 3.684211,
        "Flight": 1.888889,
        "Hotel Accommodation": 5.695652,
        "Prior Customer Care": 5.117647
    }
    ]

def get_summary_data():
    return summary_data

def load_sailing_data(data_dir: str = "/workspaces/com-rev-dtc/mr_data") -> Dict[str, pd.DataFrame]:
    """
    Load all sailing data CSV files from a directory into DataFrames
    
    Args:
        data_dir: Directory containing sailing data CSV files
        
    Returns:
        Dictionary with keys like "Voyager_CR348" and DataFrame values
    """
    sailing_data = {}
    
    for filename in os.listdir(data_dir):
#         print(filename)
        if filename.endswith(".csv"):
            try:
                # Extract ship and sailing number from filename (format: ShipName_SailingNumber.csv)
#                 print(os.path.splitext(filename))
#                 print(os.path.splitext(filename)[0].split("-"))
                ship = os.path.splitext(filename)[0].split("-")[0].strip()
                sailing = "1"
                key = f"{ship}_{sailing}"
                key = key.lower()
                
                # Load CSV and store in dictionary
                df = pd.read_csv(os.path.join(data_dir, filename))
                sailing_data[key] = df
                
                print(f"Loaded data for {ship} {sailing} with {len(df)} records")
            except Exception as e:
                print(f"Error loading {os.path.join(data_dir, filename)}: {str(e)}")
    
    return sailing_data

# SD = load_sailing_data()

# def get_sailing_data():
#     return SD