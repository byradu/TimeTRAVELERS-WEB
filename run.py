from flask import Flask,render_template,url_for,redirect,request,send_file,send_from_directory
from forms import inputText, resultsInput
import secrets,os,re
from datetime import datetime
from templates.pysyntime import SynTime, syntime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'd1c8efd030c6d6c85a46bde85c2597805cf6c18bf1f40dbbfb7fc740d38b1113'

evenimente = []

def save(f):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(f.filename)
    saveF = random_hex + f_ext
    filepath = os.path.join(app.root_path,saveF)
    f.save(filepath)
    return filepath

def readevents():
    import json
    with open('events.json') as f:
        content = f.read()
    js = json.loads(content)
    return js

def getTextFromPdf(numePdf):
    from pdf2image import convert_from_path
    import pytesseract
    from pytesseract import image_to_string
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    images = convert_from_path(numePdf,poppler_path=r'C:\Program Files\poppler-0.68.0\bin') 
    extractedText = ''
    for i in images:
        extractedText = extractedText + image_to_string(images[0],lang='ron+equ',config="--psm 6") + ' '
    
    return extractedText

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'logo_fii3.png', mimetype='image/vnd.microsoft.icon')

@app.route('/',methods = ['POST','GET'])
def home():
    form = inputText()
    if form.validate_on_submit():
        
        #prelucrare
        if form.fileInput.data != None:#daca e pdf
            to_remove_after_process_it = save(form.fileInput.data)#salvare pdf sau txt
            return redirect(url_for('results',userInput=to_remove_after_process_it))
        elif form.inputText.data != '':#atunci e input manual
            # print(form.inputText.data)
            return redirect(url_for('results',userInput=form.inputText.data))
    return render_template('index.html',form = form)

@app.route('/results/',methods =  ['POST','GET'])
def results():
    global evenimente
    syntime = SynTime()
    date = datetime.today().strftime("%d-%m-%Y")
    data = request.args.get('userInput')
    if '.pdf' in data:
        textdinpdf = getTextFromPdf(data)
        # print(timeMLText)
        form = resultsInput()
        if form.validate_on_submit():
            #prelucrare 
            timeMLText,evenimente = syntime.extractTimexFromText(form.inputText.data, date)
            return redirect(url_for('output',data=timeMLText,pdf = data))
        return render_template('results.html',data=textdinpdf,form=form)
    elif data != '':
        timeMLText,evenimente = syntime.extractTimexFromText(data, date)
        # print(evenimente)
        return redirect(url_for('output',data=timeMLText,pdf=''))
    # filesToDelete.append(data)
    
@app.route('/output/')
def output():
    listaEvenimente = readevents()
    data = request.args.get('data')
    numepdf = request.args.get('pdf')
    events ={}
    for i in evenimente:
        an = re.findall(r"(?<!\d)\d{4}(?!\d)",i)
        try:
            if an[0] in listaEvenimente:
                events[an[0]] = listaEvenimente[an[0]]
        except:
            pass

    events = dict(sorted(events.items()))
    if numepdf == '':
        return render_template('output.html',data=data,pdf=0,events=events)
    else:    
        return render_template('output.html',data=data,pdf=1,nume=numepdf,events=events)

@app.route('/download', methods=['GET'])
def download():
    file="templates/pysyntime/resource/outputXML.xml"
    print(os.getcwd())
    return send_file(file,mimetype='text/xml',as_attachment=True)

@app.route('/pdf/<numepdf>')
def showpdf(numepdf):
    filepath = os.path.split(numepdf)
    return send_from_directory(filepath[0], filepath[1])

if __name__ == '__main__':
    app.run(debug=True)