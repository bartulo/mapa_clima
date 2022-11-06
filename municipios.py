import geopandas as gpd
from shapely.geometry import Point

municipios = gpd.read_file('static/capas/municipios/recintos_municipales_inspire_peninbal_etrs89.shp')
provincias = gpd.read_file('static/capas/provincias/recintos_provinciales_inspire_peninbal_etrs89.shp')

def get_municipio( lat, lng ):
    m = municipios[municipios.geometry.contains(Point(lng, lat)) == True].NAMEUNIT.values[0]
    p = provincias[provincias.geometry.contains(Point(lng, lat)) == True].NAMEUNIT.values[0]

    return [m, p]
