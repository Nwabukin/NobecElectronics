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
from app.models import Category, Product, db
from app.blueprints.products.forms import AddCategoryForm, EditCategoryForm


# ... allowed file definition
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route("/categories", methods=["GET", "POST"])
@login_required
def manage_categories():
    """Displays a list of all categories and handles adding new categories."""
    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admins

    add_form = AddCategoryForm()
    if add_form.validate_on_submit():
        # Handle image upload (if provided)
        if add_form.image.data:
            if allowed_file(add_form.image.data.filename):
                filename = secure_filename(add_form.image.data.filename)
                image_path = os.path.join(
                    current_app.root_path,'static', 'uploads', 'categories', filename
                )
                add_form.image.data.save(image_path)
                # Resize Image
                img = Image.open(image_path)
                img.thumbnail((400, 400))  
                img.save(image_path)
            else:
                flash(
                    "Invalid file type. Allowed types are png, jpg, jpeg.", "danger"
                )
                return redirect(request.url)  # Redirect back to the form
        else:
            filename = None  # No image uploaded

        category = Category(
            name=add_form.name.data,
            description=add_form.description.data,
            image_url=filename,
        )
        db.session.add(category)
        db.session.commit()

        flash("Category added successfully!", "success")
        return redirect(url_for("admin.manage_categories"))

    categories = Category.query.all()
    edit_form = EditCategoryForm(original_name="")

    if request.method == "POST" and not add_form.validate_on_submit():
        category_id = request.form.get("category")  # Get selected category ID
        if category_id:
            category = Category.query.get_or_404(category_id)
            edit_form = EditCategoryForm(obj=category, original_name=category.name)

    return render_template(
        "admin/categories/categories.html",
        title="Manage Categories",
        categories=categories,
        add_category_form=add_form,
        edit_category_form=edit_form,
    )


@admin.route('/category/new', methods=['GET', 'POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        abort(403)
    form = AddCategoryForm()


    # Modify the submit button text
    form.submit.label.text = "Add Category"
    
    
    if form.validate_on_submit():
        # Check if category name already exists
        existing_category = Category.query.filter_by(name=form.name.data).first()
        if existing_category:
            flash('Category already exists', 'danger')
        else:
            # Handle image upload (if provided)
            filename = None
            if form.image.data:
                if allowed_file(form.image.data.filename):
                    filename = secure_filename(form.image.data.filename)
                    #create the directory where the category images will be stored if it doesn't already exist
                    os.makedirs(current_app.root_path,'static', 'uploads', 'categories', exist_ok=True)  
                    image_path = os.path.join(current_app.root_path, 'static', 'uploads', 'categories', filename)
                    form.image.data.save(image_path)
                    # Resize Image
                    img = Image.open(image_path)
                    img.thumbnail((400, 400))  # Resize to 400x400
                    img.save(image_path)
                else:
                    flash('Invalid file type. Allowed types are png, jpg, jpeg.', 'danger')
                    return redirect(request.url)  # Redirect back to the form


            new_category = Category(name=form.name.data, description=form.description.data, image_url=filename)  
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')

        return redirect(url_for('admin.manage_categories'))

    return render_template('admin/categories/new_category.html', title='Add New Category', form=form)



@admin.route("/category/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    """View function to edit a category."""
    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admins

    category = Category.query.get_or_404(category_id)
    form = EditCategoryForm(original_name=category.name, obj=category)

    if form.validate_on_submit():
        # Check for duplicate category name
        if (
            form.new_name.data.lower() != category.name.lower()
            and Category.query.filter_by(name=form.new_name.data.lower()).first()
        ):
            flash("Category name already exists.", "danger")
            return redirect(url_for("admin.edit_category", category_id=category_id))
            
        # Handle image upload (if provided)
        if form.image.data:
            file = form.image.data # Get the file data from the form
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(current_app.root_path, 'static', 'uploads', 'categories', filename)
                file.save(image_path)  # Save the file
                # Resize Image
                img = Image.open(image_path)
                img.thumbnail((400, 400)) 
                img.save(image_path)
                category.image_url = filename

                # Delete old image (if it exists and a new file is uploaded)
                if category.image_url and file.filename != "":
                    old_image_path = os.path.join(
                        current_app.root_path, 'static', 'uploads', 'categories',
                        category.image_url,
                    )
                    try:
                        os.remove(old_image_path)
                    except FileNotFoundError:
                        pass  # Ignore error if file doesn't exist
                
        # If no image is selected and the field is empty, clear the image_url
        elif form.image.data and not form.image.data.filename: 
            category.image_url = None

        # Update other fields (name, description)
        category.name = form.new_name.data
        category.description = form.description.data
        
        db.session.commit()

        flash("Category updated successfully!", "success")
        return redirect(url_for("admin.manage_categories"))

    return render_template(
        "admin/categories/new_category.html",
        title="Edit Category",
        form=form,
        category=category,
    )



@admin.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        abort(403)

    category = Category.query.get_or_404(category_id)

    # Check if the category has any associated products
    associated_products = Product.query.filter_by(category_id=category.id).all()
    if associated_products:
        # If the category has associated products, display a warning message and redirect back to the categories page
        flash(f"Cannot delete category '{category.name}' as it has associated products.", "danger")
        return redirect(url_for('admin.manage_categories'))

    db.session.delete(category)
    db.session.commit()

    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin.manage_categories'))