from flask import Flask, render_template, send_file, redirect
from flask_socketio import SocketIO
from flask_socketio import emit
import datetime
import math 
import metpy.calc
from metpy.units import units
import matplotlib.pyplot as plt
from xhtml2pdf import pisa
from jinja2 import Template
from radiosondeo import *
from municipios import *
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

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def root():
    return render_template('mapa.html')

@app.route('/download')
def download():
    return send_file('static/test.pdf', as_attachment=True)
    
@socketio.on('localizacion')
def handle_loc( data ):
    #meteograma([data['lng'], data['lat']])
    fechas = radiosondeo(data['lat'], data['lng'])
    municipio, provincia = get_municipio( data['lat'], data['lng'] )
    datos = {
            'lat': data['lat'],
            'lng': data['lng'],
            'hora': fechas[0].strftime('%H'),
            'fechas': list(map(lambda x: x.strftime('%H'), fechas)),
            'municipio': municipio,
            'provincia': provincia
            }
    emit('procesado', datos)

@socketio.on('pdf')
def handle_pdf( data ):
    convertHtmlToPdf(data)
    emit('descargar_pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
