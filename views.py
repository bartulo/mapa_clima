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

def convertHtmlToPdf(lng, lat): 
    outputFilename = "static/test.pdf"
    texto = 'esto es un ejemplo de texto'
    data = {'url' : 'static/radiosondeos/prueba_{}_{}_15.png'.format(lat, lng), 'pie_pagina': texto} 

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
    print( data )
    #meteograma([data['lng'], data['lat']])
    fechas = radiosondeo(data['lat'], data['lng'])
    emit('procesado', data)

@socketio.on('pdf')
def handle_pdf( data ):
    convertHtmlToPdf(data['lng'], data['lat'])
    emit('descargar_pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
