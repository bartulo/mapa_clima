import requests
import matplotlib.pyplot as plt
from collections import defaultdict
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import SkewT
from metpy.units import units

def radiosondeo( lat, lng ):

    rucsounding = requests.get('https://rucsoundings.noaa.gov/get_soundings.cgi?data_source=GFS&start=latest&n_hrs=24&fcst_len=shortest&airport={}%2C%20{}&text=Ascii%20text%20%28GSL%20format%29'.format(lat, lng)).text
    data = rucsounding.split('\n')

    i = 1
    j = 0
    sounding = []

    while j < 6:
      datos = defaultdict(list)
      datos['fecha'] = (data[i])

      for k in range(i+5, i+24):
        linea = data[k].split()
        datos['pres'].append(round(int(linea[1])/10))
        datos['height'].append(int(linea[2]))
        datos['tmp'].append(int(linea[3])/10)
        datos['dew'].append(int(linea[4])/10)
        datos['wdir'].append(int(linea[5]))
        datos['wsp'].append(int(linea[6]))
        
      sounding.append(datos)  
      datos = 0
      i += 38
      j += 1



    TAM_EJE = 16 # VALOR DEL TAMAÑO DE LETRA QUE QUIERES ASIGNAR

    plt.rc('ytick', labelsize=TAM_EJE) #### SOLO CAMBIA EL TAMAÑO DEL PRIMER EJE Y.
    plt.rc('xtick', labelsize=TAM_EJE)

    salidaGFS = sounding[0]['fecha'].split()

    for s in range(0, len(sounding)):
      p = sounding[s]['pres'] * units.hPa
      T = sounding[s]['tmp'] * units.degC
      Td = sounding[s]['dew'] * units.degC
      H = sounding[s]['height'] * units.m
      wind_speed = sounding[s]['wsp'] * units.knots
      wind_dir = sounding[s]['wdir'] * units.degrees
      u, v = mpcalc.wind_components(wind_speed, wind_dir)

      fecha_pronos = sounding[s]['fecha'].split()

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
        if P >= 100 * units.hPa:
          skew.ax.text(1.01, P, h.m, transform=skew.ax.get_yaxis_transform(which='tick2'), fontsize=TAM_EJE) # AQUÍ SE CAMBIA EL TAMAÑO DEL EJE DE LA DERECHA

      skew.ax.set_ylim(1050, 200)
      skew.ax.set_yticks([1000, 950, 900,  850,  800,  750,  700,  650,  600,  550,  500,  450,  400,  350,  300,  250,  200])
      skew.ax.set_xlim(-25, 45)
      skew.ax.set_ylabel('Presión (hPa)', multialignment='center', fontsize=TAM_EJE)
      skew.ax.set_xlabel('Temperatura (ºC)', multialignment='center', fontsize=TAM_EJE)
      #skew.ax.axvline(0 * units.degC, color='k', linewidth=0.8, linestyle = '--')
      plt.title(str(" ".join(salidaGFS[:1]))+" válido: "+str(fecha_pronos[1])+"z"+" | "+"Lat: "+str(lat)+" Lon: "+str(lng), fontsize=TAM_EJE)
      fig.savefig('radiosondeos/prueba_{}.png'.format(fecha_pronos[1]))
