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

L.control.layers(basemaps).addTo(map);

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

socket.on('procesado', (data) => {
  myModal.modalContent.innerHTML = `<img src="static/radiosondeos/prueba_${data.lat}_${data.lng}_${data.hora}.png" />`
  myModal.data = data;
});

socket.on('descargar_pdf', () => {
  window.open(`${window.location}/download`)
});
