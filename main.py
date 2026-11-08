"""
Pharmacy POS & Inventory Management System - Flask Web Application
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database

app = Flask(__name__)
app.secret_key = "pharmacy_pos_secret_key_2026"

# Initialize database on startup
database.init_database()


# ==================== Dashboard Routes ====================

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    total_sales = database.get_total_sales()
    today_sales = database.get_today_sales()
    expiring = database.get_expiring_medicines(30)
    expired = database.get_expired_medicines()
    low_stock = database.get_low_stock_medicines(10)

    return render_template(
        "dashboard.html",
        total_sales=total_sales,
        today_sales=today_sales,
        expiring_count=len(expiring) + len(expired),
        expired_count=len(expired),
        low_stock_count=len(low_stock),
        expiring_medicines=expiring,
        expired_medicines=expired,
        low_stock_medicines=low_stock,
    )


# ==================== Inventory Routes ====================

@app.route("/inventory")
def inventory():
    medicines = database.get_all_medicines()
    suppliers = database.get_all_suppliers()
    return render_template("inventory.html", medicines=medicines, suppliers=suppliers)


@app.route("/inventory/add", methods=["POST"])
def add_medicine():
    try:
        name = request.form.get("name", "").strip()
        batch = request.form.get("batch", "").strip()
        generic_name = request.form.get("generic_name", "").strip()
        supplier_name = request.form.get("supplier", "").strip()
        price = float(request.form.get("price", 0) or 0)
        stock_qty = int(request.form.get("stock_qty", 0) or 0)
        expiry_date = request.form.get("expiry_date", "").strip() or None

        if not name or not batch:
            flash("Name and Batch are required!", "error")
            return redirect(url_for("inventory"))

        supplier_id = None
        if supplier_name:
            suppliers = database.get_all_suppliers()
            for s in suppliers:
                if s["name"] == supplier_name:
                    supplier_id = s["id"]
                    break

        database.add_medicine(
            name, batch, generic_name, supplier_id, price, stock_qty, expiry_date
        )
        flash("Medicine added successfully!", "success")
    except ValueError:
        flash("Please enter valid price and stock quantity!", "error")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for("inventory"))


@app.route("/inventory/edit/<int:medicine_id>", methods=["POST"])
def edit_medicine(medicine_id):
    try:
        name = request.form.get("name", "").strip()
        batch = request.form.get("batch", "").strip()
        generic_name = request.form.get("generic_name", "").strip()
        supplier_name = request.form.get("supplier", "").strip()
        price = float(request.form.get("price", 0) or 0)
        stock_qty = int(request.form.get("stock_qty", 0) or 0)
        expiry_date = request.form.get("expiry_date", "").strip() or None

        if not name or not batch:
            flash("Name and Batch are required!", "error")
            return redirect(url_for("inventory"))

        supplier_id = None
        if supplier_name:
            suppliers = database.get_all_suppliers()
            for s in suppliers:
                if s["name"] == supplier_name:
                    supplier_id = s["id"]
                    break

        database.update_medicine(
            medicine_id, name, batch, generic_name, supplier_id, price, stock_qty, expiry_date
        )
        flash("Medicine updated successfully!", "success")
    except ValueError:
        flash("Please enter valid price and stock quantity!", "error")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for("inventory"))


@app.route("/inventory/delete/<int:medicine_id>", methods=["POST"])
def delete_medicine(medicine_id):
    try:
        database.delete_medicine(medicine_id)
        flash("Medicine deleted successfully!", "success")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for("inventory"))


@app.route("/inventory/search")
def search_inventory():
    query = request.args.get("q", "").strip()
    if query:
        medicines = database.search_medicines(query)
    else:
        medicines = database.get_all_medicines()
    return jsonify(medicines)


# ==================== Expiry Tracker Routes ====================

@app.route("/expiry")
def expiry():
    filter_val = request.args.get("filter", "30")
    from datetime import datetime, timedelta

    today = datetime.now().date()

    if filter_val == "expired":
        medicines = database.get_expired_medicines()
        summary = f"Showing {len(medicines)} expired medicine(s)"
    elif filter_val == "all":
        medicines = database.get_all_medicines()
        summary = f"Showing all {len(medicines)} medicine(s)"
    else:
        days = int(filter_val)
        medicines = database.get_expiring_medicines(days)
        summary = f"Showing {len(medicines)} medicine(s) expiring within {days} days"

    # Calculate days left for each medicine
    for m in medicines:
        if m.get("expiry_date"):
            try:
                exp_date = datetime.strptime(m["expiry_date"], "%Y-%m-%d").date()
                m["days_left"] = (exp_date - today).days
            except ValueError:
                m["days_left"] = None
        else:
            m["days_left"] = None

    return render_template(
        "expiry.html",
        medicines=medicines,
        filter_val=filter_val,
        summary=summary,
    )


# ==================== Supplier Routes ====================

@app.route("/suppliers")
def suppliers():
    suppliers_list = database.get_all_suppliers()
    return render_template("suppliers.html", suppliers=suppliers_list)


@app.route("/suppliers/add", methods=["POST"])
def add_supplier():
    name = request.form.get("name", "").strip()
    contact = request.form.get("contact", "").strip()
    company = request.form.get("company", "").strip()

    if not name:
        flash("Supplier name is required!", "error")
        return redirect(url_for("suppliers"))

    try:
        database.add_supplier(name, contact, company)
        flash("Supplier added successfully!", "success")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for("suppliers"))


@app.route("/suppliers/edit/<int:supplier_id>", methods=["POST"])
def edit_supplier(supplier_id):
    name = request.form.get("name", "").strip()
    contact = request.form.get("contact", "").strip()
    company = request.form.get("company", "").strip()

    if not name:
        flash("Supplier name is required!", "error")
        return redirect(url_for("suppliers"))

    try:
        database.update_supplier(supplier_id, name, contact, company)
        flash("Supplier updated successfully!", "success")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for("suppliers"))


@app.route("/suppliers/delete/<int:supplier_id>", methods=["POST"])
def delete_supplier(supplier_id):
    try:
        database.delete_supplier(supplier_id)
        flash("Supplier deleted successfully!", "success")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for("suppliers"))


# ==================== POS Billing Routes ====================

@app.route("/pos")
def pos():
    medicines = database.get_all_medicines()
    return render_template("pos.html", medicines=medicines)


@app.route("/pos/search")
def pos_search():
    query = request.args.get("q", "").strip()
    if query:
        medicines = database.search_medicines(query)
    else:
        medicines = database.get_all_medicines()
    return jsonify(medicines)


@app.route("/pos/checkout", methods=["POST"])
def pos_checkout():
    try:
        data = request.get_json()
        cart = data.get("cart", [])

        if not cart:
            return jsonify({"success": False, "message": "Cart is empty!"}), 400

        grand_total = sum(item["total_price"] for item in cart)

        # Record sale
        sale_id = database.add_sale(grand_total, "Admin")

        # Add sale items and reduce stock
        for item in cart:
            database.add_sale_item(
                sale_id,
                item["medicine_id"],
                item["quantity"],
                item["unit_price"],
                item["total_price"],
            )
            database.reduce_stock(item["medicine_id"], item["quantity"])

        return jsonify(
            {
                "success": True,
                "sale_id": sale_id,
                "total": grand_total,
                "message": "Sale completed successfully!",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)