from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Optional, but makes it clear which table this model is for

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    # --- User Information ---
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))

    # --- Address ---
    street_address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))

    # --- Contact ---
    phone_number = db.Column(db.String(50))
    
    # --- Profile ---
    about_me = db.Column(db.String(140))  
    profile_picture = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)  # New field for admin status

    # --- Relationships ---
    orders = db.relationship('Order', backref='customer', lazy=True)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader  # Tells Flask-Login how to load users
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))

    # --- Relationships ---
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0) 
    image_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shipping_first_name = db.Column(db.String(80), nullable=False)
    shipping_last_name = db.Column(db.String(80), nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    shipping_city = db.Column(db.String(50), nullable=False)
    shipping_state = db.Column(db.String(50), nullable=False)
    shipping_postal_code = db.Column(db.String(20), nullable=False)
    shipping_country = db.Column(db.String(50), nullable=False)
    # Billing Information
    billing_first_name = db.Column(db.String(80))
    billing_last_name = db.Column(db.String(80))
    billing_address = db.Column(db.String(255))
    billing_city = db.Column(db.String(50))
    billing_state = db.Column(db.String(50))
    billing_postal_code = db.Column(db.String(20))
    billing_country = db.Column(db.String(50))
    payment_method = db.Column(db.String(50), nullable=False)
    order_notes = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(20), default='pending')

    # Relationship
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

    @property
    def total_price(self):
        total = 0
        for item in self.order_items:
            total += item.product.price * item.quantity
        return total

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    # Relationship
    product = db.relationship('Product', lazy=True)


