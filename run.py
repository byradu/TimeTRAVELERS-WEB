from flask import Flask,render_template,url_for,redirect,request
from jinja2.utils import generate_lorem_ipsum
from forms import inputText

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd1c8efd030c6d6c85a46bde85c2597805cf6c18bf1f40dbbfb7fc740d38b1113'

@app.route('/',methods = ['POST','GET'])
def home():
    form = inputText()
    if form.validate_on_submit():
        return redirect(url_for('results',userInput=form.inputText.data))
    return render_template('index.html',form = form)

@app.route('/results/')
def results():
    data = request.args.get('userInput')
    #prelucrare data
    return render_template('results.html',data=data)

if __name__ == '__main__':
    app.run(debug=True)