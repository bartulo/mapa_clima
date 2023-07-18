# Mapa para obtener datos meteorológicos

Para instalar usando docker y crear un servidor local seguir los siguientes pasos (UNIX):

```
git clone https://github.com/bartulo/mapa_clima.git
```

```
cd mapa_clima
```

```
docker build -t mapa_clima .
```

```
docker run -it --rm -p 5000:5000 -v $PWD:/app -w /app mapa_clima python views.py
```

Para acceder al servidor local: http://localhost:5000
