const select = document.getElementById("ofertaSelect");
const mapContainer = document.getElementById("map-container");
const ctx = document.getElementById("grafico_candidatos_etiquetas").getContext("2d");
const ctxTotales = document.getElementById("grafico_total_candidatos").getContext("2d");
const ctxExperiencia = document.getElementById("grafico_experiencia_etiquetas").getContext("2d");

let chart = null;
let chartTotales = null;
let chartExperiencia = null;
let map = null;  

select.addEventListener("change", () => {
    const id = select.value;
    if (!id) return;
    
    // 🔹 Mostrar el mapa solo después de elegir una oferta
    mapContainer.style.display = "block";

    fetch(`/metricas/${id}`)
        .then(res => res.json())
        .then(data => {
            if (chart) chart.destroy();
            if (chartTotales) chartTotales.destroy();
            if (chartExperiencia) chartExperiencia.destroy();

            // Primer gráfico: Total de candidatos
            chartTotales = new Chart(ctxTotales, {
                type: 'bar',
                data: {
                    labels: ["Total", "Aptos", "No Aptos", "Sin Revisar"],
                    datasets: [{
                        label: 'Cantidad de candidatos por estado',
                        data: [data.total_candidatos, data.aptos, data.no_aptos, data.sin_revisar],
                        backgroundColor: ['#0ea0a0', '#4CAF50', '#FF0000', '#808080'],
                        borderColor: ['#00fff2', '#3E8E41', '#CC0000', '#606060'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Cantidad de candidatos totales, aptos, no aptos y sin revisar',
                            font: { size: 18 },
                            padding: { top: 10, bottom: 20 }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 5 }
                        }
                    }
                }
            });

            // Segundo gráfico: cantidad de candidatos por etiqueta
            chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.etiquetas,
                    datasets: [{
                        label: 'Candidatos que cumplen la etiqueta',
                        data: data.cantidades,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Cantidad de postulantes que cumplen cada etiqueta',
                            font: { size: 18 },
                            padding: { top: 10, bottom: 20 }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 5 }
                        }
                    }
                }
            });

            // Tercer gráfico: Promedio de años de experiencia por etiqueta
            const etiquetasExp = Object.keys(data.promedios_experiencia);
            const promediosExp = Object.values(data.promedios_experiencia);

            chartExperiencia = new Chart(ctxExperiencia, {
                type: 'bar',
                data: {
                    labels: etiquetasExp,
                    datasets: [{
                        label: 'Promedio de años de experiencia por etiqueta',
                        data: promediosExp,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Promedio de años de experiencia por etiqueta',
                            font: { size: 18 },
                            padding: { top: 10, bottom: 20 }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });

            // Mapa dinámico con datos de candidatos por provincia
            // Si el mapa aún no está creado, inicializar Leaflet
            if (!map) {
                map = L.map('map').setView([-38.4161, -63.6167], 4);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap'
                }).addTo(map);
            }

            // 🔹 Limpiar marcadores anteriores
            map.eachLayer(layer => {
                if (layer instanceof L.CircleMarker || layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });

            // Agregar marcadores con el número de candidatos en cada provincia
            Object.entries(data.provincias_candidatos).forEach(([provincia, cantidad]) => {
                const coordenadas = getCoordenadas(provincia); 
                if (coordenadas && cantidad > 0) {
                    L.marker(coordenadas).addTo(map)
                        .bindPopup(`${provincia}: ${cantidad} candidatos`)
                        .openPopup(); // Mostrar el número de candidatos directamente en el mapa
                }
            });
        });
});
function getCoordenadas(provincia) {
    const coordenadas = {
        "Buenos Aires": [-34.6037, -58.3816],
        "Catamarca": [-28.4696, -65.7852],
        "Chaco": [-27.4516, -58.9869],
        "Chubut": [-43.2983, -65.1042],
        "Córdoba": [-31.4167, -64.1833],
        "Corrientes": [-27.4806, -58.8341],
        "Entre Ríos": [-31.7333, -60.5238],
        "Formosa": [-26.1849, -58.1731],
        "Jujuy": [-24.1858, -65.2995],
        "La Pampa": [-36.6167, -64.2833],
        "La Rioja": [-29.4131, -66.8558],
        "Mendoza": [-32.8908, -68.8272],
        "Misiones": [-27.3671, -55.896],
        "Neuquén": [-38.9517, -68.0591],
        "Río Negro": [-40.8135, -63.0002],
        "Salta": [-24.7829, -65.4232],
        "San Juan": [-31.5375, -68.5364],
        "San Luis": [-33.295, -66.3356],
        "Santa Cruz": [-51.6226, -69.2181],
        "Santa Fe": [-31.6296, -60.7002],
        "Santiago del Estero": [-27.7951, -64.2615],
        "Tierra del Fuego": [-54.8019, -68.3029],
        "Tucumán": [-26.8083, -65.2176]
    };
    return coordenadas[provincia] || null;
}        
