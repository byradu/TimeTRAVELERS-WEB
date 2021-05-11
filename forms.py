from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import TextAreaField,SubmitField
from wtforms.validators import DataRequired,Optional

class inputText(FlaskForm):
    inputText = TextAreaField('Introduceti textul dumneavoastra aici',validators=[Optional()])
    fileInput = FileField('Introduceti fisierul',validators=[Optional(),FileAllowed(['pdf','txt'])] )
    submit = SubmitField('Start!')

class resultsInput(FlaskForm):
    inputText = TextAreaField('Inserati textul',validators=[Optional()])
    submit = SubmitField('Start!')