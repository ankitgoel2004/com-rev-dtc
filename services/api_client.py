import requests
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import json
import yaml
from pathlib import Path

@dataclass
class SailingIdentifier:
    ship_name: str
    sailing_number: str

class APIClient:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update(self.config["api"]["headers"])
        self.session.timeout = self.config["api"]["timeout"]

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
        
    def _configure_session(self):
        self.session.headers.update(self.config["api"]["headers"])
        self.session.timeout = self.config["api"]["timeout"]

    def authenticate(self, username: str, password: str) -> bool:
        endpoint = self.config["api"]["endpoints"]["auth"]
        try:
            response = self.session.post(
                f"{self.config['api']['base_url']}/{endpoint}",
                json={"username": username, "password": password}
            )
            return response.json().get("authenticated", False)
        except Exception:
            return False
        
    def get_available_ships(self) -> List[str]:
        """Fetch available ships from API"""
        endpoint = self.config["api"]["endpoints"]["get_ships"]
        response = self._make_request("GET", endpoint)
        return [ship["name"] for ship in response.get("data", [])]
    
    def get_valid_metrics(self) -> List[str]:
        """Get list of valid metrics from config"""
        return self.config["metrics"]["attributes"]

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generic request handler with enhanced error handling"""
        url = f"{self.config['api']['base_url']}/{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers or {},
                timeout=10
            )
            response.raise_for_status()
            # print(response.json())
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception("API request timed out")
        except requests.exceptions.RequestException as e:
            error_msg = f"API request to {endpoint} failed: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f" | Status: {e.response.status_code}"
                try:
                    error_details = e.response.json()
                    error_msg += f" | Details: {error_details.get('message', 'No details')}"
                except ValueError:
                    error_msg += f" | Response: {e.response.text[:200]}"
            raise Exception(error_msg)

    def get_rating_summary(
        self,
        sailings: List[SailingIdentifier],
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get rating summaries for multiple sailings
        
        Args:
            sailings: List of sailing identifiers (ship_name + sailing_number)
            from_date: Optional start date filter (YYYY-MM-DD)
            to_date: Optional end date filter (YYYY-MM-DD)
            
        Returns:
            List of rating summaries in the format matching the 'data' structure provided
        """
        endpoint = self.config["api"]["endpoints"]["get_ratings"]
        
        # Prepare request payload
        payload = {
            "sailings": [{"shipName": s.ship_name, "sailingNumber": s.sailing_number} for s in sailings],
            "filters": {}
        }
        
        if from_date:
            payload["filters"]["fromDate"] = from_date
        if to_date:
            payload["filters"]["toDate"] = to_date
            
        try:
            response = self._make_request("POST", endpoint, data=payload)
            # print(response.get("data"))
            return response.get("data")
            # return self._map_rating_summary(response)
        except Exception as e:
            raise Exception(f"Failed to get rating summary: {str(e)}")
        
# unused
    # def _map_rating_summary(self, raw_data: Dict) -> List[Dict[str, Any]]:
    #     """
    #     Map rating summary API response using global METRIC_ATTRIBUTES
    #     """
    #     if not isinstance(raw_data.get("data"), list):
    #         raise ValueError("Unexpected API response format: missing 'data' list")
        
    #     mapped_data = []
        
    #     for item in raw_data["data"]:
    #         # Start with mandatory fields
    #         mapped_item = {
    #             "Sailing Number": item.get("sailingNumber"),
    #             "Ship Name": item.get("shipName")
    #         }
            
    #         # Add all metrics from our global set
    #         for attr in self.metric_attributes:
    #             api_field_name = self._attribute_to_api_field(attr)
    #             mapped_item[attr] = item.get(api_field_name)
            
    #         # Clean None values
    #         mapped_item = {k: v for k, v in mapped_item.items() if v is not None}
    #         mapped_data.append(mapped_item)
            
    #     return mapped_data

    def get_metric_rating(
        self,
        sailings: List[SailingIdentifier],
        metric: str,
        filter_below: Optional[float] = None,
        compare_to_average: bool = False
    ) -> Dict:
        """
        Get and compare metric ratings across multiple sailings
        
        Args:
            sailings: List of sailing identifiers
            metric: Metric to compare (e.g., "F&B quality overall")
            filter_below: Optional threshold to filter low ratings
            compare_to_average: Whether to include comparison to overall average
            
        Returns:
            Dictionary with comparison results and filtered reviews
            Example:
            {
                "metric": "F&B quality overall",
                "results": [
                    {
                        "ship": "Voyager",
                        "sailingNumber": "CR348",
                        "averageRating": 4.2,
                        "filteredReviews": ["The food was..."],
                        "comparisonToOverall": -0.8
                    },
                    ...
                ]
            }
        """
        endpoint = self.config["api"]["endpoints"]["get_metric_ratings"]
        
        
        if metric not in self.get_valid_metrics():
            raise ValueError(f"Invalid metric attribute. Must be one of: {self.get_valid_metrics}")
        
        payload = {
            "sailings": [{"shipName": s.ship_name, "sailingNumber": s.sailing_number} for s in sailings],
            "metric": metric,
            "filterBelow": filter_below,
            "compareToAverage": compare_to_average
        }
        
        try:
            response = self._make_request("POST", endpoint, data=payload)
            # print(response)
            return self._check_metric_response(response)
        except Exception as e:
            raise Exception(f"Failed to get metric ratings: {str(e)}")

# unused
    # def _map_metric_rating(
    #     self,
    #     raw_data: Dict,
    #     metric_attribute: str,
    #     filter_value: Optional[float] = None
    # ) -> List[Tuple[str, str, str, List[str]]]:
    #     """
    #     Map API response to include filtered reviews
        
    #     Returns:
    #         List of tuples:
    #         (ship_name, sailing_number, metric_value, [filtered_review_excerpts])
    #     """
    #     if not isinstance(raw_data.get("data"), list):
    #         raise ValueError("Unexpected API response format")
        
    #     mapped_data = []
        
    #     for item in raw_data["data"]:
    #         try:
    #             ship = str(item["shipName"])
    #             sailing = str(item["sailingNumber"])
    #             value = float(item["metrics"].get(metric_attribute, 0))
                
    #             # Get all reviews where this metric is below filter threshold
    #             filtered_reviews = []
    #             if filter_value is not None and value < filter_value:
    #                 reviews = item.get("reviews", [])
    #                 for review in reviews:
    #                     if isinstance(review, str):
    #                         filtered_reviews.append(review[:500])  # Return first 500 chars
    #                     elif isinstance(review, dict):
    #                         filtered_reviews.append(review.get("text", "")[:500])
                
    #             mapped_data.append((
    #                 ship,
    #                 sailing,
    #                 str(value),
    #                 filtered_reviews
    #             ))
    #         except (KeyError, ValueError) as e:
    #             continue
        
    #     return mapped_data
    
    def get_metric_comparison(
        self,
        sailings: List[SailingIdentifier],
        metrics: List[str],
        filter_below: Optional[float] = None
    ) -> Dict:
        """
        Compare multiple metrics across sailings
        
        Args:
            sailings: List of sailing identifiers
            metrics: List of metrics to compare
            filter_below: Optional threshold for filtering
            
        Returns:
            Dictionary with comparison results for all metrics
            Example:
            {
                "comparisons": [
                    {
                        "metric": "F&B quality overall",
                        "results": [...]
                    },
                    {
                        "metric": "Cabin cleanliness",
                        "results": [...]
                    }
                ]
            }
        """
        comparisons = []
        
        for metric in metrics:
            try:
                result = self.get_metric_rating(
                    sailings=sailings,
                    metric=metric,
                    filter_below=filter_below,
                    compare_to_average=True
                )
                comparisons.append(result)
            except Exception as e:
                comparisons.append({
                    "metric": metric,
                    "error": str(e)
                })
        
        return {"comparisons": comparisons}

    def _check_metric_response(self, response: Dict) -> Dict:
        """Process and validate metric rating response"""
        if not isinstance(response, dict):
            raise ValueError("Invalid API response format")
        
        required_keys = {"status", "metric", "results"}
        if not all(key in response for key in required_keys):
            raise ValueError("Missing required fields in API response")
        
        if response["status"] != "success":
            raise ValueError(f"API request failed: {response.get('error', 'Unknown error')}")
        
        return {
            "metric": response["metric"],
            "filterBelow": response.get("filterBelow"),
            "results": [
                self._process_sailing_result(r)
                for r in response["results"]
            ]
        }


    def _process_sailing_result(self, result: Dict) -> Dict:
        """Process individual sailing result"""
        processed = {
            "ship": result.get("ship"),
            "sailingNumber": result.get("sailingNumber"),
            "averageRating": result.get("averageRating"),
            "ratingCount": result.get("ratingCount", 0),
            "filteredReviews": result.get("filteredReviews", []),
            "filteredMetric": result.get("filteredMetric", []),
            "filteredCount": result.get("filteredCount", 0)
        }
        
        if "comparisonToOverall" in result:
            processed["comparisonToOverall"] = result["comparisonToOverall"]
        
        if "error" in result:
            processed["error"] = result["error"]
        
        return processed

    
    @staticmethod
    def _attribute_to_api_field(attribute: str) -> str:
        """
        Convert display attribute name to API field name
        Example: "Holiday and Ship Experience" → "holidayExperienceScore"
        """
        # Add your conversion logic here
        conversions = {
            'Holiday and Ship Experience': 'holidayExperienceScore',
            'Cabins': 'cabinScore',
            'F&B Quality Overall': 'fbQualityOverall',
            'F&B Service Overall': 'fbServiceOverall',
            'F&B Quality Main Dining': 'fbQualityMainDining',
            'Entertainment': 'entertainmentScore',
            'Excursions': 'excursionScore',
            'Sentiment Analysis': 'sentimentScore',
            'Bar Service': 'barServiceScore',
            'Cabin Cleanliness': 'cabinCleanlinessScore',
            'Crew Friendliness': 'crewFriendlinessScore',
            'Drinks Offerings': 'drinksScore',
            'App Booking': 'appScore',
            'Flight': 'flightScore',
            'Hotel Accommodation': 'hotelScore',
            'Prior Customer Care': 'customerCareScore'
        }
        return conversions.get(attribute, attribute.lower().replace(" ", ""))

# Example usage
if __name__ == "__main__":
    client = APIClient()
    
    # Example sailings to query
    sailings = [
        SailingIdentifier(ship_name="Ocean Queen", sailing_number="CR330"),
        SailingIdentifier(ship_name="Ocean Queen", sailing_number="CR343"),
        SailingIdentifier(ship_name="Voyager", sailing_number="CR351")
    ]

    sailings_metric = [
        SailingIdentifier(ship_name="EXPLORER", sailing_number="1"),
        SailingIdentifier(ship_name="DISCOVERY 2", sailing_number="1"),
        SailingIdentifier(ship_name="DISCOVERY", sailing_number="1")
    ]
    
    try:
        # Get full rating summaries
        # print("Getting rating summaries...")
        summaries = client.get_rating_summary(sailings)
        print(f"Got {len(summaries)} rating summaries")
        # print(summaries)
        print(json.dumps(summaries, indent=2))
        
        # Get specific metric
        print("\nGetting cabin ratings...")
        metric_filter = client.get_metric_rating(
            sailings=sailings_metric,
            metric="Ship rooms",
            filter_below=5.0,
            compare_to_average=True
        )
        print("Cabin ratings:")
        print(json.dumps(metric_filter, indent=2))

        # Multi-metric comparison
        print("\nMulti-metric comparison:")
        comparison = client.get_metric_comparison(
            sailings=sailings_metric,
            metrics=["F&B quality overall", "F&B service overall"],
            filter_below=5.0
        )
        print(json.dumps(comparison, indent=2))
        # with open("metric_filter.json", "w") as f:
        #     json.dump(metric_filter, f)
        with open("comp.json", "w") as f:
            json.dump(comparison, f)
            
    except Exception as e:
        print(f"API Error: {e}")