import os
from PIL import Image  # For image resizing
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    abort,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.blueprints.admin import admin  # Import the admin blueprint
from app.models import Product, Category, db
from app.blueprints.products.forms import ProductForm

# Image upload configuration
#  = "uploads/products"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@admin.route('/')
@login_required
def index():
    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admins
    return render_template('admin/admin_index.html', title='Admin Dashboard')

@admin.route("/products")
@login_required
def manage_products():
    """View all products."""
    if not current_user.is_admin:
        abort(403)  

    page = request.args.get("page", 1, type=int)
    products = Product.query.paginate(page=page, per_page=current_app.config.get("ADMIN_PRODUCTS_PAGE", 10))
    return render_template('admin/products/products.html', title='Manage Products', products=products)

@admin.route("/products/new", methods=["GET", "POST"])
@login_required
def new_product():
    """Add a new product."""
    if not current_user.is_admin:
        abort(403)

    form = ProductForm()
    categories = Category.query.all()
    form.category.choices = [(c.id, c.name) for c in categories]
    
    if request.method == "POST":
        print("Form submitted:", request.form)
        
    if form.validate_on_submit():
        print("Form validated successfully")
        # Image Handling
        if form.image.data:
            if allowed_file(form.image.data.filename):
                image_filename = secure_filename(form.image.data.filename)
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
                os.makedirs(upload_path, exist_ok=True)
                form.image.data.save(os.path.join(upload_path, image_filename))
                
                # Resize the image
                img = Image.open(os.path.join(upload_path, image_filename))
                img.thumbnail((400, 400))
                img.save(os.path.join(upload_path, image_filename))
            else:
                flash('Invalid file type. Allowed types are png, jpg, jpeg.', 'danger')
                return redirect(url_for('admin.add_product'))
        else:
            filename = None  # No image uploaded

        # Create a new product instance and save it to the database
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category_id=form.category.data,
            image_url=image_filename,
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.manage_products'))
    return render_template('admin/products/new_product.html', title='Add Product', form=form)

# Edit Product Route
@admin.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Allows admin to edit an existing product."""

    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admins

    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)  # Pre-populate the form

    if form.validate_on_submit():
        # Handle image upload (if provided)
        if form.image.data:
            if allowed_file(form.image.data.filename):
                filename = secure_filename(form.image.data.filename)
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
                os.makedirs(upload_path, exist_ok=True)

                # Delete old image if it exists
                if product.image_url:
                    old_image_path = os.path.join(upload_path, product.image_url)
                    try:
                        os.remove(old_image_path)
                    except FileNotFoundError:
                        pass  # Ignore if the old image doesn't exist

                # Save and resize the new image
                img = Image.open(form.image.data)
                img.thumbnail((400, 400)) 
                img.save(os.path.join(upload_path, filename))

                product.image_url = filename
            else:
                flash('Invalid file type. Allowed types are png, jpg, jpeg.', 'danger')
                return redirect(request.url)

        # Update other fields
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.category_id = form.category.data
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.manage_products', product_id=product.id))

    return render_template('admin/products/new_product.html', title='Edit Product', form=form, product=product)


# Delete Product Route
@admin.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    """Deletes a product."""
    if not current_user.is_admin:
        abort(403)

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.manage_products')) 
