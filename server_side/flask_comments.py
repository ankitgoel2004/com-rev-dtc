from flask import Flask, request, jsonify
from typing import Dict, List
from test_data import get_summary_data, load_sailing_data
import pandas as pd
import yaml
from werkzeug.security import check_password_hash
from pathlib import Path

app = Flask(__name__)

METRIC_ATTRIBUTES = ['Ship overall', 'Ship rooms', 'F&B quality overall',
       'F&B service overall', 'F&B quality main dining', 'Entertainment',
       'Excursions', 'drinks offerings', 'bar service', 'cabin cleanliness',
       'crew friendliness', 'Sentiment analysis', 'Primary issues mentioned',
       'Review']

# Sample data matching your structure
SAMPLE_DATA = get_summary_data()
# print(SAMPLE_DATA)
AUTH_FILE = Path("sailing_auth.yaml")
def load_auth_data():
    """Load authentication data from YAML file"""
    if not AUTH_FILE.exists():
        raise FileNotFoundError(f"Auth file not found at {AUTH_FILE}")
    
    with open(AUTH_FILE, 'r') as f:
        return yaml.safe_load(f)


SAILING_DATA: Dict[str, pd.DataFrame] = load_sailing_data()
# print(SAILING_DATA)
def get_sailing_df(ship: str, sailing_number: str):
    """Helper to get DataFrame for specific sailing"""
    key = f"{ship}_{sailing_number}"
    key = key.lower()
    return SAILING_DATA.get(key)

# Helper functions
def generate_rating_text(score: float, attribute: str) -> str:
    """Generate realistic rating text based on score"""
    if score >= 8:
        return f"Exceptional {attribute.lower()} experience. Guests rated this {score:.1f}/10"
    elif score >= 6:
        return f"Positive {attribute.lower()} feedback with {score:.1f} rating. Most guests were satisfied"
    elif score >= 4:
        return f"Average {attribute.lower()} rating of {score:.1f}. Some room for improvement"
    else:
        return f"Critical feedback on {attribute.lower()} ({score:.1f}). Needs immediate attention"

def find_sailings(sailings: List[Dict]) -> List[Dict]:
    """Filter sample data based on requested sailings"""
    results = []
    for sailing in sailings:
        ship = sailing.get("shipName")
        number = sailing.get("sailingNumber")
        found = next(
            (item for item in SAMPLE_DATA 
             if item["Ship Name"].lower() == ship.lower() and item["Sailing Number"].lower() == number.lower()),
            None
        )
        if found:
            results.append(found)
    return results

# API Endpoints
@app.route('/sailing/getRatingSmry', methods=['POST'])
def get_rating_summary():
    """Endpoint for getting full rating summaries"""
    data = request.get_json()
    
    # Validate input
    if not data or "sailings" not in data:
        return jsonify({"error": "Missing sailings parameter"}), 400
    
    # Get requested sailings
    results = find_sailings(data["sailings"])

    # Apply date filters if provided
    if "filters" in data:
        if "fromDate" in data["filters"]:
            pass  # In a real API, you would filter by date here
        if "toDate" in data["filters"]:
            pass
    
    return jsonify({
        "status": "success",
        "count": len(results),
        "data": results
    })

@app.route('/sailing/getMetricRating', methods=['POST'])
def get_metric_comparison():
    """Enhanced endpoint with metric value filtering"""
    data = request.get_json()
    
    # Validate input
    if not data or "sailings" not in data or "metric" not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    metric = data["metric"]
    sailings = data["sailings"]
    filter_below = data.get("filterBelow")
    compare_avg = data.get("compareToAverage", False)

    # Validate metric (excluding 'Review')
    if metric not in METRIC_ATTRIBUTES:
        return jsonify({
            "error": "Metric must be a numeric field (not 'Review')",
            "valid_metrics": METRIC_ATTRIBUTES
        }), 400
    
    # Prepare response
    results = []
    all_metric_values = []

    for sailing in sailings:
        print("get metric comparison",sailing)
        ship = sailing["shipName"]
        number = sailing["sailingNumber"]
        df = get_sailing_df(ship, number)
        # print(df)
        
        if df is None or metric not in df.columns:
            results.append({
                "ship": ship,
                "sailingNumber": number,
                "error": "Data not found" if df is None else "Invalid metric"
            })
            continue
        
        # Calculate basic stats
        metric_values = pd.to_numeric(df[metric], errors='coerce').dropna()
        avg_rating = metric_values.mean()
        all_metric_values.extend(metric_values.tolist())
        
        # Get filtered reviews if requested
        filtered_reviews = []
        if filter_below is not None:
            mask = df[metric].astype(float) < filter_below
            filtered_reviews = df.loc[mask, "Review"].tolist()
            filtered_metric = df.loc[mask, metric].tolist()
        
        results.append({
            "ship": ship,
            "sailingNumber": number,
            "metric": metric,
            "averageRating": round(avg_rating, 2),
            "ratingCount": len(metric_values),
            "filteredReviews": filtered_reviews,
            "filteredMetric": filtered_metric,
            "filteredCount": len(filtered_reviews)
        })
    
    # Add comparison to overall average if requested
    if compare_avg and all_metric_values:
        overall_avg = sum(all_metric_values) / len(all_metric_values)
        for result in results:
            if "averageRating" in result:
                result["comparisonToOverall"] = round(result["averageRating"] - overall_avg, 2)
    
    return jsonify({
        "status": "success",
        "metric": metric,
        "results": results,
        "filterBelow": filter_below,
        "comparedToAverage": compare_avg
    })

@app.route('/sailing/ships', methods=['GET'])
def get_ships():
    SHIPS = ["Voyager", "Explorer", "Discovery", "Explorer 2", "Discovery 2"]
    return jsonify({
        "status": "success",
        "data": [{"name": ship, "id": idx+1} for idx, ship in enumerate(SHIPS)]
    })
    # """Endpoint for getting available ships from database"""
    # ships = db.query("SELECT ship_id as id, ship_name as name FROM ships")
    # return jsonify({
    #     "status": "success",
    #     "data": ships
    # })


@app.route('/sailing/auth', methods=['POST'])
def authenticate():
    try:
        # Get credentials from request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                "authenticated": False,
                "error": "Username and password required"
            }), 400
        
        # Load auth data
        auth_data = load_auth_data()
        user_data = auth_data['users'].get(username)
        
        # Verify user exists and password matches
        if user_data and check_password_hash(user_data['password'], password):
            return jsonify({
                "authenticated": True,
                "user": username,
                "role": user_data.get('role')
            })
        
        return jsonify({
            "authenticated": False,
            "error": "Invalid credentials"
        }), 401
        
    except Exception as e:
        return jsonify({
            "authenticated": False,
            "error": f"Authentication failed: {str(e)}"
        }), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)