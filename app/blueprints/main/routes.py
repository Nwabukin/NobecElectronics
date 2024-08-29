import random
from flask import render_template, flash, redirect, url_for, request, current_app, abort
from app.blueprints.main import main
from app.blueprints.main.forms import ContactForm
from app.models import Product, Category

# Home Page Route
@main.route('/', endpoint='home')
@main.route('/home')
def home():
    """Renders the home page template."""
    # featured_products = Product.query.limit(8).all()
    all_products = Product.query.all()  
    categories = Category.query.all()
    featured_products = random.sample(all_products, min(8, len(all_products)))
    testimonials = [
        {
            'name': 'Sara Parker',
            'position': 'Customer',
            'text': 'Nobec Electronics has the best selection of electronics I\'ve ever seen. I found exactly what I was looking for and the prices were unbeatable!'
        },
        {
            'name': 'Mark Wilson',
            'position': 'Customer',
            'text': 'The customer service at Nobec Electronics is top-notch. They answered all my questions and helped me choose the perfect product for my needs.'
        }
    ]

    return render_template('main/home.html', title='Home', featured_products=featured_products, categories=categories, testimonials=testimonials)


@main.route('/about', endpoint='about')
def about():
    """Renders the about page template."""

    # Fetch team members' data (replace with actual data later)
    team_members = [
        {
            'name': 'John Doe', 
            'position': 'CEO', 
            'image_url': url_for('static', filename='team-member1.jpeg'), 
            'bio': 'A passionate leader with a vision to transform the electronics industry through innovation and customer-centricity.',
            'facebook_url': '#',  # Replace with actual URLs
            'twitter_url': '#',
            'linkedin_url': '#'
        },
        {
            'name': 'Jane Smith', 
            'position': 'CTO', 
            'image_url': url_for('static', filename='team-member1.jpeg'), 
            'bio': 'A tech visionary who leads our development team with expertise and creativity.',
            'facebook_url': '#',
            'twitter_url': '#',
            'linkedin_url': '#'
        },
        {
            'name': 'Michael Johnson',
            'position': 'Marketing Director',
            'image_url': url_for('static', filename='team-member1.jpeg'),
            'bio': 'A marketing guru with a knack for connecting with customers and building brand loyalty.',
            'facebook_url': '#',
            'twitter_url': '#',
            'linkedin_url': '#'
        }  
    ]

    # Testimonials Data (replace with actual testimonials later)
    testimonials = [
        {
            'name': 'Sarah Williams',
            'position': 'Satisfied Customer',
            'text': "I've been a loyal customer of Nobec Electronics for years. Their products are top-notch, and their customer service is always helpful and friendly."
        },
        {
            'name': 'David Brown',
            'position': 'Tech Enthusiast',
            'text': "Nobec Electronics is my go-to for all the latest gadgets. I love their selection and the fact that they always have competitive prices."
        },
    ]

    return render_template(
        'main/about.html', 
        title='About Us', 
        team_members=team_members,
        testimonials=testimonials
    )


# Contact Page Route
@main.route('/contact', methods=['GET', 'POST'], endpoint='contact')
def contact():
    """Handles contact form submission and renders the contact page."""
    form = ContactForm()
    if form.validate_on_submit():
        # Process contact form data (send email, etc.) - will be implemented later
        current_app.logger.info(
            f'Contact form submitted:\nName: {form.name.data}\nEmail: {form.email.data}\nMessage: {form.message.data}'
        )
        flash('Your message has been received! We will get back to you soon.', 'success')
        return redirect(url_for('main.home'))  # Redirect to home page after successful submission

    return render_template('main/contact.html', title='Contact', form=form)


# Shop Page Route
@main.route('/shop', endpoint='shop')
def shop():
    """Renders the shop page template with all products."""
    page = request.args.get('page', 1, type=int)  # Default to page 1
    per_page = current_app.config.get('PRODUCTS_PER_PAGE', 9) 
    products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('main/shop.html', title='Shop', products=products)


