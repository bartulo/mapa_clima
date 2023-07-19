from flask import Flask, render_template, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
import datetime
from radiosondeo import *
from municipios import *
from htmlToPdf import *
import geopandas as gpd
import pandas as pd 
from PIL import Image
from io import BytesIO
import requests

pd.options.display.float_format = '${:,.2f}'.format

app = Flask(__name__)
socketio = SocketIO(app)

def create_gif(fecha):
    f = datetime.datetime.strptime(fecha, '%Y-%m-%d')
    frames =[]
    for i in (f - datetime.timedelta(days=n) for n in range(2, -1, -1)):
        for j in ['00', '06', '12', '18']:
            response = requests.get(f'https://www.wetterzentrale.de/maps/archive/{datetime.datetime.strftime(i, "%Y")}/cfsr/CFSR_1_{datetime.datetime.strftime(i,"%Y%m%d")}{j}_1.png')
            frames.append(Image.open(BytesIO(response.content)))

    frame_one = frames[0]
    frame_one.save("static/500hpa.gif", format="GIF", append_images=frames,
               save_all=True, duration=300, loop=0)

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
    inc= effis_file[effis_file.id == num]
    create_gif(inc.FIREDATE.iloc[0].split(' ')[0])
    return render_template('incendio.html', incendio=inc.to_dict(orient='records')[0]) 
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
