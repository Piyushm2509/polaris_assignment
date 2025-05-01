from flask import Blueprint, request, jsonify
from models.rider import Rider
from models.order import Order
from utils import format_order_details
import logging
from models.restaurant import Restaurant

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

rider_routes = Blueprint('rider_routes', __name__)

@rider_routes.route('/register_rider', methods=['POST'])
def register_rider():
    """
    Register a new rider.
    
    Request Body:
        - name (str): Rider's name
        - location (str): Rider's location (e.g., 'Downtown')
    
    Returns:
        JSON: Rider ID and success message, or error message
    """
    try:
        logger.debug("Received request to register rider")
        data = request.get_json()
        logger.debug(f"Request JSON: {data}")
        
        if not data or 'name' not in data or 'location' not in data:
            logger.warning("Missing name or location in request")
            return jsonify({"error": "Name and location are required"}), 400
            
        rider = Rider.register(data['name'], data['location'])
        logger.info(f"Rider registered successfully: ID={rider.rider_id}")
        return jsonify({
            "rider_id": rider.rider_id,
            "message": "Rider registered successfully"
        }), 201
    except ValueError as e:
        logger.error(f"ValueError in register_rider: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in register_rider: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@rider_routes.route('/update_rider_location', methods=['PUT'])
def update_rider_location():
    """
    Update a rider's location.
    
    Request Body:
        - rider_id (int): Rider's ID
        - location (str): New location
    
    Returns:
        JSON: Success or error message
    """
    try:
        logger.debug("Received request to update rider location")
        data = request.get_json()
        logger.debug(f"Request JSON: {data}")
        
        if not data or 'rider_id' not in data or 'location' not in data:
            logger.warning("Missing rider_id or location in request")
            return jsonify({"error": "Rider ID and location are required"}), 400
            
        rider_id = data['rider_id']
        location = data['location']
        
        if Rider.update_location(rider_id, location):
            logger.info(f"Rider location updated: ID={rider_id}, Location={location}")
            return jsonify({"message": "Rider location updated successfully"}), 200
        else:
            logger.warning(f"Rider not found: ID={rider_id}")
            return jsonify({"error": "Rider not found"}), 404
    except ValueError as e:
        logger.error(f"ValueError in update_rider_location: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in update_rider_location: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@rider_routes.route('/rider/<int:rider_id>/orders', methods=['GET'])
def get_rider_orders(rider_id):
    """
    Fetch order history for a rider.
    
    Path Parameters:
        - rider_id (int): Rider's ID
    
    Returns:
        JSON: List of rider's orders with details
    """
    try:
        logger.debug(f"Fetching orders for rider_id={rider_id}")
        rider = Rider.get_by_id(rider_id)
        if not rider:
            logger.warning(f"Rider not found: rider_id={rider_id}")
            return jsonify({"error": "Rider not found"}), 404
            
        orders = Order.get_rider_orders(rider_id)
        formatted_orders = []
        for order in orders:
            restaurant = Restaurant.get_by_id(order.restaurant_id)
            order_dict = {
                "order_id": order.order_id,
                "restaurant_name": restaurant.name if restaurant else "Unknown",
                "items": order.items,
                "total_price": order.total_price,
                "status": order.status,
                "order_time": order.order_time
            }
            formatted_orders.append(format_order_details(order_dict))
        
        logger.info(f"Retrieved {len(orders)} orders for rider_id={rider_id}")
        return jsonify({
            "rider_id": rider_id,
            "orders": formatted_orders
        }), 200
    except Exception as e:
        logger.error(f"Unexpected error in get_rider_orders: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500