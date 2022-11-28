# Mapa para obtener datos meteorológicos


```
git clone 
```


```
docker build -t mapa_clima .
```

```
docker ru-it --rm -p 5000:5000 -v $PWD:/app -w /app mapa_clima python views.py
```
