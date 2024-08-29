from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, request, jsonify, abort
from app.blueprints.cart import cart
from app.models import Product, db 


# Initialize an empty cart in the session if it doesn't exist
@cart.before_app_request
def initialize_cart():
    if 'cart' not in session:
        session['cart'] = {}

# Route to view the cart
@cart.route('/cart', endpoint = 'view_cart')
def view_cart():
    """Displays the contents of the shopping cart."""
    cart_items = []
    total_price = 0
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            item_price = product.price * quantity
            cart_items.append({'product': product, 'quantity': quantity, 'price': item_price, 'product_id': product_id}) #Add the product id here
            total_price += item_price

    if not cart_items:
        flash('Your cart is empty. Please add some items before checking out.', 'warning')
        return redirect(url_for('products.all_products')) 
    return render_template('cart/cart.html', cart_items=cart_items, total_price=total_price)


# Route to add an item to the cart
@cart.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    """Adds a product to the shopping cart."""
    
     # Check if product exists
    product = Product.query.get(product_id)
    if not product:
        abort(404)  
    
    # Convert product_id to string
    product_id_str = str(product_id)

    if product_id_str in session.get('cart', {}):
        session['cart'][product_id_str] += 1  # Increment quantity if product is already in cart
    else:
        session['cart'][product_id_str] = 1  # Add product to cart with quantity 1
    
    flash('Product added to cart!', 'success')


    # You can redirect to the cart or the product page
    return redirect(url_for('products.product_detail', product_id=product_id))

@cart.route('/remove_from_cart/<int:product_id>', methods=['GET', 'POST'])
def remove_from_cart(product_id):
    """Removes a product from the shopping cart."""
    #convert product_id to string since that is how it is saved to the session variable
    product_id = str(product_id)
    
    if 'cart' not in session or product_id not in session['cart']:
        return redirect(url_for('cart.view_cart'))
   
    del session['cart'][product_id] 
    flash('Product removed from cart.', 'success')
    return redirect(url_for('cart.view_cart'))



# Route to update the quantity of an item in the cart
@cart.route('/update_cart/<product_id>', methods=['POST'])
def update_cart(product_id):
    """Updates the quantity of a product in the cart."""

    if 'cart' not in session or product_id not in session['cart']:
        return redirect(url_for('cart.view_cart'))

    new_quantity = int(request.form.get('quantity', 0))  # Get quantity, default to 0 if not found

    if new_quantity <= 0:
        del session['cart'][product_id]
        flash('Product removed from cart.', 'info')
    else:
        session['cart'][product_id] = new_quantity
        flash('Cart updated.', 'success')

    return redirect(url_for('cart.view_cart'))