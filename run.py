from flask import Flask,render_template,url_for,redirect,request
from forms import inputText
import secrets,os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd1c8efd030c6d6c85a46bde85c2597805cf6c18bf1f40dbbfb7fc740d38b1113'

def save(f):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(f.filename)
    saveF = random_hex + f_ext
    filepath = os.path.join(app.root_path,saveF)
    f.save(filepath)
    return filepath

@app.route('/',methods = ['POST','GET'])
def home():
    form = inputText()
    if form.validate_on_submit():
        print(form.fileInput.data)
        print(form.inputText.data)
        
        #prelucrare
        if form.fileInput.data != None:#daca e poza
            to_remove_after_process_it = save(form.fileInput.data)#salvare pdf sau txt
            return redirect(url_for('results',userInput=to_remove_after_process_it,mode=0))
        elif form.inputText.data != '':#atunci e input manual
            return redirect(url_for('results',userInput=form.inputText.data,mode=1))
    return render_template('index.html',form = form)

@app.route('/results/')
def results():
    mode = request.args.get('mode')
    data = request.args.get('userInput')
    #prelucrare data
    # if mode == 1:
    return render_template('results.html',data=data)
    # else :
        # return render_template('results.html',data="....")
if __name__ == '__main__':
    app.run(debug=True)