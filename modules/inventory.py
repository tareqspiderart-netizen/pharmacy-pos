"""
Medicine Inventory Management module.
CRUD operations for medicines with supplier association.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database


class InventoryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f4f8")
        self.controller = controller
        self.selected_medicine_id = None
        self.build_ui()
        self.refresh_medicines()

    def build_ui(self):
        title = tk.Label(
            self, text="Medicine Inventory", font=("Segoe UI", 20, "bold"),
            bg="#f0f4f8", fg="#2c3e50"
        )
        title.pack(pady=(15, 10))

        form_frame = tk.LabelFrame(
            self, text="Add / Edit Medicine", font=("Segoe UI", 11, "bold"),
            bg="#ffffff", fg="#2c3e50", padx=20, pady=15
        )
        form_frame.pack(pady=10, padx=40, fill="x")

        fields = [
            ("Name:", "name"),
            ("Batch:", "batch"),
            ("Generic Name:", "generic_name"),
            ("Supplier:", "supplier"),
            ("Price ($):", "price"),
            ("Stock Qty:", "stock_qty"),
            ("Expiry Date (YYYY-MM-DD):", "expiry_date"),
        ]

        self.entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            row = i // 4
            col = (i % 4) * 2

            tk.Label(
                form_frame, text=label_text, font=("Segoe UI", 10),
                bg="#ffffff", fg="#34495e"
            ).grid(row=row, column=col, padx=(0, 5), pady=5, sticky="e")

            if field_name == "supplier":
                combo = ttk.Combobox(
                    form_frame, font=("Segoe UI", 10),
                    state="readonly", width=27
                )
                combo.grid(row=row, column=col + 1, padx=(0, 15), pady=5, sticky="w")
                self.entries[field_name] = combo
                self.load_suppliers_into_combo(combo)
            else:
                entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=30)
                entry.grid(row=row, column=col + 1, padx=(0, 15), pady=5, sticky="w")
                self.entries[field_name] = entry
        btn_frame = tk.Frame(form_frame, bg="#ffffff")
        btn_frame.grid(row=len(fields) // 4 + 1, column=0, columnspan=8, pady=15)

        tk.Button(
            btn_frame, text="Add Medicine", font=("Segoe UI", 10, "bold"),
            bg="#27ae60", fg="white", padx=20, pady=6, cursor="hand2",
            command=self.add_medicine
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Update", font=("Segoe UI", 10, "bold"),
            bg="#3498db", fg="white", padx=20, pady=6, cursor="hand2",
            command=self.update_medicine
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Delete", font=("Segoe UI", 10, "bold"),
            bg="#e74c3c", fg="white", padx=20, pady=6, cursor="hand2",
            command=self.delete_medicine
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Clear", font=("Segoe UI", 10, "bold"),
            bg="#95a5a6", fg="white", padx=20, pady=6, cursor="hand2",
            command=self.clear_form
        ).pack(side="left", padx=5)

        search_frame = tk.Frame(self, bg="#f0f4f8")
        search_frame.pack(pady=10)

        tk.Label(
            search_frame, text="Search:", font=("Segoe UI", 10),
            bg="#f0f4f8", fg="#34495e"
        ).pack(side="left", padx=(0, 5))

        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 10), width=30)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_medicines())

        tk.Button(
            search_frame, text="Refresh", font=("Segoe UI", 10, "bold"),
            bg="#34495e", fg="white", padx=15, pady=4, cursor="hand2",
            command=self.refresh_medicines
        ).pack(side="left")

        tree_frame = tk.Frame(self, bg="#ffffff")
        tree_frame.pack(pady=10, padx=40, fill="both", expand=True)

        columns = ("ID", "Name", "Batch", "Generic Name", "Supplier", "Price", "Stock", "Expiry")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

        col_widths = {"ID": 50, "Name": 150, "Batch": 100, "Generic Name": 150,
                      "Supplier": 120, "Price": 80, "Stock": 70, "Expiry": 100}

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_tree(col))
            self.tree.column(col, width=col_widths.get(col, 100), anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    def load_suppliers_into_combo(self, combo):
        suppliers = database.get_all_suppliers()
        combo["values"] = [s["name"] for s in suppliers]
        self.supplier_map = {s["name"]: s["id"] for s in suppliers}

    def get_supplier_id_by_name(self, name):
        return self.supplier_map.get(name)

    def refresh_medicines(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        medicines = database.get_all_medicines()
        for m in medicines:
            self.tree.insert("", "end", values=(
                m["id"], m["name"], m["batch"], m["generic_name"] or "",
                m["supplier_name"] or "", f"${m['price']:.2f}",
                m["stock_qty"], m["expiry_date"] or ""
            ))

    def search_medicines(self):
        query = self.search_entry.get().strip()
        if not query:
            self.refresh_medicines()
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        medicines = database.search_medicines(query)
        for m in medicines:
            self.tree.insert("", "end", values=(
                m["id"], m["name"], m["batch"], m["generic_name"] or "",
                m["supplier_name"] or "", f"${m['price']:.2f}",
                m["stock_qty"], m["expiry_date"] or ""
            ))

    def sort_tree(self, col):
        medicines = database.get_all_medicines()
        reverse = getattr(self, f"_sort_reverse_{col}", False)
        key_map = {
            "ID": "id", "Name": "name", "Batch": "batch",
            "Generic Name": "generic_name", "Supplier": "supplier_name",
            "Price": "price", "Stock": "stock_qty", "Expiry": "expiry_date"
        }
        key = key_map.get(col, "name")
        medicines.sort(key=lambda x: (x[key] is None, x[key] or ""), reverse=reverse)
        setattr(self, f"_sort_reverse_{col}", not reverse)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for m in medicines:
            self.tree.insert("", "end", values=(
                m["id"], m["name"], m["batch"], m["generic_name"] or "",
                m["supplier_name"] or "", f"${m['price']:.2f}",
                m["stock_qty"], m["expiry_date"] or ""
            ))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        values = item["values"]
        self.selected_medicine_id = values[0]
        self.entries["name"].delete(0, tk.END)
        self.entries["name"].insert(0, values[1])
        self.entries["batch"].delete(0, tk.END)
        self.entries["batch"].insert(0, values[2])
        self.entries["generic_name"].delete(0, tk.END)
        self.entries["generic_name"].insert(0, values[3])
        self.entries["supplier"].set(values[4])
        self.entries["price"].delete(0, tk.END)
        self.entries["price"].insert(0, values[5].replace("$", ""))
        self.entries["stock_qty"].delete(0, tk.END)
        self.entries["stock_qty"].insert(0, values[6])
        self.entries["expiry_date"].delete(0, tk.END)
        self.entries["expiry_date"].insert(0, values[7])

    def clear_form(self):
        self.selected_medicine_id = None
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
                entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def add_medicine(self):
        try:
            name = self.entries["name"].get().strip()
            batch = self.entries["batch"].get().strip()
            generic_name = self.entries["generic_name"].get().strip()
            supplier_name = self.entries["supplier"].get().strip()
            price = float(self.entries["price"].get().strip() or 0)
            stock_qty = int(self.entries["stock_qty"].get().strip() or 0)
            expiry_date = self.entries["expiry_date"].get().strip() or None
            if not name or not batch:
                messagebox.showerror("Error", "Name and Batch are required!")
                return
            supplier_id = self.get_supplier_id_by_name(supplier_name) if supplier_name else None
            database.add_medicine(name, batch, generic_name, supplier_id, price, stock_qty, expiry_date)
            messagebox.showinfo("Success", "Medicine added successfully!")
            self.clear_form()
            self.refresh_medicines()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid price and stock quantity!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_medicine(self):
        if not self.selected_medicine_id:
            messagebox.showwarning("Warning", "Please select a medicine to update!")
            return
        try:
            name = self.entries["name"].get().strip()
            batch = self.entries["batch"].get().strip()
            generic_name = self.entries["generic_name"].get().strip()
            supplier_name = self.entries["supplier"].get().strip()
            price = float(self.entries["price"].get().strip() or 0)
            stock_qty = int(self.entries["stock_qty"].get().strip() or 0)
            expiry_date = self.entries["expiry_date"].get().strip() or None
            if not name or not batch:
                messagebox.showerror("Error", "Name and Batch are required!")
                return
            supplier_id = self.get_supplier_id_by_name(supplier_name) if supplier_name else None
            database.update_medicine(
                self.selected_medicine_id, name, batch, generic_name,
                supplier_id, price, stock_qty, expiry_date
            )
            messagebox.showinfo("Success", "Medicine updated successfully!")
            self.clear_form()
            self.refresh_medicines()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid price and stock quantity!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_medicine(self):
        if not self.selected_medicine_id:
            messagebox.showwarning("Warning", "Please select a medicine to delete!")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this medicine?"):
            database.delete_medicine(self.selected_medicine_id)
            messagebox.showinfo("Success", "Medicine deleted successfully!")
            self.clear_form()
            self.refresh_medicines()