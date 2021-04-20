from flask import Flask,render_template,url_for,redirect,request
from forms import inputText
import secrets,os
import PyPDF2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd1c8efd030c6d6c85a46bde85c2597805cf6c18bf1f40dbbfb7fc740d38b1113'


def save(f):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(f.filename)
    saveF = random_hex + f_ext
    filepath = os.path.join(app.root_path,saveF)
    f.save(filepath)
    return filepath

def getTextFromPdf(numePdf):
    file = open(numePdf, "rb")
    reader = PyPDF2.PdfFileReader(file)
    # fileToWrite = open("pdf.txt", "a+")
    extractedText = ''
    for i in range(0, reader.numPages):
        extractedText += '' + reader.getPage(i).extractText()
    return extractedText


@app.route('/',methods = ['POST','GET'])
def home():
    form = inputText()
    if form.validate_on_submit():
        print(form.fileInput.data)
        print(form.inputText.data)
        
        #prelucrare
        if form.fileInput.data != None:#daca e pdf
            to_remove_after_process_it = save(form.fileInput.data)#salvare pdf sau txt
            return redirect(url_for('results',userInput=to_remove_after_process_it))
        elif form.inputText.data != '':#atunci e input manual
            return redirect(url_for('results',userInput=form.inputText.data))
    return render_template('index.html',form = form)

@app.route('/results/')
def results():
    data = request.args.get('userInput')
    if '.pdf' in data:
        textdinpdf = getTextFromPdf(data)
        print(textdinpdf)
        return render_template('results.html',data=textdinpdf)
    else:
        return render_template('results.html',data=data)
    # filesToDelete.append(data)
if __name__ == '__main__':
    app.run(debug=True)