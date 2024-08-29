from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email

class CheckoutForm(FlaskForm):
    shipping_first_name = StringField('First Name', validators=[DataRequired()])
    shipping_last_name = StringField('Last Name', validators=[DataRequired()])
    shipping_address = StringField('Address', validators=[DataRequired()])
    shipping_city = StringField('City', validators=[DataRequired()])
    shipping_state = StringField('State', validators=[DataRequired()])
    shipping_postal_code = StringField('Postal Code', validators=[DataRequired()])
    shipping_country = StringField('Country', validators=[DataRequired()])

    same_as_shipping = BooleanField('Same as shipping address')
    
    billing_first_name = StringField('First Name')
    billing_last_name = StringField('Last Name')
    billing_address = StringField('Address')
    billing_city = StringField('City')
    billing_state = StringField('State')
    billing_postal_code = StringField('Postal Code')
    billing_country = StringField('Country')

    payment_method = RadioField('Payment Method', choices=[('Bank Transfer', 'Bank Transfer'), ('Cash on Delivery', 'Cash on Delivery')], validators=[DataRequired()])
    
    order_notes = TextAreaField('Order Notes')
    
    submit = SubmitField('Place Order')