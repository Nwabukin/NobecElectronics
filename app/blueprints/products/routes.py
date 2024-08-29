import os
from flask import (
    render_template,
    request,
    current_app,
    abort,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from PIL import Image  # For image resizing


from app.blueprints.products import products
from app.models import Product, Category, db  # Import your database and models
from app.blueprints.products.forms import ProductForm

# Image upload configuration (adjust path as needed)
UPLOAD_FOLDER = "app/static/uploads/products"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@products.route('/', methods=['GET', 'POST'])
@products.route('/products')
def all_products():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('PRODUCTS_PER_PAGE', 9) 
    search_query = request.args.get('q', '') 
    category_id = request.args.get('category_id', None, type=int)
    sort_by = request.args.get('sort_by', 'name_asc')

    query = Product.query
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)

    # Apply sorting to the query
    if sort_by == 'name_desc':
        query = query.order_by(Product.name.desc())
    elif sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:  # Default or invalid sort_by
        query = query.order_by(Product.name.asc())

    products = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        'products/products.html', 
        title='Products', 
        products=products, 
        categories=Category.query.all(), 
        search_query=search_query, 
        selected_category=category_id, 
        sort_by=sort_by,               
    )


@products.route("/product/<int:product_id>")
def product_detail(product_id):
    """Displays the details of a single product."""

    product = Product.query.get_or_404(product_id)
    if product.stock == 0:
        flash("This product is currently out of stock.", "warning")
    return render_template(
        "products/product_detail.html", title=product.name, product=product
    )


@products.route("/category/<int:category_id>")
def category(category_id):
    """Displays products in a specific category."""
    category = Category.query.get_or_404(category_id)
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("PRODUCTS_PER_PAGE", 9)
    products = Product.query.filter_by(category_id=category_id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template(
        "products/category.html",
        title=category.name,
        category=category,
        products=products,
    )

#Add product
@products.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Allows admin to add a new product."""
    from app import app
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admins

    form = ProductForm()
    if form.validate_on_submit():
        # Handle image upload (if provided)
        if form.image.data:
            if allowed_file(form.image.data.filename):
                filename = secure_filename(form.image.data.filename)

                # Create UPLOAD_FOLDER if it doesn't exist
                upload_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
                os.makedirs(upload_path, exist_ok=True)

                # Resize and save the image (adjust sizes as needed)
                img = Image.open(form.image.data)
                img.thumbnail((400, 400))  # Thumbnail size
                img.save(os.path.join(upload_path, filename))
            else:
                flash('Invalid file type. Allowed types are png, jpg, jpeg.', 'danger')
                return redirect(request.url)  # Redirect back to the form
        else:
            filename = None  # No image uploaded

        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category_id=form.category.data,
            image_url=filename,
        )
        db.session.add(product)
        db.session.commit()

        flash('Product added successfully!', 'success')
        return redirect(url_for('products.all_products')) 

    return render_template('products/add_product.html', title='Add Product', form=form)


# Edit Product Route
@products.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Allows admin to edit an existing product."""
    from app import app
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admins

    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)  # Pre-populate the form

    if form.validate_on_submit():
        # Handle image upload (if provided)
        if form.image.data:
            if allowed_file(form.image.data.filename):
                filename = secure_filename(form.image.data.filename)
                upload_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
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
        return redirect(url_for('products.product_detail', product_id=product.id))

    return render_template('products/edit_product.html', title='Edit Product', form=form, product=product)

# Delete Product Route
@products.route('/delete/<int:product_id>')
@login_required
def delete_product(product_id):
    """Allows admin to delete a product."""

    if not current_user.is_admin:
        abort(403)

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.all_products')) 