from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Secret key for session management
app.secret_key = "your_secret_key"

# Database configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------------------
# Database Model
# --------------------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Product {self.name}>"

# --------------------------------
# Database Initialization (Fixed)
# --------------------------------
with app.app_context():
    db.create_all()

# --------------------------------
# Routes
# --------------------------------

# Home page
@app.route("/")
def index():
    products = Product.query.all()
    return render_template("index.html", products=products)

# Add Product
@app.route("/add", methods=["POST"])
def add_product():
    name = request.form['name']
    price = request.form['price']
    quantity = request.form['quantity']

    if name and price and quantity:
        new_product = Product(name=name, price=float(price), quantity=int(quantity))
        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully!", "success")
    else:
        flash("All fields are required!", "danger")

    return redirect(url_for("index"))

# Delete Product
@app.route("/delete/<int:id>")
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for("index"))

# Update Product
@app.route("/update/<int:id>", methods=["POST"])
def update_product(id):
    product = Product.query.get_or_404(id)
    product.name = request.form['name']
    product.price = float(request.form['price'])
    product.quantity = int(request.form['quantity'])
    db.session.commit()
    flash("Product updated successfully!", "success")
    return redirect(url_for("index"))

# --------------------------------
# Run the app
# --------------------------------
if __name__ == "__main__":
    app.run(debug=True)
