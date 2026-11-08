"""
Database module for Pharmacy POS System.
Handles SQLite database initialization and all CRUD operations.
"""

import sqlite3
import os
from datetime import datetime, timedelta


DB_NAME = "pharmacy.db"


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with required tables and seed data."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            company TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            batch TEXT NOT NULL,
            generic_name TEXT,
            supplier_id INTEGER,
            price REAL NOT NULL DEFAULT 0,
            stock_qty INTEGER NOT NULL DEFAULT 0,
            expiry_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_amount REAL NOT NULL DEFAULT 0,
            sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
            cashier_name TEXT DEFAULT 'Admin'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)

    conn.commit()
    conn.close()


# ==================== Supplier Operations ====================

def add_supplier(name, contact, company):
    """Add a new supplier."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO suppliers (name, contact, company) VALUES (?, ?, ?)",
        (name, contact, company)
    )
    conn.commit()
    supplier_id = cursor.lastrowid
    conn.close()
    return supplier_id


def get_all_suppliers():
    """Get all suppliers."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_supplier(supplier_id, name, contact, company):
    """Update an existing supplier."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE suppliers SET name=?, contact=?, company=? WHERE id=?",
        (name, contact, company, supplier_id)
    )
    conn.commit()
    conn.close()


def delete_supplier(supplier_id):
    """Delete a supplier."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
    conn.commit()
    conn.close()


# ==================== Medicine Operations ====================

def add_medicine(name, batch, generic_name, supplier_id, price, stock_qty, expiry_date):
    """Add a new medicine."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO medicines 
           (name, batch, generic_name, supplier_id, price, stock_qty, expiry_date) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, batch, generic_name, supplier_id, price, stock_qty, expiry_date)
    )
    conn.commit()
    medicine_id = cursor.lastrowid
    conn.close()
    return medicine_id


def get_all_medicines():
    """Get all medicines with supplier info."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.*, s.name as supplier_name 
        FROM medicines m 
        LEFT JOIN suppliers s ON m.supplier_id = s.id 
        ORDER BY m.name
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_medicine_by_id(medicine_id):
    """Get a single medicine by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines WHERE id=?", (medicine_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_medicine(medicine_id, name, batch, generic_name, supplier_id, price, stock_qty, expiry_date):
    """Update an existing medicine."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE medicines 
           SET name=?, batch=?, generic_name=?, supplier_id=?, price=?, stock_qty=?, expiry_date=? 
           WHERE id=?""",
        (name, batch, generic_name, supplier_id, price, stock_qty, expiry_date, medicine_id)
    )
    conn.commit()
    conn.close()


def delete_medicine(medicine_id):
    """Delete a medicine."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE id=?", (medicine_id,))
    conn.commit()
    conn.close()


def search_medicines(query):
    """Search medicines by name, batch, or generic name."""
    conn = get_connection()
    cursor = conn.cursor()
    search_term = f"%{query}%"
    cursor.execute("""
        SELECT m.*, s.name as supplier_name 
        FROM medicines m 
        LEFT JOIN suppliers s ON m.supplier_id = s.id 
        WHERE m.name LIKE ? OR m.batch LIKE ? OR m.generic_name LIKE ?
        ORDER BY m.name
    """, (search_term, search_term, search_term))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def reduce_stock(medicine_id, quantity):
    """Reduce stock quantity after a sale."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE medicines SET stock_qty = stock_qty - ? WHERE id=? AND stock_qty >= ?",
        (quantity, medicine_id, quantity)
    )
    conn.commit()
    changes = cursor.rowcount
    conn.close()
    return changes > 0


def get_low_stock_medicines(threshold=10):
    """Get medicines with stock below threshold."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.*, s.name as supplier_name 
        FROM medicines m 
        LEFT JOIN suppliers s ON m.supplier_id = s.id 
        WHERE m.stock_qty <= ?
        ORDER BY m.stock_qty ASC
    """, (threshold,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_expiring_medicines(days=30):
    """Get medicines expiring within specified days."""
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date()
    future_date = today + timedelta(days=days)
    cursor.execute("""
        SELECT m.*, s.name as supplier_name 
        FROM medicines m 
        LEFT JOIN suppliers s ON m.supplier_id = s.id 
        WHERE m.expiry_date IS NOT NULL 
          AND date(m.expiry_date) <= ? 
          AND date(m.expiry_date) >= ?
        ORDER BY m.expiry_date ASC
    """, (future_date.isoformat(), today.isoformat()))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_expired_medicines():
    """Get medicines that have already expired."""
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date().isoformat()
    cursor.execute("""
        SELECT m.*, s.name as supplier_name 
        FROM medicines m 
        LEFT JOIN suppliers s ON m.supplier_id = s.id 
        WHERE m.expiry_date IS NOT NULL AND date(m.expiry_date) < ?
        ORDER BY m.expiry_date ASC
    """, (today,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ==================== Sales Operations ====================

def add_sale(total_amount, cashier_name="Admin"):
    """Record a new sale and return the sale ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sales (total_amount, cashier_name) VALUES (?, ?)",
        (total_amount, cashier_name)
    )
    conn.commit()
    sale_id = cursor.lastrowid
    conn.close()
    return sale_id


def add_sale_item(sale_id, medicine_id, quantity, unit_price, total_price):
    """Add an item to a sale."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, total_price) 
           VALUES (?, ?, ?, ?, ?)""",
        (sale_id, medicine_id, quantity, unit_price, total_price)
    )
    conn.commit()
    conn.close()


def get_all_sales():
    """Get all sales records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales ORDER BY sale_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_sale_items(sale_id):
    """Get items for a specific sale with medicine details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT si.*, m.name as medicine_name 
        FROM sale_items si 
        JOIN medicines m ON si.medicine_id = m.id 
        WHERE si.sale_id=?
    """, (sale_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_total_sales():
    """Get total sales amount."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) as total FROM sales")
    row = cursor.fetchone()
    conn.close()
    return row["total"] if row else 0


def get_today_sales():
    """Get today's sales amount."""
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date().isoformat()
    cursor.execute(
        "SELECT COALESCE(SUM(total_amount), 0) as total FROM sales WHERE date(sale_date)=?",
        (today,)
    )
    row = cursor.fetchone()
    conn.close()
    return row["total"] if row else 0