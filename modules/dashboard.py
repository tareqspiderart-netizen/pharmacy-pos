"""
Dashboard module - Shows quick stats: Total Sales, Expiring Soon, Low Stock.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import database


class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f4f8")
        self.controller = controller
        self.build_ui()
        self.refresh_stats()

    def build_ui(self):
        # Title
        title = tk.Label(
            self, text="Dashboard", font=("Segoe UI", 24, "bold"),
            bg="#f0f4f8", fg="#2c3e50"
        )
        title.pack(pady=(20, 30))

        # Stats cards container
        stats_frame = tk.Frame(self, bg="#f0f4f8")
        stats_frame.pack(pady=10)

        self.create_stat_card(stats_frame, "Total Sales", "$0.00", "#3498db", "0 sales today")
        self.create_stat_card(stats_frame, "Expiring Soon (30 days)", "0", "#e74c3c", "Medicines expiring within 30 days")
        self.create_stat_card(stats_frame, "Low Stock Items", "0", "#f39c12", "Items below stock threshold")

        # Recent activity / alerts section
        alerts_frame = tk.LabelFrame(
            self, text="Alerts & Notifications", font=("Segoe UI", 12, "bold"),
            bg="#ffffff", fg="#2c3e50", padx=20, pady=15
        )
        alerts_frame.pack(pady=30, padx=40, fill="both", expand=True)

        self.alerts_listbox = tk.Listbox(
            alerts_frame, font=("Segoe UI", 11),
            bg="#ffffff", fg="#34495e", selectbackground="#3498db",
            selectforeground="#ffffff", borderwidth=0, highlightthickness=0,
            activestyle="none"
        )
        self.alerts_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Refresh button
        refresh_btn = tk.Button(
            self, text="Refresh Stats", font=("Segoe UI", 11, "bold"),
            bg="#3498db", fg="white", padx=20, pady=8,
            cursor="hand2", command=self.refresh_stats
        )
        refresh_btn.pack(pady=20)

    def create_stat_card(self, parent, title, value, color, subtitle):
        card = tk.Frame(parent, bg="#ffffff", bd=1, relief="solid")
        card.pack(side="left", padx=15, pady=10, ipadx=25, ipady=25)

        tk.Label(
            card, text=title, font=("Segoe UI", 12, "bold"),
            bg="#ffffff", fg="#7f8c8d"
        ).pack()

        value_label = tk.Label(
            card, text=value, font=("Segoe UI", 24, "bold"),
            bg="#ffffff", fg=color
        )
        value_label.pack(pady=(5, 0))

        tk.Label(
            card, text=subtitle, font=("Segoe UI", 9),
            bg="#ffffff", fg="#95a5a6"
        ).pack(pady=(5, 0))

        # Store reference to value label for updates
        setattr(self, f"card_{title.lower().replace(' ', '_').replace('(', '').replace(')', '')}_value", value_label)

    def refresh_stats(self):
        # Total sales
        total_sales = database.get_total_sales()
        today_sales = database.get_today_sales()
        self.card_total_sales_value.config(text=f"${total_sales:.2f}")
        # Update subtitle for today's sales
        # Find and update - we'll just update the value label

        # Expiring soon
        expiring = database.get_expiring_medicines(30)
        expired = database.get_expired_medicines()
        total_expiring = len(expiring) + len(expired)
        self.card_expiring_soon_30_days_value.config(text=str(total_expiring))

        # Low stock
        low_stock = database.get_low_stock_medicines(10)
        self.card_low_stock_items_value.config(text=str(len(low_stock)))

        # Update alerts list
        self.alerts_listbox.delete(0, tk.END)
        if expired:
            self.alerts_listbox.insert(tk.END, "EXPIRED MEDICINES:")
            for m in expired:
                self.alerts_listbox.insert(
                    tk.END,
                    f"  {m['name']} (Batch: {m['batch']}) - Expired on {m['expiry_date']}"
                )
            self.alerts_listbox.insert(tk.END, "")

        if expiring:
            self.alerts_listbox.insert(tk.END, "EXPIRING SOON (within 30 days):")
            for m in expiring:
                self.alerts_listbox.insert(
                    tk.END,
                    f"  {m['name']} (Batch: {m['batch']}) - Expires on {m['expiry_date']}"
                )

        if not expired and not expiring:
            self.alerts_listbox.insert(tk.END, "No expiry alerts. All medicines are valid.")

        if low_stock:
            self.alerts_listbox.insert(tk.END, "")
            self.alerts_listbox.insert(tk.END, "LOW STOCK ALERT:")
            for m in low_stock:
                self.alerts_listbox.insert(
                    tk.END,
                    f"  {m['name']} - Only {m['stock_qty']} left in stock"
                )

        if not low_stock:
            if not expired and not expiring:
                self.alerts_listbox.insert(tk.END, "All stock levels are healthy.")