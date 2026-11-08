"""
Expiry Date Tracker module.
Highlights medicines expiring within 30 or 60 days and expired medicines.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import database


class ExpiryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f4f8")
        self.controller = controller
        self.build_ui()
        self.refresh_expiry()

    def build_ui(self):
        # Title
        title = tk.Label(
            self, text="Expiry Date Tracker", font=("Segoe UI", 20, "bold"),
            bg="#f0f4f8", fg="#2c3e50"
        )
        title.pack(pady=(15, 10))

        # Filter options
        filter_frame = tk.LabelFrame(
            self, text="Filter", font=("Segoe UI", 11, "bold"),
            bg="#ffffff", fg="#2c3e50", padx=20, pady=10
        )
        filter_frame.pack(pady=10, padx=40, fill="x")

        self.filter_var = tk.StringVar(value="30")
        tk.Radiobutton(
            filter_frame, text="Expiring within 30 days", variable=self.filter_var,
            value="30", bg="#ffffff", font=("Segoe UI", 10),
            command=self.refresh_expiry
        ).pack(side="left", padx=10)

        tk.Radiobutton(
            filter_frame, text="Expiring within 60 days", variable=self.filter_var,
            value="60", bg="#ffffff", font=("Segoe UI", 10),
            command=self.refresh_expiry
        ).pack(side="left", padx=10)

        tk.Radiobutton(
            filter_frame, text="Already Expired", variable=self.filter_var,
            value="expired", bg="#ffffff", font=("Segoe UI", 10),
            command=self.refresh_expiry
        ).pack(side="left", padx=10)

        tk.Radiobutton(
            filter_frame, text="All Medicines", variable=self.filter_var,
            value="all", bg="#ffffff", font=("Segoe UI", 10),
            command=self.refresh_expiry
        ).pack(side="left", padx=10)

        # Summary label
        self.summary_label = tk.Label(
            self, text="", font=("Segoe UI", 11, "bold"),
            bg="#f0f4f8", fg="#2c3e50"
        )
        self.summary_label.pack(pady=5)

        # Treeview
        tree_frame = tk.Frame(self, bg="#ffffff")
        tree_frame.pack(pady=10, padx=40, fill="both", expand=True)

        columns = ("ID", "Name", "Batch", "Generic Name", "Supplier", "Price", "Stock", "Expiry Date", "Days Left")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        col_widths = {"ID": 50, "Name": 150, "Batch": 100, "Generic Name": 150,
                      "Supplier": 120, "Price": 80, "Stock": 70, "Expiry Date": 100, "Days Left": 80}

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100), anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure tags for color coding
        self.tree.tag_configure("expired", background="#fadbd8", foreground="#c0392b")
        self.tree.tag_configure("expiring_soon", background="#fcf3cf", foreground="#b7950b")
        self.tree.tag_configure("normal", background="#ffffff", foreground="#2c3e50")

        # Refresh button
        tk.Button(
            self, text="Refresh", font=("Segoe UI", 10, "bold"),
            bg="#3498db", fg="white", padx=20, pady=6, cursor="hand2",
            command=self.refresh_expiry
        ).pack(pady=15)

    def refresh_expiry(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filter_val = self.filter_var.get()
        today = datetime.now().date()

        if filter_val == "expired":
            medicines = database.get_expired_medicines()
            self.summary_label.config(text=f"Showing {len(medicines)} expired medicine(s)")
        elif filter_val == "all":
            medicines = database.get_all_medicines()
            self.summary_label.config(text=f"Showing all {len(medicines)} medicine(s)")
        else:
            days = int(filter_val)
            medicines = database.get_expiring_medicines(days)
            self.summary_label.config(
                text=f"Showing {len(medicines)} medicine(s) expiring within {days} days"
            )

        for m in medicines:
            expiry_date = m.get("expiry_date")
            if expiry_date:
                try:
                    exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
                    days_left = (exp_date - today).days
                except ValueError:
                    days_left = 0
            else:
                days_left = None

            tag = "normal"
            if days_left is not None:
                if days_left < 0:
                    tag = "expired"
                elif days_left <= int(filter_val) if filter_val.isdigit() else days_left <= 30:
                    tag = "expiring_soon"

            values = (
                m["id"], m["name"], m["batch"], m["generic_name"] or "",
                m["supplier_name"] or "", f"${m['price']:.2f}",
                m["stock_qty"], expiry_date or "",
                f"{days_left} days" if days_left is not None else "N/A"
            )
            self.tree.insert("", "end", values=values, tags=(tag,))