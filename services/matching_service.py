from db import db_cursor
from utils import calculate_distance, estimate_delivery_time
from models.restaurant import Restaurant
from models.rider import Rider

class MatchingService:
    """Service to handle restaurant suggestions and rider assignment."""
    
    @staticmethod
    def suggest_restaurants(user_location: str, food_type: str, max_delivery_time: int) -> list:
        """
        Suggest restaurants based on food type and delivery time.
        
        Args:
            user_location (str): User's location (e.g., 'Downtown')
            food_type (str): Desired food type (e.g., 'Italian')
            max_delivery_time (int): Maximum delivery time in minutes
            
        Returns:
            list: List of restaurant dictionaries with estimated delivery time
        """
        if not user_location or not food_type or max_delivery_time <= 0:
            raise ValueError("User location, food type, and valid delivery time are required")
            
        suggestions = []
        with db_cursor() as cursor:
            cursor.execute(
                "SELECT restaurant_id, name, location, food_type, prep_time FROM restaurants WHERE food_type = ?",
                (food_type,)
            )
            restaurants = cursor.fetchall()
            
            for restaurant in restaurants:
                delivery_time = estimate_delivery_time(restaurant['location'], user_location, restaurant['prep_time'])
                if delivery_time <= max_delivery_time:
                    suggestions.append({
                        "restaurant_id": restaurant['restaurant_id'],
                        "name": restaurant['name'],
                        "location": restaurant['location'],
                        "food_type": restaurant['food_type'],
                        "estimated_delivery_time": delivery_time
                    })
        
        # Sort by estimated delivery time
        return sorted(suggestions, key=lambda x: x['estimated_delivery_time'])
    
    @staticmethod
    def find_nearest_rider(restaurant_location: str) -> dict:
        """
        Find the nearest available rider to the restaurant.
        
        Args:
            restaurant_location (str): Restaurant's location
            
        Returns:
            dict: Rider details (rider_id, name, location) or None if no rider available
        """
        with db_cursor() as cursor:
            cursor.execute(
                "SELECT rider_id, name, location FROM riders WHERE is_available = ?",
                (True,)
            )
            riders = cursor.fetchall()
            
            if not riders:
                return None
                
            # Find rider with minimum distance to restaurant
            min_distance = float('inf')
            nearest_rider = None
            for rider in riders:
                distance = calculate_distance(restaurant_location, rider['location'])
                if distance < min_distance:
                    min_distance = distance
                    nearest_rider = {
                        "rider_id": rider['rider_id'],
                        "name": rider['name'],
                        "location": rider['location']
                    }
            
            return nearest_rider