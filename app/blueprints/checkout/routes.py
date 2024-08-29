from flask import  render_template, redirect, url_for, flash,session, current_app
from flask_login import current_user, login_required
from app.models import Product, Order, OrderItem, db
from .forms import CheckoutForm
from app.config import Config
from . import checkout
import urllib.parse


@checkout.route("/whatsapp_redirect/<int:order_id>")
@login_required
def whatsapp_redirect(order_id):
    order = Order.query.get_or_404(order_id)
    if order.customer != current_user:
        flash("You don't have permission to view this order.", "danger")
        return redirect(url_for("main.home"))
    
    # Fetch order items
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    
     # Construct the WhatsApp message
    message = "🛒 *New Order Confirmation* 🛒\n\n"
    message += f"Order id#: *{order.id}*\n"
    message += f"Date: {order.date_created.strftime('%d %b %Y, %I:%M %p')}\n\n"
    
    message += "📦 *Order Details*:\n"
    total_price = 0
    for item in order_items:
        product = Product.query.get(item.product_id)
        item_total = product.price * item.quantity
        total_price += item_total
        message += f"• {product.name}\n"
        message += f"  Quantity: {item.quantity}\n"
        message += f"  Price: ₦{product.price:.2f}\n"
        message += f"  Subtotal: ₦{item_total:.2f}\n\n"
    
    message += f"📊 *Total*: ₦{total_price:.2f}\n\n"
    
    message += "👤 *Customer Information*:\n"
    message += f"Name: {order.shipping_first_name} {order.shipping_last_name}\n"
    message += f"Address: {order.shipping_address}, {order.shipping_city}, {order.shipping_state}, {order.shipping_postal_code}\n"
    message += f"Country: {order.shipping_country}\n\n"
    
    message += "💳 *Payment Method*: Bank Transfer\n\n"
    
    message += "🏦 *Bank Details*:\n"
    message += "Bank Name: [Bank Name]\n"
    message += "Account Name: [Account Name]\n"
    message += "Account Number: [Account Number]\n"
    message += "Sort Code: [Sort Code]\n\n"
    
    message += "Please complete the bank transfer using the order id as the reference. Once payment is confirmed, we will process your order.\n\n"
    
    message += "If you have any questions or concerns, please don't hesitate to reply to this message. Thank you for your order! 🙏"

    # Encode the message for URL
    encoded_message = urllib.parse.quote(message)
    
    # Replace with your actual WhatsApp business number
    whatsapp_number = Config.WHATSAPP_NUMBER
    
    # Construct the WhatsApp URL
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
    
    return redirect(whatsapp_url)

@checkout.route("/", methods=["GET", "POST"])
@login_required
def checkout_process():
    form = CheckoutForm()
    
    # Fetch cart items from session
    cart_items = []
    total_price = 0
    for product_id_str, quantity in session.get("cart", {}).items():
        product_id = int(product_id_str)
        product = Product.query.get(product_id)
        if product:
            item_price = product.price * quantity
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "price": item_price
            })
            total_price += item_price

    if not cart_items:
        flash("Your cart is empty. Please add some items before checking out.", "warning")
        return redirect(url_for("products.all_products"))

    payment_methods = ["Bank Transfer", "Cash on Delivery"]

    if form.validate_on_submit():
        try:
            order = create_order(form, current_user)
            if process_order_items(order, cart_items):
                db.session.commit()
                session.pop("cart", None)

                if form.payment_method.data == "Cash on Delivery":
                    order.status = "processing"
                    db.session.commit()
                    flash("Your order has been placed successfully! We will contact you to confirm your order and arrange delivery.", "success")
                    return redirect(url_for("checkout.order_confirmation", order_id=order.id))
                elif form.payment_method.data == "Bank Transfer":
                    order.status = "pending_payment"
                    db.session.commit()
                    flash("Your order has been placed. Please complete the bank transfer to the following account: [Account Details]. Once payment is confirmed, we will process your order.", "info")
                    return redirect(url_for("checkout.whatsapp_redirect", order_id=order.id))
                
            else:
                db.session.rollback()
                return redirect(url_for("cart.view_cart"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error processing order: {e}")
            flash("An error occurred while processing your order. Please try again later.", "danger")
            return redirect(url_for("cart.view_cart"))

    return render_template(
        "checkout/checkout.html",
        title="Checkout",
        form=form,
        cart_items=cart_items,
        total_price=total_price,
        # payment_methods=payment_methods
    )

@checkout.route("/order_confirmation/<int:order_id>")
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.customer != current_user:
        flash("You don't have permission to view this order.", "danger")
        return redirect(url_for("main.home"))
    return render_template("checkout/order_confirmation.html", order=order)

def create_order(form, user):
    order = Order(
        customer=user,
        shipping_first_name=form.shipping_first_name.data,
        shipping_last_name=form.shipping_last_name.data,
        shipping_address=form.shipping_address.data,
        shipping_city=form.shipping_city.data,
        shipping_state=form.shipping_state.data,
        shipping_postal_code=form.shipping_postal_code.data,
        shipping_country=form.shipping_country.data,
        billing_first_name=form.billing_first_name.data if not form.same_as_shipping.data else form.shipping_first_name.data,
        billing_last_name=form.billing_last_name.data if not form.same_as_shipping.data else form.shipping_last_name.data,
        billing_address=form.billing_address.data if not form.same_as_shipping.data else form.shipping_address.data,
        billing_city=form.billing_city.data if not form.same_as_shipping.data else form.shipping_city.data,
        billing_state=form.billing_state.data if not form.same_as_shipping.data else form.shipping_state.data,
        billing_postal_code=form.billing_postal_code.data if not form.same_as_shipping.data else form.shipping_postal_code.data,
        billing_country=form.billing_country.data if not form.same_as_shipping.data else form.shipping_country.data,
        payment_method=form.payment_method.data,
        order_notes=form.order_notes.data
    )
    db.session.add(order)
    db.session.flush()
    return order

def process_order_items(order, cart_items):
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            # price=item["price"]
        )
        db.session.add(order_item)

        product = Product.query.get(int(item["product"].id)) # Convert product id to int
        if product and product.stock >= item["quantity"]:
            product.stock -= item["quantity"]
            db.session.add(product)
        else:
            flash(
                f'Not enough stock for {item["product"].name}. Please adjust the quantity.',
                "danger",
            )
            return False
    return True