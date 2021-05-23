from flask import Flask,render_template,url_for,redirect,request,send_file,send_from_directory
from forms import inputText, resultsInput
import secrets,os,re,cv2 as cv,numpy as np
from datetime import datetime
from templates.pysyntime import SynTime, syntime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'd1c8efd030c6d6c85a46bde85c2597805cf6c18bf1f40dbbfb7fc740d38b1113'


IMAGE_FOLDER=os.path.join('static')
app.config['UPLOAD_FOLDER']=IMAGE_FOLDER
loading_gif=os.path.join(app.config['UPLOAD_FOLDER'],'spinner2.gif')

evenimente = []
numepdf = ''
images_data = []
imgs = []

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
    from pytesseract import image_to_data,Output
    import cv2 as cv
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    images = convert_from_path(numePdf,poppler_path=r'C:\Program Files\poppler-0.68.0\bin')
    extractedText = ''
    global images_data,imgs
    images_data = []
    imgs = []
    for i in images:
        imgs.append(cv.cvtColor(np.array(i),cv.COLOR_RGB2BGR))
        d = pytesseract.image_to_data(i,output_type=Output.DICT,lang='eng+ron+equ',config="--psm 6")
        images_data.append(d)
        n = len(d['level'])
        for j in range(n):
            extractedText = extractedText + d['text'][j] + ' '
    
    return extractedText

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'logo_fii3.png', mimetype='image/vnd.microsoft.icon')

def createMarkedPdf(nume,functionEvent): #salvarea pdf-ului marcat
    from pdf2image import convert_from_path
    import pytesseract
    from pytesseract import Output
    from PIL import Image
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    try:
        os.remove('result.pdf')        
    except :
        pass
    first_page = 0
    ok = 0 
    restOfThePages = []
    for i,img in zip(images_data,imgs):
        boxes = len(i['level'])
        for e in functionEvent:
            for j in range(boxes):
                if e in i['text'][j]:
                    (x,y,w,h) = (i['left'][j],i['top'][j],i['width'][j],i['height'][j])
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                elif j+1<boxes:
                    if e in (i['text'][j]+' '+i['text'][j+1] or i['text'][j]+i['text'][j+1]):
                        (x,y,w,h) = (min(i['left'][j],i['left'][j+1]),max(i['top'][j],i['top'][j+1]),max(i['width'][j],i['width'][j+1]),max(i['height'][j],i['height'][j+1]))
                        cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)
        restOfThePages.append(im_pil)
        if ok == 0:
            ok = 1
            first_page = im_pil
    first_page.save('results.pdf',"PDF",resolution=100.0,save_all=True,append_images=restOfThePages[1:])



@app.route('/',methods = ['POST','GET'])
def home():
    
    form = inputText()
    if form.validate_on_submit():
        
        #prelucrare
        if form.fileInput.data != None:#daca e pdf
            to_remove_after_process_it = save(form.fileInput.data)#salvare pdf sau txt
            if '.txt' in to_remove_after_process_it:
                with open(to_remove_after_process_it,'rb') as f:
                    textdintxt = f.read()
                    return redirect(url_for('results',userInput=textdintxt))        
            else:
                return redirect(url_for('results',userInput=to_remove_after_process_it))
        elif form.inputText.data != '':#atunci e input manual
            return redirect(url_for('results',userInput=form.inputText.data))
    return render_template('index.html',form = form,loading_gif=loading_gif)

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
        return render_template('results.html',data=textdinpdf,form = form,loading_gif=loading_gif)
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
    print(evenimente)
    if numepdf == '':
        return render_template('output.html',data=data,pdf=0,events=events)
    else:    
        createMarkedPdf(numepdf,evenimente)
        return render_template('output.html',data=data,pdf=1,nume='results.pdf',events=events)

@app.route('/download', methods=['GET'])
def download():
    file="templates/pysyntime/resource/outputXML.xml"
    print(os.getcwd())
    return send_file(file,mimetype='text/xml',as_attachment=True)

@app.route('/downloadpdf',methods=['GET'])
def downloadpdf():
    file="results.pdf"
    print(os.getcwd())
    return send_file(file,mimetype='application/pdf',as_attachment=True)

@app.route('/pdf/<numepdf>')
def showpdf(numepdf):
    filepath = os.path.split(numepdf)
    return send_from_directory(filepath[0], filepath[1])

if __name__ == '__main__':
    app.run(debug=True)