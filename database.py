# database.py
import os
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from typing import List, Optional, Dict
from models import Product, Order, OrderItem, OrderStatus, User, UserRole, CartItem

def get_database_url():
    if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
        return st.secrets['DATABASE_URL']
    load_dotenv()
    return os.getenv('DATABASE_URL')

class DatabaseManager:
    def __init__(self):
        self.database_url = get_database_url()
        if not self.database_url:
            import streamlit as st
            st.error("⚠️ Database not configured!")
            st.info("""
            **To set up your database:**
            
            1. Create a PostgreSQL database in Replit (Tools > Database)
            2. Add your DATABASE_URL to `.streamlit/secrets.toml`:
               ```
               DATABASE_URL = "your_postgresql_url_here"
               ```
            3. Restart the app
            
            Or use Replit's Secrets (Tools > Secrets) to add DATABASE_URL
            """)
            st.stop()
        self.init_database()

    def get_connection(self):
        return psycopg2.connect(self.database_url)

    def init_database(self):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY, username VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL, role VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );""")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, description TEXT,
                        price DECIMAL(10, 2) NOT NULL, stock_quantity INTEGER NOT NULL DEFAULT 0,
                        category VARCHAR(100), low_stock_threshold INTEGER DEFAULT 10
                    );""")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id SERIAL PRIMARY KEY, username VARCHAR(255) NOT NULL, status VARCHAR(50) NOT NULL,
                        total_amount DECIMAL(10, 2) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );""")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS order_items (
                        id SERIAL PRIMARY KEY, order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                        product_id INTEGER, product_name VARCHAR(255), quantity INTEGER,
                        unit_price DECIMAL(10, 2)
                    );""")
                # A simple cart implementation using a session state is often better for Streamlit
                # But a DB-backed cart allows it to persist across sessions
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS shopping_cart (
                        id SERIAL PRIMARY KEY, username VARCHAR(255) NOT NULL,
                        product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                        quantity INTEGER NOT NULL, UNIQUE(username, product_id)
                    );""")
            conn.commit()
        print("Database tables initialized.")

    def get_all_products(self) -> List[Product]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, name, description, price, stock_quantity, category, low_stock_threshold
                    FROM products ORDER BY name
                """)
                products = []
                for row in cursor.fetchall():
                    products.append(Product(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        price=float(row['price']),
                        stock_quantity=row['stock_quantity'],
                        category=row['category'],
                        low_stock_threshold=row['low_stock_threshold'],
                        sku=None
                    ))
                return products

    def get_all_orders(self) -> List[Order]:
        orders = []
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
                orders_data = cursor.fetchall()
                for o_data in orders_data:
                    items = self.get_order_items(o_data['id'])
                    order_dict = dict(o_data)
                    status_str = order_dict.pop('status')
                    orders.append(Order(status=OrderStatus(status_str), items=items, **order_dict))
        return orders
    
    def get_order_items(self, order_id: int) -> List[OrderItem]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT product_id, product_name, quantity, unit_price FROM order_items WHERE order_id = %s", (order_id,))
                return [OrderItem(**item) for item in cursor.fetchall()]
    
    def update_order_status(self, order_id: int, new_status: OrderStatus) -> bool:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("UPDATE orders SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (new_status.value, order_id))
                    conn.commit()
                    return cursor.rowcount > 0
                except:
                    conn.rollback()
                    return False

    def add_product(self, name: str, price: float, stock: int, desc: str, category: str) -> bool:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        "INSERT INTO products (name, description, price, stock_quantity, category) VALUES (%s, %s, %s, %s, %s)",
                        (name, desc, price, stock, category)
                    )
                    conn.commit()
                    return True
                except:
                    conn.rollback()
                    return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def create_user(self, username: str, password_hash: str, role: str) -> bool:
        """Create a new user"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                        (username, password_hash, role)
                    )
                    conn.commit()
                    return True
                except:
                    conn.rollback()
                    return False
