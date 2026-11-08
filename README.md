# Pharmacy POS & Inventory Management System

A complete desktop-based Pharmacy Point of Sale and Inventory Management Software built with Python, Tkinter, and SQLite.

## Features

1. **Dashboard** - Quick stats: Total Sales, Expiring Soon (30 days), Low Stock items
2. **Medicine Inventory Management** - Add, edit, delete medicines with Name, Batch, Generic Name, Supplier, Price, Stock Qty, Expiry Date
3. **Expiry Date Tracker** - Track medicines expiring within 30 or 60 days, with color-coded alerts
4. **Supplier Management** - Manage suppliers with Name, Contact, Company details
5. **POS Billing** - Search medicines, add to cart, calculate total, print receipt, auto-reduce stock after sale

## Project Structure

```
PharmacyPOS/
├── .venv/                    # Python virtual environment
├── pharmacy.db               # SQLite database (auto-created)
├── main.py                   # Application entry point
├── database.py               # Database initialization and CRUD operations
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── modules/
    ├── __init__.py
    ├── dashboard.py          # Dashboard with quick stats
    ├── inventory.py          # Medicine inventory management
    ├── expiry.py             # Expiry date tracker
    ├── suppliers.py          # Supplier management
    └── pos_billing.py        # POS billing screen
```

## Setup & Installation

### 1. Create and activate virtual environment

**Windows (PowerShell):**
```powershell
cd e:\PharmacyPOS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
cd e:\PharmacyPOS
python -m venv .venv
.venv\Scripts\activate.bat
```

### 2. Run the application

```powershell
python main.py
```

## Database

The application uses SQLite (`pharmacy.db`) which is created automatically on first run. No additional database setup is required.

## Screenshots / Usage

- **Dashboard**: View total sales, expiring medicines, and low stock alerts at a glance
- **Inventory**: Add medicines with batch numbers, generic names, supplier info, prices, and stock levels
- **Expiry Tracker**: Filter medicines expiring within 30/60 days or already expired (color-coded: red for expired, yellow for expiring soon)
- **Suppliers**: Maintain a list of medicine suppliers with contact details
- **POS Billing**: Search medicines by name/batch/generic name, add to cart, checkout, and automatically reduce stock

## Technologies

- Python 3.x (Tkinter for GUI, SQLite for database)
- No external dependencies required
