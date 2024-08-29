from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from flask_login import login_required, current_user
from app.blueprints.admin import admin  # Import the admin blueprint
from app.models import Order, OrderItem, User, db
from app.blueprints.auth.forms import EditProfileForm 



@admin.route('/orders')
@login_required
def manage_orders():
    """Displays a list of all orders."""
    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admins

    page = request.args.get('page', 1, type=int)  # Get page number for pagination
    per_page = 10  # Number of orders to display per page

    orders = Order.query.paginate(page=page, per_page=per_page, error_out=False) 
    return render_template('admin/orders/orders.html', title='Manage Orders', orders=orders)

@admin.route('/order/<int:order_id>')
@login_required
def view_order_details(order_id):
    """Displays details of a single order."""
    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admins

    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()  
    #  Fetch items related to the order

    return render_template(
        'admin/orders/order_details.html', 
        title='Order Details', 
        order=order,
        order_items=order_items
    )

@admin.route('/users')
@login_required
def manage_users():
    """Displays a list of all users with actions (edit, delete)."""
    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admins

    page = request.args.get('page', 1, type=int)  # Get page number for pagination
    per_page = 10  # Number of users to display per page

    users = User.query.paginate(page=page, per_page=per_page, error_out=False) 
    return render_template(
        'admin/users/users.html',  
        title='Manage Users',
        users=users
    )

@admin.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Allows an admin to edit a user's details."""

    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admins

    user = User.query.get_or_404(user_id)  # Fetch the user from the database
    form = EditProfileForm(original_username=user.username, original_email=user.email, obj=user)

    if form.validate_on_submit():
        # Check for duplicate usernames/emails (excluding the current user)
        if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Update the user's information
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.street_address = form.street_address.data
        user.city = form.city.data
        user.state = form.state.data
        user.country = form.country.data
        user.postal_code = form.postal_code.data
        user.phone_number = form.phone_number.data
        user.about_me = form.about_me.data 

        # Save changes to the database
        db.session.commit()

        flash('User details updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    # Handle GET requests to pre-populate the form
    return render_template('admin/users/edit_user.html', title='Edit User', form=form, user=user)