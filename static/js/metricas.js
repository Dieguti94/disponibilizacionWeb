const select = document.getElementById("ofertaSelect");
const mapContainer = document.getElementById("map-container");

const ctxTotales = document.getElementById("grafico_total_candidatos").getContext("2d");

const ctxEduCant = document.getElementById("grafico_edu_cant").getContext("2d");
const ctxTecCant = document.getElementById("grafico_tec_cant").getContext("2d");
const ctxTec2Cant = document.getElementById("grafico_tec2_cant").getContext("2d");
const ctxHabCant = document.getElementById("grafico_hab_cant").getContext("2d");
const ctxHab2Cant = document.getElementById("grafico_hab2_cant").getContext("2d");

const ctxEduExp = document.getElementById("grafico_edu_exp").getContext("2d");
const ctxTecExp = document.getElementById("grafico_tec_exp").getContext("2d");
const ctxTec2Exp = document.getElementById("grafico_tec2_exp").getContext("2d");
const ctxHabExp = document.getElementById("grafico_hab_exp").getContext("2d");
const ctxHab2Exp = document.getElementById("grafico_hab2_exp").getContext("2d");

let chartTotales = null;
let chartEduCant = null;
let chartTecCant = null;
let chartTec2Cant = null;
let chartHabCant = null;
let chartHab2Cant = null;
let chartEduExp = null;
let chartTecExp = null;
let chartTec2Exp = null;
let chartHabExp = null;
let chartHab2Exp = null;

let map = null;

select.addEventListener("change", () => {
    const id = select.value;
    if (!id) return;

    mapContainer.style.display = "block";

    fetch(`/metricas/${id}`)
        .then(res => res.json())
        .then(data => {
            // Destruir todos los gráficos si ya existen
            if (chartTotales) chartTotales.destroy();
            if (chartEduCant) chartEduCant.destroy();
            if (chartTecCant) chartTecCant.destroy();
            if (chartTec2Cant) chartTec2Cant.destroy();
            if (chartHabCant) chartHabCant.destroy();
            if (chartHab2Cant) chartHab2Cant.destroy();
            if (chartEduExp) chartEduExp.destroy();
            if (chartTecExp) chartTecExp.destroy();
            if (chartTec2Exp) chartTec2Exp.destroy();
            if (chartHabExp) chartHabExp.destroy();
            if (chartHab2Exp) chartHab2Exp.destroy();

            // =================== GRAFICO DE TOTALES ===================
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
                            color: 'white',
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

            // =================== GRAFICOS DE CANTIDADES POR TIPO ===================
            chartEduCant = crearBarChart(ctxEduCant, data.etiquetas_educacion, data.cant_educacion, 'Cantidad de candidatos por educación');
            chartTecCant = crearBarChart(ctxTecCant, data.etiquetas_tecnologia, data.cant_tecnologia, 'Cantidad de candidatos por tecnología');
            chartTec2Cant = crearBarChart(ctxTec2Cant, data.etiquetas_tecnologia2, data.cant_tecnologia2, 'Cantidad de candidatos por tecnología Secundaria');
            chartHabCant = crearBarChart(ctxHabCant, data.etiquetas_habilidad, data.cant_habilidad, 'Cantidad de candidatos por habilidad');
            chartHab2Cant = crearBarChart(ctxHab2Cant, data.etiquetas_habilidad2, data.cant_habilidad2, 'Cantidad de candidatos por habilidad Secundaria');

            // =================== GRAFICOS DE PROMEDIO DE EXPERIENCIA ===================
            chartEduExp = crearBarChart(ctxEduExp, Object.keys(data.exp_educacion), Object.values(data.exp_educacion), 'Promedio de experiencia por educación', 1);
            chartTecExp = crearBarChart(ctxTecExp, Object.keys(data.exp_tecnologia), Object.values(data.exp_tecnologia), 'Promedio de experiencia por tecnología', 1);
            chartTec2Exp = crearBarChart(ctxTec2Exp, Object.keys(data.exp_tecnologia2), Object.values(data.exp_tecnologia2), 'Promedio de experiencia por tecnología Secundaria', 1);
            chartHabExp = crearBarChart(ctxHabExp, Object.keys(data.exp_habilidad), Object.values(data.exp_habilidad), 'Promedio de experiencia por habilidad', 1);
            chartHab2Exp = crearBarChart(ctxHab2Exp, Object.keys(data.exp_habilidad2), Object.values(data.exp_habilidad2), 'Promedio de experiencia por habilidad Secundaria', 1);

            // =================== MAPA ===================
            if (!map) {
                map = L.map('map').setView([-38.4161, -63.6167], 4);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap'
                }).addTo(map);
            }

            map.eachLayer(layer => {
                if (layer instanceof L.CircleMarker || layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });

            Object.entries(data.provincias_candidatos).forEach(([provincia, cantidad]) => {
                const coordenadas = getCoordenadas(provincia);
                if (coordenadas && cantidad > 0) {
                    L.marker(coordenadas).addTo(map)
                        .bindPopup(`${provincia}: ${cantidad} candidatos`)
                }
            });
        });
});

// Función utilitaria para crear un bar chart
function crearBarChart(ctx, etiquetas, datos, titulo, stepSize = 5) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: etiquetas,
            datasets: [{
                label: titulo,
                data: datos,
                backgroundColor: 'rgba(57, 248, 248, 0.7)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: titulo,
                    color: 'white',
                    font: { size: 18 },
                    padding: { top: 10, bottom: 20 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: stepSize }
                }
            }
        }
    });
}

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