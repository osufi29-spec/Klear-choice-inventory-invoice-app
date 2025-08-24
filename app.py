import os
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database config (SQLite by default, Render pe Postgres use hoga if DATABASE_URL set)
DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(BASE_DIR, "data.db")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ MODELS ------------------ #
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # price in paisa (₹100 = 10000 paisa)
    quantity = db.Column(db.Integer, default=0)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer_name = db.Column(db.String(200))
    total_amount = db.Column(db.Integer, nullable=False)  # in paisa
    paid = db.Column(db.Boolean, default=False)

# ------------------ INIT ------------------ #

with app.app_context():
    db.create_all()
# ------------------ ROUTES ------------------ #

@app.route("/")
def home():
    items = Item.query.all()
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()
    return render_template("index.html", items=items, invoices=invoices)

# Add new item
@app.route("/add_item", methods=["POST"])
def add_item():
    name = request.form.get("name")
    price = int(float(request.form.get("price")) * 100)  # convert to paisa
    qty = int(request.form.get("quantity"))
    item = Item(name=name, price=price, quantity=qty)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for("home"))

# Create invoice
@app.route("/create_invoice", methods=["POST"])
def create_invoice():
    customer = request.form.get("customer_name", "Walk-in")
    items = json.loads(request.form.get("items_json", "[]"))
    total = 0
    for it in items:
        total += int(it.get("price", 0)) * int(it.get("quantity", 1))
    inv = Invoice(customer_name=customer, total_amount=total, paid=False)
    db.session.add(inv)
    db.session.commit()
    return redirect(url_for("invoice_view", invoice_id=inv.id))

# View invoice
@app.route("/invoice/<int:invoice_id>")
def invoice_view(invoice_id):
    inv = Invoice.query.get_or_404(invoice_id)

    # GPay / Bank Details (Change yahan apni details dalna)
    gpay_id = "yourgpay@upi"
    bank_name = "J&K Bank"
    acc_no = "1234567890"
    ifsc = "JAKA0XXXXXX"

    return render_template("invoice.html", invoice=inv,
                           gpay_id=gpay_id, bank_name=bank_name,
                           acc_no=acc_no, ifsc=ifsc)

# Mark invoice as paid (manual after receiving payment)
@app.route("/mark_paid/<int:invoice_id>", methods=["POST"])
def mark_paid(invoice_id):
    inv = Invoice.query.get_or_404(invoice_id)
    inv.paid = True
    db.session.commit()
    return redirect(url_for("invoice_view", invoice_id=invoice_id))

# Payment success page (optional)
@app.route("/success/<int:invoice_id>")
def payment_success(invoice_id):
    inv = Invoice.query.get_or_404(invoice_id)
    return render_template("success.html", invoice=inv)

# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    app.run(debug=True)
