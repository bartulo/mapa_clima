def meteograma(punto):
    horas = 48

    best_gfs = TDSCatalog('http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/'
                          'Global_0p25deg/catalog.xml?dataset=grib/NCEP/GFS/Global_0p25deg/Best')
    best_gfs.datasets
    best_ds = list(best_gfs.datasets.values())[0]
    ncss = best_ds.subset()

    query = ncss.query()

    query.lonlat_point( punto[0], punto[1] ).time_range(datetime.datetime.utcnow(), datetime.datetime.utcnow() + datetime.timedelta(hours=horas))
    #query.lonlat_point( punto[0], punto[1] ).time(datetime.datetime.utcnow())

    query.accept('netcdf4')
    query.variables('Temperature_surface', 
                    'Dewpoint_temperature_height_above_ground',
                    'Relative_humidity_height_above_ground', 
                    'Precipitation_rate_surface',  
                    'u-component_of_wind_height_above_ground',
                    'v-component_of_wind_height_above_ground',
                    'Wind_speed_gust_surface',
                    )

    data = ncss.get_data(query)

    T = data['Temperature_surface']
    Td = data['Dewpoint_temperature_height_above_ground']
    RH = data['Relative_humidity_height_above_ground']
    Pp = data['Precipitation_rate_surface']
    u = data['u-component_of_wind_height_above_ground']
    v = data['v-component_of_wind_height_above_ground']
    gust = data['Wind_speed_gust_surface']

    vientox_10m = list(map(lambda x: x[0], u[:][0]))*units('m/s')
    vientoy_10m = list(map(lambda x: x[0], v[:][0]))*units('m/s')

    velviento_10m = metpy.calc.wind_speed(vientox_10m, vientoy_10m)
    dirviento_10m = metpy.calc.wind_direction(vientox_10m, vientoy_10m, convention='from')

    horaIN= data.time_coverage_start # esta variable se mantiene del bloque anterior

    time = data.variables['time']
    times = num2date( time[:], time.units)
    horas = list(map(lambda x: x.strftime('%H:%M'), times[:][0] ))

    fig = plt.figure(figsize=(20, 20))
    fig, ax = plt.subplots(3, sharex=True, figsize=(10, 5))
    plot_range = [-10, 50]

    def temp():
      ln1 = ax[1].plot(T[:][0] - 273.15, 'r-', label='Temperatura')
      ln2 = ax[1].plot(Td[:][0] - 273.15, 'k', linewidth=0.8, label='Punto de rocío')

      ax[1].set_ylabel('Temperatura (ºC)', multialignment='center')
      ax[1].grid(b=True, which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
      ax[1].set_ylim(plot_range[0], plot_range[1])
      ax[1].legend(loc = 'upper right')

    def humedad():
      ax[2].plot(data['Relative_humidity_height_above_ground'][:][0] , 'b-', label='Humedad relativa')
      ax[2].set_ylabel('HR (%) ', multialignment='center')
      ax[2].grid(b=True, axis='y', color='k', linestyle='--', linewidth=0.5)
      ax[2].legend(loc = 'upper right')

    def viento():
      ln4 = ax[0].plot(gust[:][0], 'y' ,label= 'Viento 10m')
      ln3 = ax[0].plot(velviento_10m[:], 'g', label='Rachas viento')
      #ln5 = ax[0].plot(dirviento_10m[:], 'p', label= 'wind-u')

      ax[0].set_ylabel('Velocidad \ndel Viento', multialignment='center')
      ax[0].grid(b=True, which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
      ax[0].set_ylim(plot_range[0],plot_range[1])

    temp()
    humedad()
    viento()

    #specify x-axis locations
    x_ticks = range(len(horas))

    #specify x-axis labels
    x_labels = horas
    #add x-axis values to plot
    plt.xticks(ticks=x_ticks, labels=x_labels)

    fig.tight_layout()

    fig.savefig('static/images/meteograma_{}_{}.png'.format(punto[0], punto[1]))
