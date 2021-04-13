from flask_wtf import FlaskForm
from wtforms import TextAreaField,SubmitField
from wtforms.validators import DataRequired

class inputText(FlaskForm):
    inputText = TextAreaField('Insert text to process',validators=[DataRequired()])
    submit = SubmitField('Start!')