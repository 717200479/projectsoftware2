# model.py
import sqlite3
import hashlib
import logging

# Configure logging to file
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE,
            credit REAL DEFAULT 0,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_username(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, email, phone, credit FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def get_services_by_brand(brand):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, description, price, requirements FROM services WHERE brand = ?', (brand,))
    services = cursor.fetchall()
    conn.close()
    return services

def add_user(username, password, email, phone, is_admin=False):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, email, phone, is_admin) VALUES (?, ?, ?, ?, ?)', 
                   (username, password, email, phone, is_admin))
    conn.commit()
    conn.close()

def update_user_credit(user_id, credit):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET credit = credit + ? WHERE id = ?', (credit, user_id))
    conn.commit()
    conn.close()

def add_service(brand, name, price, description, requirements):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO services (brand, name, price, description, requirements) VALUES (?, ?, ?, ?, ?)', 
                   (brand, name, price, description, requirements))
    conn.commit()
    conn.close()

def delete_service(service_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
    conn.commit()
    conn.close()

def update_service(service_id, brand, name, price, description, requirements):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE services SET brand = ?, name = ?, price = ?, description = ?, requirements = ? WHERE id = ?',
                   (brand, name, price, description, requirements, service_id))
    conn.commit()
    conn.close()

def get_all_services():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services')
    services = cursor.fetchall()
    conn.close()
    return services
# model.py
def get_user_by_id(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, email, phone, credit FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user