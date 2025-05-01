from flask import Blueprint, request, jsonify, render_template
from services.matching_service import MatchingService
from services.order_service import OrderService
from models.order import Order
from models.restaurant import Restaurant

order_routes = Blueprint('order_routes', __name__)
def format_order_details(order):
    return {
        'order_id': order.order_id,
        'user_id': order.user_id,
        'restaurant_id': order.restaurant_id,
        'rider_id': order.rider_id,
        'items': order.items,
        'total_price': order.total_price,
        'status': order.status,
        'order_time': order.order_time.strftime('%Y-%m-%d %H:%M:%S') if order.order_time else None
    }

@order_routes.route('/suggest_restaurants', methods=['POST'])
def suggest_restaurants():
    """
    Suggest restaurants based on food type and delivery time.
    
    Request Body:
        - user_location (str): User's location (e.g., 'Downtown')
        - food_type (str): Desired food type (e.g., 'Italian')
        - max_delivery_time (int): Maximum delivery time in minutes
    
    Returns:
        JSON: List of suggested restaurants with details
    """
    try:
        data = request.get_json()
        if not data or 'user_location' not in data or 'food_type' not in data or 'max_delivery_time' not in data:
            return jsonify({"error": "User location, food type, and max delivery time are required"}), 400
            
        suggestions = MatchingService.suggest_restaurants(
            data['user_location'], data['food_type'], data['max_delivery_time']
        )
        return jsonify({"restaurants": suggestions}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@order_routes.route('/place_order', methods=['POST'])
def place_order():
    """
    Place an order for a user from a restaurant.
    
    Request Body:
        - user_id (int): User's ID
        - restaurant_id (int): Restaurant's ID
        - item_ids (list): List of menu item IDs to order
    
    Returns:
        JSON: Order details or error message
    """
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'restaurant_id' not in data or 'item_ids' not in data:
            return jsonify({"error": "User ID, restaurant ID, and item IDs are required"}), 400
            
        order_details = OrderService.place_order(
            data['user_id'], data['restaurant_id'], data['item_ids']
        )
        return jsonify({
            "message": "Order placed successfully",
            "order": order_details
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@order_routes.route('/assign_rider/<int:order_id>', methods=['POST'])
def assign_rider(order_id):
    """
    Assign a rider to an order.
    
    Path Parameters:
        - order_id (int): Order's ID
    
    Returns:
        JSON: Rider assignment details or error message
    """
    try:
        order = Order.get_by_id(order_id)  # Fix: Use get_by_id
        if not order:
            return jsonify({"error": "Order not found"}), 404
            
        restaurant = Restaurant.get_by_id(order.restaurant_id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
            
        rider = MatchingService.find_nearest_rider(restaurant.location)
        if not rider:
            return jsonify({"message": "No rider available"}), 200
            
        if Order.assign_rider(order_id, rider['rider_id']):
            return jsonify({
                "message": "Rider assigned successfully",
                "rider_id": rider['rider_id']
            }), 200
        else:
            return jsonify({"error": "Failed to assign rider"}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500    
@order_routes.route('/api/completed_orders', methods=['GET'])
def get_completed_orders():
    """
    Get all completed orders for a user.
    
    Query Parameter:
        - user_id (int): User's ID
    
    Returns:
        JSON: List of completed orders
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        all_orders = Order.get_user_orders(user_id)
        completed_orders = [
            {
                "order_id": order.order_id,
                "restaurant_name": Restaurant.get_by_id(order.restaurant_id).name if Restaurant.get_by_id(order.restaurant_id) else "Unknown",
                "items": order.items,
                "total_price": order.total_price,
                "status": order.status,
                "order_time": order.order_time
            }
            for order in all_orders if order.status == 'completed'
        ]
        formatted_orders = [format_order_details(order) for order in completed_orders]

        return jsonify({
            "user_id": user_id,
            "orders": formatted_orders
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500