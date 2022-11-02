import requests
import matplotlib.pyplot as plt
from collections import defaultdict
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import SkewT
from metpy.units import units
import xarray as xr
import datetime

def radiosondeo( lat, lng ):

    rucsounding = requests.get('https://rucsoundings.noaa.gov/get_soundings.cgi?data_source=GFS&start=latest&n_hrs=24&fcst_len=shortest&airport={}%2C%20{}&text=Ascii%20text%20%28GSL%20format%29'.format(lat, lng)).text
    data = rucsounding.split('\n')

    fechas = []
    temperaturas = []
    dews = []
    heights = []
    winds = []
    wsps = []
    for i in range(6):
      s = data[(38 * i) + 1].split()
      fecha = datetime.datetime.strptime(','.join(s[1:]), '%H,%d,%b,%Y')
      fechas.append(fecha)
      temperatura = []
      dew = []
      pres = []
      height = []
      wind =[]
      wsp = []
      for n in range( (38 * i + 6), (38 * i + 25)):
        linea = data[n].split()
        pres.append(round(int(linea[1])/10))
        height.append(int(linea[2]))
        temperatura.append(int(linea[3])/10)
        dew.append(int(linea[4])/10)
        wind.append(int(linea[5]))
        wsp.append(int(linea[6]))

      temperaturas.append(temperatura)
      heights.append(height)
      dews.append(dew)
      winds.append(wind)
      wsps.append(wsp)
    xarray_3d = xr.Dataset(
        {'temp': (('fechas', 'pres'), temperaturas)},
        coords = {
            'fechas': fechas,
            'pres': pres,
            'dew': (('fechas', 'pres'), dews),
            'height': (('fechas', 'pres'), heights),
            'wdir': (('fechas', 'pres'), winds),
            'wsp': (('fechas', 'pres'), wsps),
        }
    )
    df = xarray_3d.to_dataframe()

    TAM_EJE = 16 # VALOR DEL TAMAÑO DE LETRA QUE QUIERES ASIGNAR

    plt.rc('ytick', labelsize=TAM_EJE) #### SOLO CAMBIA EL TAMAÑO DEL PRIMER EJE Y.
    plt.rc('xtick', labelsize=TAM_EJE)

    for fecha, d in df.groupby('fechas'):
      p = d.reset_index('pres')['pres'].values * units.hPa
      T = d['temp'].values * units.degC
      Td = d['dew'].values * units.degC
      H = d['height'].values * units.m
      wind_speed = d['wsp'].values * units.knots
      wind_dir = d['wdir'].values * units.degrees
      u, v = mpcalc.wind_components(wind_speed, wind_dir)

      fig = plt.figure(figsize=(10, 10))
      skew = SkewT(fig, rotation = 40)

      skew.plot(p, T, 'r')
      skew.plot(p, Td, 'g')
      skew.plot_barbs(p, u, v)

      parcel_prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
      skew.plot(p, parcel_prof, 'k', linestyle='--')

      skew.plot_dry_adiabats(linewidth=0.8)
      skew.plot_moist_adiabats(linewidth=0.8)
      skew.plot_mixing_lines(linewidth=0.8)

      for P, t, h in zip(p, T, H):
        if P.magnitude % 100  == 0 * units.hPa:
          skew.ax.text(1.01, P, h.m, transform=skew.ax.get_yaxis_transform(which='tick2'), fontsize=TAM_EJE) # AQUÍ SE CAMBIA EL TAMAÑO DEL EJE DE LA DERECHA

      skew.ax.set_ylim(1050, 200)
      skew.ax.set_yticks([1000, 950, 900,  850,  800,  750,  700,  650,  600,  550,  500,  450,  400,  350,  300,  250,  200])
      skew.ax.set_xlim(-25, 45)
      skew.ax.set_ylabel('Presión (hPa)', multialignment='center', fontsize=TAM_EJE)
      skew.ax.set_xlabel('Temperatura (ºC)', multialignment='center', fontsize=TAM_EJE)
      #skew.ax.axvline(0 * units.degC, color='k', linewidth=0.8, linestyle = '--')
      plt.title('GFS válido: {} | Lat: {:.2f} | Long: {:.2f}'.format(fecha.strftime('%d %b %HZ'), lat, lng), fontsize=TAM_EJE)
      fig.savefig('static/radiosondeos/prueba_{}_{}_{}.png'.format(lat, lng, fecha.strftime('%H')))
    
    return fechas
