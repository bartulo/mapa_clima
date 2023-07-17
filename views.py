from flask import Flask, render_template, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
import datetime
from radiosondeo import *
from municipios import *
from htmlToPdf import *
import geopandas as gpd
import pandas as pd 

pd.options.display.float_format = '${:,.2f}'.format

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def root():
    global effis_file 
    effis_file = gpd.read_file('static/capas/effis/effis.shp')
    historico = effis_file.to_crs(4326)
    return render_template('mapa.html', data={ 
        'historico': historico.to_json()
        })

@app.route('/download')
def download():
    return send_file('static/test.pdf', as_attachment=True)

@app.route('/incendio/<num>')
def incendio(num):
    i = effis_file[effis_file.id == num]
    print(i)
    return render_template('incendio.html', incendio=i.to_dict(orient='records')[0]) 
 #   return render_template('incendio.html', incendio=i.drop(columns=['geometry']).to_html(index=False, float_format= lambda x: "{:.2f}".format(x))) 
    
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

@socketio.on('nominatim')
def nominatim( data ):
    salida = requests.get('https://nominatim.openstreetmap.org/search?format=json&namedetails=1&addressdetails=1&q={}'.format(data))
    print(salida)
    emit('listado_nominatim', salida.text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
