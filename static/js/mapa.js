var map = L.map('map', {
  center: [40.0, -3],
  zoom: 6
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

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

map.on('click', (e) => {
  const modalContent = document.querySelector('.modal-body');
  modalContent.innerHTML = 'Procesando...';
  modal.show();
  socket.emit('localizacion', e.latlng);
  console.log(e.latlng.lat);
});
