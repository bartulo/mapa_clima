var map = L.map('map', {
  drawControl: true,
  center: [40.0, -3],
  zoom: 6
});

var basemaps = {
  'OSM': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }),
  'Topográfico': L.tileLayer.wms('https://www.ign.es/wms-inspire/mapa-raster', {
        layers: 'mtn_rasterizado'
  }),
  'Ortofoto': L.tileLayer.wms('https://www.ign.es/wms-inspire/pnoa-ma', {
        layers: 'OI.OrthoimageCoverage'
  }),
}

basemaps.OSM.addTo(map);

map.on(L.Draw.Event.CREATED, (event) => {
  if ( event.layerType == 'marker' ) {

    const latlng = event.layer._latlng;
    const modalContent = document.querySelector('.modal-body');
    modalContent.innerHTML = 'Procesando...';
    modal.show();
    socket.emit('localizacion', latlng);
  } else if (event.layerType == 'polygon' ) {
    map.addLayer(event.layer);
    console.log(event.layer);
  }

});

const socket = io();

const modal = new bootstrap.Modal(document.getElementById('modal'), {backdrop: 'static'});
const modalSearch = new bootstrap.Modal(document.getElementById('modalSearch'), {backdrop: 'static'});

class MyModal {

  constructor() {
    this.modalContent = document.querySelector('.modal-body');
    this.crearPdfButton = document.getElementById('pdf');
    
    this.crearPdfButton.addEventListener('click', () => {
      socket.emit('pdf', this.data);
    })

  }

}

const myModal = new MyModal();

const buscar = document.getElementById('buscar');
buscar.addEventListener('click', () => {
  modalSearch.show();
});

let lugares_menu = document.querySelector('ul.dropdown-menu');

let inputSearch = document.getElementById('inputSearch');
inputSearch.addEventListener('input', (e) => {
  if (e.target.value.length > 4) {
    console.log(e.target.value);
   socket.emit('nominatim', e.target.value);
  } else {
    lugares_menu.innerHTML = '';
  }
});

function goToHistorico(e) {
  const incendio = e.target.feature.properties;
  window.open(`${document.URL}/incendio/${incendio.id}`);
}

function historicoOnEachFeature(feature, layer){
  layer.on({
    click: goToHistorico
  });
}

const effis_group = L.layerGroup().addTo(map);
const egif_group = L.layerGroup().addTo(map);

const effis = JSON.parse(data.effis);
L.geoJson(effis, {
  style: {color: 'red'},
  onEachFeature: historicoOnEachFeature
}).addTo(effis_group);

const egif = JSON.parse(data.egif_navarra);
L.geoJson(egif, {
  pointToLayer: function (feature, latlng) {
    return L.circleMarker(latlng, {
      radius: feature.properties.SUPERFICIE / 10,
    });
  }
}).addTo(egif_group);

const overlayMaps = {
  'EFFIS': effis_group,
  'EGIF_Navarra': egif_group
}

let layerControl = L.control.layers(basemaps, overlayMaps).addTo(map);

socket.on('procesado', (data) => {
  myModal.modalContent.innerHTML = `<img src="static/radiosondeos/prueba_${data.lat}_${data.lng}_${data.hora}.png" />`
  myModal.data = data;
});

socket.on('descargar_pdf', () => {
  window.open(`${window.location}/download`)
});

socket.on('listado_nominatim', ( data ) => {
  const lugares = JSON.parse(data);
  lugares_menu.innerHTML = '';
  lugares.forEach( (item) => {
    let li = document.createElement('li');
    let a = document.createElement('a');
    a.classList.add('dropdown-item');
    a.innerHTML = item.display_name;
    a.href = '#';
    a.dataset.name = item.display_name;
    console.log(item);
    a.addEventListener('click', () => {
      modalSearch.hide();
      map.setView([item.lat, item.lon], 12);
    });
    li.appendChild(a);
    lugares_menu.appendChild(li);
  });
});
