// --- Gauge charts con Chart.js ---
// Crea tres gauges de ejemplo para mostrar métricas de las ofertas
document.addEventListener('DOMContentLoaded', function() {
    // Datos de ejemplo para los gauges
    const gaugeData = [5, 23, 2];
    const gaugeMax = [10, 50, 10];
    const gaugeColors = [
        ['#4caf50', '#e0e0e0'],
        ['#2196f3', '#e0e0e0'],
        ['#f44336', '#e0e0e0']
    ];

    function createGauge(ctx, value, max, colors) {
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [value, max - value],
                    backgroundColor: colors,
                    borderWidth: 0
                }]
            },
            options: {
                rotation: -90,
                circumference: 180,
                cutout: '70%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false },
                    title: { display: false },
                },
                responsive: false
            }
        });
    }

    // Si existen los canvas para los gauges, los crea
    if (document.getElementById('gauge1')) createGauge(document.getElementById('gauge1'), gaugeData[0], gaugeMax[0], gaugeColors[0]);
    if (document.getElementById('gauge2')) createGauge(document.getElementById('gauge2'), gaugeData[1], gaugeMax[1], gaugeColors[1]);
    if (document.getElementById('gauge3')) createGauge(document.getElementById('gauge3'), gaugeData[2], gaugeMax[2], gaugeColors[2]);

    // --- Marcar ofertas cerradas con más de 1 día ---
    // (Este ejemplo es para ofertas cerradas, pero aquí solo hay ofertas activas)
    document.querySelectorAll('.oferta-card.oferta-cerrada').forEach(card => {
        const fecha = card.querySelector('.oferta-fecha');
        if (fecha && fecha.textContent.includes('2 días')) {
            card.querySelector('.btn-eliminar-oferta').classList.add('cerrada-mas-1dia');
        }
    });

    // --- Expansión de tarjetas de ofertas ---
    // Permite expandir/cerrar detalles de cada oferta al hacer click en la tarjeta
    const cards = document.querySelectorAll('.oferta-card[data-oferta-id]');
    let expandedCard = null;
    cards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Evita expandir si se hace click en un botón dentro de la tarjeta
            if (e.target.tagName === 'BUTTON' || e.target.closest('form')) return;
            const detalles = card.querySelector('.oferta-detalles');
            if (expandedCard && expandedCard !== card) {
                collapseCard(expandedCard);
            }
            if (detalles.style.display === 'none' || detalles.style.display === '') {
                expandCard(card);
                expandedCard = card;
            } else {
                collapseCard(card);
                expandedCard = null;
            }
        });
    });

    function expandCard(card) {
        const detalles = card.querySelector('.oferta-detalles');
        detalles.style.display = 'block';
        detalles.style.maxHeight = detalles.scrollHeight + 'px';
        card.classList.add('expanded');
        //card.style.height = (220 + detalles.scrollHeight) + 'px';
    }

    function collapseCard(card) {
        const detalles = card.querySelector('.oferta-detalles');
        detalles.style.display = 'none';
        detalles.style.maxHeight = null;
        card.classList.remove('expanded');
        //card.style.height = '';
    }
});