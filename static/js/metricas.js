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

// Carrusel de gráficos
const chartIds = [
    "grafico_total_candidatos",
    "grafico_edu_cant",
    "grafico_tec_cant",
    "grafico_tec2_cant",
    "grafico_hab_cant",
    "grafico_hab2_cant",
    "grafico_edu_exp",
    "grafico_tec_exp",
    "grafico_tec2_exp",
    "grafico_hab_exp",
    "grafico_hab2_exp"
];
let currentChartIndex = 0;

const carouselContainer = document.querySelector('.carousel-container');
if (carouselContainer) carouselContainer.style.display = "none";

function showChart(index) {
    chartIds.forEach((id, i) => {
        const canvas = document.getElementById(id);
        if (canvas) {
            canvas.classList.remove("active");
            canvas.style.display = "none";
        }
    });
    const activeCanvas = document.getElementById(chartIds[index]);
    if (activeCanvas) {
        activeCanvas.classList.add("active");
        activeCanvas.style.display = "block";
    }
    document.getElementById("prevChart").disabled = index === 0;
    document.getElementById("nextChart").disabled = index === chartIds.length - 1;
}

document.getElementById("prevChart").addEventListener("click", () => {
    if (currentChartIndex > 0) {
        currentChartIndex--;
        showChart(currentChartIndex);
    }
});
document.getElementById("nextChart").addEventListener("click", () => {
    if (currentChartIndex < chartIds.length - 1) {
        currentChartIndex++;
        showChart(currentChartIndex);
    }
});

select.addEventListener("change", () => {
    const id = select.value;
    if (!id) {
        if (carouselContainer) carouselContainer.style.display = "none";
        return;
    }
    if (carouselContainer) carouselContainer.style.display = "flex";
    currentChartIndex = 0;
    showChart(currentChartIndex);

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
                        data: [data.total_postulantes, data.aptos, data.no_aptos, data.sin_revisar],
                        backgroundColor: [
                            'rgba(235, 28, 183, 0.74)',
                            'rgba(57, 180, 57, 0.86)',
                            'rgba(248, 20, 20, 0.7)',
                            'rgba(57, 248, 248, 0.7)'
                        ],
                        borderColor: [
                            'rgba(235, 28, 183, 0.74)',
                            'rgba(57, 180, 57, 0.86)',
                            'rgba(248, 20, 20, 0.7)',
                            'rgba(57, 248, 248, 0.7)'
                        ],
                        borderWidth: 2,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'CANDIDATOS Totales, Aptos, No Aptos y Sin Revisar',
                            color: '#fff',
                            font: { size: 20 },
                            padding: { top: 10, bottom: 20 }
                        },
                        legend: {
                            labels: {
                                color: '#fff',
                                font: { family: 'Space Grotesk, Segoe UI, sans-serif', size: 16 }
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#fff', font: { size: 14 } },
                            grid: { color: 'rgba(255,255,255,0.08)' }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 5, color: '#fff', font: { size: 14 } },
                            grid: { color: 'rgba(255,255,255,0.08)' }
                        }
                    }
                }
            });

            // =================== GRAFICOS DE CANTIDADES POR TIPO ===================
            chartEduCant = crearBarChart(ctxEduCant, data.etiquetas_educacion, data.cant_educacion, 'CANDIDATOS x Educación');
            chartTecCant = crearBarChart(ctxTecCant, data.etiquetas_tecnologia, data.cant_tecnologia, 'CANDIDATOS x Tecnología Principal');
            chartTec2Cant = crearBarChart(ctxTec2Cant, data.etiquetas_tecnologia2, data.cant_tecnologia2, 'CANDIDATOS x Tecnología Secundaria');
            chartHabCant = crearBarChart(ctxHabCant, data.etiquetas_habilidad, data.cant_habilidad, 'CANDIDATOS x Habilidad 1');
            chartHab2Cant = crearBarChart(ctxHab2Cant, data.etiquetas_habilidad2, data.cant_habilidad2, 'CANDIDATOS x Habilidad 2');

            // =================== GRAFICOS DE PROMEDIO DE EXPERIENCIA ===================
            chartEduExp = crearBarChart(ctxEduExp, Object.keys(data.exp_educacion), Object.values(data.exp_educacion), 'Promedio de experiencia x Educación', 1);
            chartTecExp = crearBarChart(ctxTecExp, Object.keys(data.exp_tecnologia), Object.values(data.exp_tecnologia), 'Promedio de experiencia x Tecnología Principal', 1);
            chartTec2Exp = crearBarChart(ctxTec2Exp, Object.keys(data.exp_tecnologia2), Object.values(data.exp_tecnologia2), 'Promedio de experiencia x Tecnología Secundaria', 1);
            chartHabExp = crearBarChart(ctxHabExp, Object.keys(data.exp_habilidad), Object.values(data.exp_habilidad), 'Promedio de experiencia x Habilidad 1', 1);
            chartHab2Exp = crearBarChart(ctxHab2Exp, Object.keys(data.exp_habilidad2), Object.values(data.exp_habilidad2), 'Promedio de experiencia x Habilidad 2', 1);

            // =================== MAPA ===================
            if (!map) {
                map = L.map('map', {
                    zoomControl: false,
                    scrollWheelZoom: false,
                    doubleClickZoom: false,
                    boxZoom: false,
                    keyboard: false,
                    tap: false,
                    touchZoom: false,
                }).setView([-40, -63.6167], 4);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap'
                }).addTo(map);
            }

            map.eachLayer(layer => {
                if (layer instanceof L.CircleMarker || layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });

            Object.entries(data.provincias_postulantes).forEach(([provincia, cantidad]) => {
                const coordenadas = getCoordenadas(provincia);
                if (coordenadas && cantidad > 0) {
                    L.marker(coordenadas).addTo(map)
                        .bindPopup(`${provincia}<br>Candidatos en total: ${cantidad}`)
                }
            });
        });
});

// Función utilitaria para crear un bar chart con estilo personalizado
function crearBarChart(ctx, etiquetas, datos, titulo, stepSize = 5) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: etiquetas,
            datasets: [{
                label: titulo,
                data: datos,
                backgroundColor: [
                    'rgba(0, 212, 255, 0.7)'
                ],
                borderColor: [
                    'rgba(0, 212, 255, 0.7)'
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#fff',
                        font: { family: 'Space Grotesk, Segoe UI, sans-serif', size: 16 }
                    }
                },
                title: {
                    display: true,
                    text: titulo,
                    color: '#fff',
                    font: { size: 20 }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#fff', font: { size: 14 } },
                    grid: { color: 'rgba(255,255,255,0.08)' }
                },
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: stepSize, color: '#fff', font: { size: 14 } },
                    grid: { color: 'rgba(255,255,255,0.08)' }
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

// Inicializar el carrusel oculto
showChart(currentChartIndex);
if (carouselContainer) carouselContainer.style.display = "none";

// Quitar el focus visual del botón del carrusel al hacer clic
// Esto mejora la experiencia visual y evita el contorno azul tras el click
// Puedes mover este bloque a tu archivo static/js/metricas.js si lo prefieres modular

document.addEventListener('DOMContentLoaded', function () {
    // Mostrar panel solo si se selecciona una oferta
    const select = document.getElementById('ofertaSelect');
    const panel = document.querySelector('.box-background ');
    select.addEventListener('change', function () {
        if (select.value) {
            panel.style.display = 'block';
        } else {
            panel.style.display = 'none';
        }
    });
    document.querySelectorAll('.carousel-arrow').forEach(function (btn) {
        btn.addEventListener('mouseup', function () {
            this.blur();
        });
    });
});