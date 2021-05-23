from flask import Flask,render_template,url_for,redirect,request,send_file,send_from_directory
from forms import inputText, resultsInput
import secrets,os,re,cv2 as cv,numpy as np
from datetime import datetime
from templates.pysyntime import SynTime, syntime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'd1c8efd030c6d6c85a46bde85c2597805cf6c18bf1f40dbbfb7fc740d38b1113'

evenimente = []
numepdf = ''

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
    from pytesseract import image_to_string,Output
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    images = convert_from_path(numePdf,poppler_path=r'C:\Program Files\poppler-0.68.0\bin')
    extractedText = ''
    for i in images:
        extractedText = extractedText + image_to_string(i,lang='ron+equ',config="--psm 6") + ' '
    
    return extractedText

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'logo_fii3.png', mimetype='image/vnd.microsoft.icon')

def createMarkedPdf(nume,functionEvent): #salvarea pdf-ului marcat
    from pdf2image import convert_from_path
    import pytesseract
    from pytesseract import Output
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    images = convert_from_path(nume,poppler_path=r'C:\Program Files\poppler-0.68.0\bin')

    for i in images:
        img = cv.cvtColor(np.array(images[0]),cv.COLOR_RGB2BGR)
        d = pytesseract.image_to_data(img,output_type=Output.DICT,lang='eng+ron+equ',config="--psm 6")
        boxes = len(d['level'])
        for i in range(boxes):
            for e in functionEvent:
                if e in d['text'][i]:
                    (x,y,w,h) = (d['left'][i],d['top'][i],d['width'][i],d['height'][i])
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                elif i+1<boxes:
                    if e in d['text'][i]+d['text'][i+1]:
                        (x,y,w,h) = (max(d['left'][i],d['left'][i+1]),max(d['top'][i],d['top'][i+1]),max(d['width'][i],d['width'][i+1]),max(d['height'][i],d['height'][i+1]))
                        cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        pdf = pytesseract.image_to_pdf_or_hocr(img,extension='pdf')
        with open('results.pdf','w+b') as f:
            f.write(pdf)



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
    global evenimente,numepdf
    syntime = SynTime()
    date = datetime.today().strftime("%d-%m-%Y")
    data = request.args.get('userInput')
    numepdf = data
    if '.pdf' in data:
        textdinpdf = getTextFromPdf(data)
        # print(timeMLText)
        form = resultsInput()
        if form.validate_on_submit():
            #prelucrare 
            try:
                timeMLText,evenimente = syntime.extractTimexFromText(form.inputText.data, date)
            except :
                timeMLText = syntime.extractTimexFromText(form.inputText.data, date)
            return redirect(url_for('output',data=timeMLText,pdf = data))
        return render_template('results.html',data=textdinpdf,form=form)
    elif data != '':
        try:            
            timeMLText,evenimente = syntime.extractTimexFromText(data, date)
        except :
            timeMLText = syntime.extractTimexFromText(data, date)
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
    createMarkedPdf(numepdf,evenimente)
    if numepdf == '':
        return render_template('output.html',data=data,pdf=0,events=events)
    else:    
        return render_template('output.html',data=data,pdf=1,nume='results.pdf',events=events)

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