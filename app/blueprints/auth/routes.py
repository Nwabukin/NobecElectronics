import os
from PIL import Image  # For image resizing
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import Order
from app import db

from . import auth
from .forms import LoginForm, RegistrationForm, EditProfileForm

# Configuration for image uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
UPLOAD_FOLDER = 'app/static/uploads/profile_pics'

# Check if file has an allowed extension
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@auth.route("/register", methods=["GET", "POST"], endpoint = 'register')
def register():
    from app.models import User  # Import the model inside the function

    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the password
        hashed_password = generate_password_hash(form.password.data)

        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            street_address=form.street_address.data,
            city=form.city.data,
            state=form.state.data,
            country=form.country.data,
            postal_code=form.postal_code.data,
            phone_number=form.phone_number.data,
            password_hash=hashed_password
            # ... other fields you added to the User model
        )
        db.session.add(user)
        db.session.commit()

        flash("Congratulations, you are now a registered user!", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", title="Register", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    from app.models import User  # Import the model inside the function

    if current_user.is_authenticated:
        return redirect(url_for("main.home"))  # Redirect if already logged in

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):  # Check hashed password
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")  # Handle 'next' parameter
            return (
                redirect(next_page)
                if next_page
                else redirect(url_for("main.home"))  # Redirect to home if next is not set
            )
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("auth/login.html", title="Login", form=form)


@auth.route("/logout")
@login_required  # Require login to access this route
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


@auth.route('/dashboard')
@login_required
def dashboard():
    user_orders = Order.query.filter_by(customer_id=current_user.id).all()
    return render_template('auth/dashboard.html', title='Dashboard', user_orders=user_orders)



@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    from app import db # Import database here to prevent circular import
    from app.models import User
    form = EditProfileForm(original_username=current_user.username, original_email=current_user.email, obj=current_user)

    if form.validate_on_submit():
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                # Delete old profile picture if it exists or "delete" is checked
                if current_user.profile_picture:
                    old_image_path = os.path.join(current_app.root_path, 'app', 'static', 'uploads', 'profile_pics', current_user.profile_picture)
                    try:
                        os.remove(old_image_path)
                    except FileNotFoundError:
                        pass  # Ignore error if file doesn't exist

                # Save the new profile picture (if a new file was uploaded)
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics')
                    file.save(os.path.join(upload_path, filename))
                    current_user.profile_picture = filename  
                else:
                    # Remove the profile picture if the checkbox was checked
                    current_user.profile_picture = None

        # Update user's other fields (username, email, etc.)
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.street_address = form.street_address.data
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.country = form.country.data
        current_user.postal_code = form.postal_code.data
        current_user.phone_number = form.phone_number.data
        current_user.about_me = form.about_me.data 

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('auth.dashboard'))

    return render_template('auth/edit_profile.html', title='Edit Profile', form=form)
    
    