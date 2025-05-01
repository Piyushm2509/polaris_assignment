from contextlib import contextmanager
import sqlite3

@contextmanager
def db_cursor():
    conn = sqlite3.connect('food_delivery.db')
    conn.row_factory = sqlite3.Row  # Set BEFORE creating the cursor!
    cursor = conn.cursor()

    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def init_db():
    """
    Initialize the SQLite database with required tables.
    """
    try:
        with sqlite3.connect('food_delivery.db') as conn:
            cursor = conn.cursor()

            # Optional: enable column access by name
            conn.row_factory = sqlite3.Row

            # Drop old restaurants table if exists (to remove food_type)
            cursor.execute('DROP TABLE IF EXISTS restaurants')

            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL
                )
            ''')

            # Create riders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS riders (
                    rider_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    is_available BOOLEAN DEFAULT TRUE
                )
            ''')

            # Create updated restaurants table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS restaurants (
                    restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    food_type TEXT DEFAULT 'Mixed',
                    prep_time INTEGER DEFAULT 10
                )
            ''')

            # Create menus table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menus (
                    menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    restaurant_id INTEGER,
                    item_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
                )
            ''')

            # Create orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    restaurant_id INTEGER,
                    rider_id INTEGER,
                    items TEXT NOT NULL,
                    total_price REAL NOT NULL,
                    status TEXT DEFAULT 'placed',
                    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id),
                    FOREIGN KEY (rider_id) REFERENCES riders (rider_id)
                )
            ''')

            # Create notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    order_id INTEGER,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (order_id) REFERENCES orders (order_id)
                )
            ''')

            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_rider_id ON orders (rider_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_menus_restaurant_id ON menus (restaurant_id)')

            conn.commit()
            print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")