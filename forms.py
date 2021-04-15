from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import TextAreaField,SubmitField
from wtforms.validators import DataRequired,Optional

class inputText(FlaskForm):
    inputText = TextAreaField('Insert text to process',validators=[Optional()])
    fileInput = FileField('Insert your file here',validators=[Optional(),FileAllowed(['pdf','txt'])] )
    submit = SubmitField('Start!')