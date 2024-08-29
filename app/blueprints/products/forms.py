from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed  # For image uploads
from wtforms import StringField, SubmitField, TextAreaField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Optional, Length
from app.models import Category


class ProductForm(FlaskForm):
    """Form for adding or editing a product."""

    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField("Category", coerce=int, validators=[DataRequired()])
    image_url = StringField("Image URL") 
    image = FileField(
        "Image",
        validators=[FileAllowed(["jpg", "png", "jpeg"], "Images only!")],  # Image validation
    )
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and populate the category choices.
        """
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.all()]

class AddCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])  # Optional description
    image = FileField(
        "Image",
        validators=[FileAllowed(["jpg", "png", "jpeg"], "Images only!")],  # Image validation
    )
    submit = SubmitField('Add Category')
    
    def validate_name(self, name):
        """Custom validator to check if category name is unique."""
        category = Category.query.filter_by(name=name.data).first()
        if category is not None:
            raise ValidationError('Please use a different category name.')

class EditCategoryForm(FlaskForm):
    """Form for editing a product category."""

    new_name = StringField('New Category Name', validators=[Optional(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])
    image = FileField(
        "New Image",
        validators=[FileAllowed(["jpg", "png", "jpeg"], "Images only!"), Optional()],  # Image validation
    )
    submit = SubmitField('Save Changes')

    def __init__(self, original_name, *args, **kwargs):
        """
        Initialize the form and populate the category choices.
        """
        super(EditCategoryForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_new_name(self, new_name):
        """Custom validator to check if category name is unique."""
        if new_name.data != self.original_name:
            category = Category.query.filter_by(name=new_name.data).first()
            if category is not None:
                raise ValidationError('Please use a different category name.')