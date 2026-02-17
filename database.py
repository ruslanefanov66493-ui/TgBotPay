import sqlite3
from datetime import datetime, timedelta
from config import config

def get_db_connection():
    conn = sqlite3.connect('bot_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            tariff TEXT,
            subscription_end TIMESTAMP,
            is_active BOOLEAN DEFAULT 0,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            currency TEXT,
            tariff TEXT,
            payment_id TEXT UNIQUE,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username, full_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)',
        (user_id, username, full_name)
    )
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def activate_subscription(user_id, tariff):
    end_date = datetime.now() + timedelta(days=config.SUBSCRIPTION_DAYS)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET tariff = ?, subscription_end = ?, is_active = 1 WHERE user_id = ?',
        (tariff, end_date, user_id)
    )
    conn.commit()
    conn.close()

def check_subscription(user_id):
    user = get_user(user_id)
    if user and user['is_active']:
        end_date = datetime.fromisoformat(user['subscription_end'])
        if end_date > datetime.now():
            return True
    return False

def save_payment(user_id, amount, currency, tariff, payment_id, status='pending'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO payments (user_id, amount, currency, tariff, payment_id, status) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, amount, currency, tariff, payment_id, status)
    )
    conn.commit()
    conn.close()

def update_payment_status(payment_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE payments SET status = ? WHERE payment_id = ?',
        (status, payment_id)
    )
    conn.commit()
    conn.close()