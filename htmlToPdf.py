from xhtml2pdf import pisa
from jinja2 import Template
import datetime

def convertHtmlToPdf(data): 
    print('prueba')
    outputFilename = "static/test.pdf"
    texto = 'esto es un ejemplo de texto'
    data = {
            'lat' : data['lat'], 
            'lng': data['lng'], 
            'alt': 0,
            'lugar': texto,
            'municipio': data['municipio'],
            'provincia': data['provincia'],
            'fechas': data['fechas'],
            'hoy': datetime.datetime.now().strftime('%d/%m/%Y')
            } 

    resultFile = open(outputFilename, "w+b")
    template = Template(open('static/template.html').read()) 
    html  = template.render(data) 

    pisaStatus = pisa.CreatePDF(
            html,
            dest=resultFile)
    resultFile.close()
    return pisaStatus.err


