"""
POS Billing Screen module.
Search medicine, add to cart, calculate total, show receipt, reduce stock after sale.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database


class POSBillingFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f4f8")
        self.controller = controller
        self.cart = []
        self.build_ui()
        self.refresh_medicine_list()

    def build_ui(self):
        title = tk.Label(
            self, text="POS Billing", font=("Segoe UI", 20, "bold"),
            bg="#f0f4f8", fg="#2c3e50"
        )
        title.pack(pady=(15, 10))

        main_container = tk.Frame(self, bg="#f0f4f8")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        left_frame = tk.LabelFrame(
            main_container, text="Search & Add Medicine", font=("Segoe UI", 11, "bold"),
            bg="#ffffff", fg="#2c3e50", padx=15, pady=15
        )
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        search_frame = tk.Frame(left_frame, bg="#ffffff")
        search_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            search_frame, text="Search:", font=("Segoe UI", 10),
            bg="#ffffff", fg="#34495e"
        ).pack(side="left", padx=(0, 5))

        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 10), width=25)
        self.search_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_medicines())

        tk.Button(
            search_frame, text="Refresh", font=("Segoe UI", 9, "bold"),
            bg="#34495e", fg="white", padx=10, pady=3, cursor="hand2",
            command=self.refresh_medicine_list
        ).pack(side="left")

        list_frame = tk.Frame(left_frame, bg="#ffffff")
        list_frame.pack(fill="both", expand=True)

        columns = ("ID", "Name", "Batch", "Price", "Stock", "Expiry")
        self.medicine_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)

        col_widths = {"ID": 40, "Name": 120, "Batch": 80, "Price": 70, "Stock": 60, "Expiry": 90}
        for col in columns:
            self.medicine_tree.heading(col, text=col)
            self.medicine_tree.column(col, width=col_widths.get(col, 80), anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.medicine_tree.yview)
        self.medicine_tree.configure(yscrollcommand=scrollbar.set)
        self.medicine_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        add_frame = tk.Frame(left_frame, bg="#ffffff")
        add_frame.pack(fill="x", pady=(10, 0))

        tk.Label(
            add_frame, text="Qty:", font=("Segoe UI", 10),
            bg="#ffffff", fg="#34495e"
        ).pack(side="left", padx=(0, 5))

        self.qty_entry = tk.Entry(add_frame, font=("Segoe UI", 10), width=8)
        self.qty_entry.pack(side="left", padx=(0, 10))
        self.qty_entry.insert(0, "1")

        tk.Button(
            add_frame, text="Add to Cart", font=("Segoe UI", 10, "bold"),
            bg="#27ae60", fg="white", padx=20, pady=6, cursor="hand2",
            command=self.add_to_cart
        ).pack(side="left")

        right_frame = tk.LabelFrame(
            main_container, text="Shopping Cart", font=("Segoe UI", 11, "bold"),
            bg="#ffffff", fg="#2c3e50", padx=15, pady=15
        )
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        cart_columns = ("Name", "Qty", "Unit Price", "Total")
        self.cart_tree = ttk.Treeview(right_frame, columns=cart_columns, show="headings", height=12)

        cart_widths = {"Name": 130, "Qty": 50, "Unit Price": 90, "Total": 90}
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=cart_widths.get(col, 80), anchor="center")

        cart_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        self.cart_tree.pack(fill="both", expand=True, pady=(0, 10))
        cart_scrollbar.pack(side="right", fill="y")

        tk.Button(
            right_frame, text="Remove Selected", font=("Segoe UI", 9, "bold"),
            bg="#e74c3c", fg="white", padx=15, pady=4, cursor="hand2",
            command=self.remove_from_cart
        ).pack(anchor="e", pady=(0, 10))

        total_frame = tk.Frame(right_frame, bg="#ffffff")
        total_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            total_frame, text="Grand Total:", font=("Segoe UI", 14, "bold"),
            bg="#ffffff", fg="#2c3e50"
        ).pack(side="left")

        self.total_label = tk.Label(
            total_frame, text="$0.00", font=("Segoe UI", 16, "bold"),
            bg="#ffffff", fg="#e74c3c"
        )
        self.total_label.pack(side="right")

        checkout_frame = tk.Frame(right_frame, bg="#ffffff")
        checkout_frame.pack(fill="x")

        tk.Button(
            checkout_frame, text="Checkout", font=("Segoe UI", 11, "bold"),
            bg="#27ae60", fg="white", padx=30, pady=10, cursor="hand2",
            command=self.checkout
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            checkout_frame, text="Clear Cart", font=("Segoe UI", 11, "bold"),
            bg="#95a5a6", fg="white", padx=30, pady=10, cursor="hand2",
            command=self.clear_cart
        ).pack(side="left")

    def refresh_medicine_list(self):
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)
        medicines = database.get_all_medicines()
        for m in medicines:
            self.medicine_tree.insert("", "end", values=(
                m["id"], m["name"], m["batch"],
                f"${m['price']:.2f}", m["stock_qty"],
                m["expiry_date"] or ""
            ))

    def search_medicines(self):
        query = self.search_entry.get().strip()
        if not query:
            self.refresh_medicine_list()
            return
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)
        medicines = database.search_medicines(query)
        for m in medicines:
            self.medicine_tree.insert("", "end", values=(
                m["id"], m["name"], m["batch"],
                f"${m['price']:.2f}", m["stock_qty"],
                m["expiry_date"] or ""
            ))

    def add_to_cart(self):
        selection = self.medicine_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a medicine!")
            return
        item = self.medicine_tree.item(selection[0])
        values = item["values"]
        medicine_id = values[0]
        name = values[1]
        price = float(values[3].replace("$", ""))
        stock = values[4]
        try:
            quantity = int(self.qty_entry.get().strip())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0!")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity!")
            return
        if quantity > stock:
            messagebox.showerror(
                "Error",
                f"Not enough stock! Only {stock} available."
            )
            return
        for cart_item in self.cart:
            if cart_item["medicine_id"] == medicine_id:
                new_qty = cart_item["quantity"] + quantity
                if new_qty > stock:
                    messagebox.showerror(
                        "Error",
                        f"Not enough stock! Only {stock} available for {name}."
                    )
                    return
                cart_item["quantity"] = new_qty
                cart_item["total_price"] = new_qty * price
                self.update_cart_display()
                return
        total_price = quantity * price
        self.cart.append({
            "medicine_id": medicine_id,
            "name": name,
            "quantity": quantity,
            "unit_price": price,
            "total_price": total_price
        })
        self.update_cart_display()

    def update_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        grand_total = 0
        for item in self.cart:
            self.cart_tree.insert("", "end", values=(
                item["name"], item["quantity"],
                f"${item['unit_price']:.2f}", f"${item['total_price']:.2f}"
            ))
            grand_total += item["total_price"]
        self.total_label.config(text=f"${grand_total:.2f}")

    def remove_from_cart(self):
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove!")
            return
        item = self.cart_tree.item(selection[0])
        name = item["values"][0]
        self.cart = [c for c in self.cart if c["name"] != name]
        self.update_cart_display()

    def clear_cart(self):
        self.cart = []
        self.update_cart_display()

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        grand_total = sum(item["total_price"] for item in self.cart)
        if messagebox.askyesno("Confirm Checkout", f"Total amount: ${grand_total:.2f}\nProceed with checkout?"):
            try:
                sale_id = database.add_sale(grand_total, "Admin")
                for item in self.cart:
                    database.add_sale_item(
                        sale_id, item["medicine_id"], item["quantity"],
                        item["unit_price"], item["total_price"]
                    )
                    database.reduce_stock(item["medicine_id"], item["quantity"])
                self.show_receipt(sale_id, grand_total)
                self.clear_cart()
                messagebox.showinfo("Success", "Sale completed successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Checkout failed: {str(e)}")

    def show_receipt(self, sale_id, grand_total):
        receipt_window = tk.Toplevel(self)
        receipt_window.title("Receipt")
        receipt_window.geometry("350x550")
        receipt_window.resizable(False, False)
        receipt_window.grab_set()
        receipt_window.transient(self.winfo_toplevel())
        frame = tk.Frame(receipt_window, padx=20, pady=20, bg="#ffffff")
        frame.pack(fill="both", expand=True)
        tk.Label(
            frame, text="PHARMACY POS", font=("Segoe UI", 16, "bold"),
            bg="#ffffff", fg="#2c3e50"
        ).pack()
        tk.Label(
            frame, text="Receipt", font=("Segoe UI", 12, "bold"),
            bg="#ffffff", fg="#34495e"
        ).pack(pady=(5, 15))
        tk.Label(
            frame, text=f"Sale ID: {sale_id}", font=("Segoe UI", 10),
            bg="#ffffff", fg="#7f8c8d"
        ).pack(anchor="w")
        tk.Label(
            frame, text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            font=("Segoe UI", 10), bg="#ffffff", fg="#7f8c8d"
        ).pack(anchor="w")
        tk.Label(
            frame, text="Cashier: Admin", font=("Segoe UI", 10),
            bg="#ffffff", fg="#7f8c8d"
        ).pack(anchor="w")
        tk.Frame(frame, height=1, bg="#bdc3c7").pack(fill="x", pady=10)
        header_frame = tk.Frame(frame, bg="#ffffff")
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Item", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(side="left")
        tk.Label(header_frame, text="Qty", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(side="left", padx=(40, 0))
        tk.Label(header_frame, text="Price", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(side="right")
        tk.Frame(frame, height=1, bg="#bdc3c7").pack(fill="x", pady=5)
        for item in self.cart:
            item_frame = tk.Frame(frame, bg="#ffffff")
            item_frame.pack(fill="x", pady=2)
            tk.Label(item_frame, text=item["name"], font=("Segoe UI", 10), bg="#ffffff").pack(side="left")
            tk.Label(item_frame, text=str(item["quantity"]), font=("Segoe UI", 10), bg="#ffffff").pack(side="left", padx=(40, 0))
            tk.Label(item_frame, text=f"${item['total_price']:.2f}", font=("Segoe UI", 10), bg="#ffffff").pack(side="right")
        tk.Frame(frame, height=1, bg="#bdc3c7").pack(fill="x", pady=10)
        total_frame = tk.Frame(frame, bg="#ffffff")
        total_frame.pack(fill="x")
        tk.Label(
            total_frame, text="TOTAL:", font=("Segoe UI", 12, "bold"),
            bg="#ffffff", fg="#e74c3c"
        ).pack(side="left")
        tk.Label(
            total_frame, text=f"${grand_total:.2f}", font=("Segoe UI", 12, "bold"),
            bg="#ffffff", fg="#e74c3c"
        ).pack(side="right")
        tk.Frame(frame, height=1, bg="#bdc3c7").pack(fill="x", pady=15)
        tk.Label(
            frame, text="Thank you for your purchase!",
            font=("Segoe UI", 10, "italic"), bg="#ffffff", fg="#7f8c8d"
        ).pack()
        tk.Button(
            frame, text="Print / Close", font=("Segoe UI", 10, "bold"),
            bg="#3498db", fg="white", padx=20, pady=6, cursor="hand2",
            command=receipt_window.destroy
        ).pack(pady=(20, 0))