"""
Supplier Management module.
CRUD operations for suppliers.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database


class SuppliersFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f4f8")
        self.controller = controller
        self.selected_supplier_id = None
        self.build_ui()
        self.refresh_suppliers()

    def build_ui(self):
        title = tk.Label(
            self, text="Supplier Management", font=("Segoe UI", 20, "bold"),
            bg="#f0f4f8", fg="#2c3e50"
        )
        title.pack(pady=(15, 10))

        form_frame = tk.LabelFrame(
            self, text="Add / Edit Supplier", font=("Segoe UI", 11, "bold"),
            bg="#ffffff", fg="#2c3e50", padx=20, pady=15
        )
        form_frame.pack(pady=10, padx=40, fill="x")

        fields = [
            ("Supplier Name:", "name"),
            ("Contact:", "contact"),
            ("Company:", "company"),
        ]

        self.entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            tk.Label(
                form_frame, text=label_text, font=("Segoe UI", 10),
                bg="#ffffff", fg="#34495e"
            ).grid(row=i, column=0, padx=(0, 10), pady=8, sticky="e")
            entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=40)
            entry.grid(row=i, column=1, padx=(0, 20), pady=8, sticky="w")
            self.entries[field_name] = entry

        btn_frame = tk.Frame(form_frame, bg="#ffffff")
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)

        tk.Button(
            btn_frame, text="Add Supplier", font=("Segoe UI", 10, "bold"),
            bg="#27ae60", fg="white", padx=20, pady=6, cursor="hand2",
            command=self.add_supplier
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Update", font=("Segoe UI", 10, "bold"),
            bg="#3498db", fg="white", padx=20, pady=6, cursor="hand2",
            command=self.update_supplier
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Delete", font=("Segoe UI", 10, "bold"),
            bg="#e74c3c", fg="white", padx=20, pady=6, cursor="hand2",
            command=self.delete_supplier
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Clear", font=("Segoe UI", 10, "bold"),
            bg="#95a5a6", fg="white", padx=20, pady=6, cursor="hand2",
            command=self.clear_form
        ).pack(side="left", padx=5)

        tree_frame = tk.Frame(self, bg="#ffffff")
        tree_frame.pack(pady=20, padx=40, fill="both", expand=True)

        columns = ("ID", "Name", "Contact", "Company", "Created At")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

        col_widths = {"ID": 50, "Name": 150, "Contact": 150, "Company": 200, "Created At": 150}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100), anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh_suppliers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        suppliers = database.get_all_suppliers()
        for s in suppliers:
            self.tree.insert("", "end", values=(
                s["id"], s["name"], s["contact"] or "",
                s["company"] or "", s["created_at"] or ""
            ))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        values = item["values"]
        self.selected_supplier_id = values[0]
        self.entries["name"].delete(0, tk.END)
        self.entries["name"].insert(0, values[1])
        self.entries["contact"].delete(0, tk.END)
        self.entries["contact"].insert(0, values[2])
        self.entries["company"].delete(0, tk.END)
        self.entries["company"].insert(0, values[3])

    def clear_form(self):
        self.selected_supplier_id = None
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def add_supplier(self):
        name = self.entries["name"].get().strip()
        contact = self.entries["contact"].get().strip()
        company = self.entries["company"].get().strip()
        if not name:
            messagebox.showerror("Error", "Supplier name is required!")
            return
        try:
            database.add_supplier(name, contact, company)
            messagebox.showinfo("Success", "Supplier added successfully!")
            self.clear_form()
            self.refresh_suppliers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_supplier(self):
        if not self.selected_supplier_id:
            messagebox.showwarning("Warning", "Please select a supplier to update!")
            return
        name = self.entries["name"].get().strip()
        contact = self.entries["contact"].get().strip()
        company = self.entries["company"].get().strip()
        if not name:
            messagebox.showerror("Error", "Supplier name is required!")
            return
        try:
            database.update_supplier(self.selected_supplier_id, name, contact, company)
            messagebox.showinfo("Success", "Supplier updated successfully!")
            self.clear_form()
            self.refresh_suppliers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_supplier(self):
        if not self.selected_supplier_id:
            messagebox.showwarning("Warning", "Please select a supplier to delete!")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this supplier?"):
            try:
                database.delete_supplier(self.selected_supplier_id)
                messagebox.showinfo("Success", "Supplier deleted successfully!")
                self.clear_form()
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", str(e))