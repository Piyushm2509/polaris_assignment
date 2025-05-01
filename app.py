from flask import Flask, render_template
from routes.user_routes import user_routes
from routes.rider_routes import rider_routes
from routes.restaurant_routes import restaurant_routes
from routes.order_routes import order_routes
from routes.notification_routes import notification_routes
from db import init_db

app = Flask(__name__)

# Register Blueprints for API routes
app.register_blueprint(user_routes)
app.register_blueprint(rider_routes)
app.register_blueprint(restaurant_routes)
app.register_blueprint(order_routes)
app.register_blueprint(notification_routes)

# Initialize database
init_db()

# Web UI Routes
@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/register_user')
def register_user_page():
    """Render the user registration page."""
    return render_template('register_user.html')

@app.route('/register_rider')
def register_rider_page():
    """Render the rider registration page."""
    return render_template('register_rider.html')

@app.route('/register_restaurant')
def register_restaurant_page():
    """Render the restaurant registration page."""
    return render_template('register_restaurant.html')

@app.route('/suggest_restaurants')
def suggest_restaurants_page():
    """Render the restaurant suggestion page."""
    return render_template('suggest_restaurants.html')

@app.route('/view_menu')
def view_menu_page():
    """Render the menu viewing page."""
    return render_template('view_menu.html')

@app.route('/place_order')
def place_order_page():
    """Render the order placement page."""
    return render_template('place_order.html')

@app.route('/assign_rider')
def assign_rider_page():
    """Render the rider assignment page."""
    return render_template('assign_rider.html')

@app.route('/update_rider_location')
def update_rider_location_page():
    """Render the rider location update page."""
    return render_template('update_rider_location.html')

@app.route('/user_orders')
def user_orders_page():
    """Render the user order history page."""
    return render_template('user_orders.html')

@app.route('/rider_orders')
def rider_orders_page():
    """Render the rider order history page."""
    return render_template('rider_orders.html')

@app.route('/completed_orders')
def completed_orders_page():
    """Render the completed orders page."""
    return render_template('completed_orders.html')

@app.route('/users')
def all_users_page():
    return render_template('users.html')

@app.route('/riders')
def all_riders_page():
    return render_template('riders.html')

@app.route('/restaurants')
def all_restaurants_page():
    return render_template('restaurants.html')

if __name__ == '__main__':
    app.run(debug=True)