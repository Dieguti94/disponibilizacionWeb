// Carrusel de gráficos/tablas
document.addEventListener('DOMContentLoaded', function () {
  const charts = document.querySelectorAll('.carousel-chart');
  let currentChartIndex = 0;

  function showChart(index) {
    charts.forEach((chart, i) => {
      chart.classList.toggle('active', i === index);
    });
    document.getElementById('prevChart').disabled = index === 0;
    document.getElementById('nextChart').disabled = index === charts.length - 1;
  }

  document.getElementById('prevChart').addEventListener('click', () => {
    if (currentChartIndex > 0) {
      currentChartIndex--;
      showChart(currentChartIndex);
    }
  });

  document.getElementById('nextChart').addEventListener('click', () => {
    if (currentChartIndex < charts.length - 1) {
      currentChartIndex++;
      showChart(currentChartIndex);
    }
  });

  // Quitar el focus visual del botón del carrusel al hacer clic
  document.querySelectorAll('.carousel-arrow').forEach(function (btn) {
    btn.addEventListener('mouseup', function () {
      this.blur();
    });
  });

  // Inicializa el carrusel
  showChart(currentChartIndex);
});

// Botones personalizados para inputs de importancia
document.querySelectorAll('.input-num-custom').forEach(function (wrapper) {
  const input = wrapper.querySelector('.input-importancia');
  wrapper.querySelector('.menos').onclick = function () {
    input.stepDown();
    input.dispatchEvent(new Event('input'));
  };
  wrapper.querySelector('.mas').onclick = function () {
    input.stepUp();
    input.dispatchEvent(new Event('input'));
  };
});

// Actualización automática de importancia
document.querySelectorAll('.input-importancia').forEach(function (input) {
  function actualizarImportancia() {
    const id = input.getAttribute('data-id');
    const tipo = input.getAttribute('data-tipo');
    const valor = input.value;

    fetch(`/importancia/${tipo}/${id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
        // Si usas CSRF, agrega aquí el token
        // 'X-CSRFToken': csrf_token
      },
      body: JSON.stringify({ importancia: valor })
    })
      .then(response => response.json())
      .then(data => {
        console.log('Respuesta:', data);
        if (!data.ok) {
          alert(data.error || 'Error al actualizar la importancia');
        }
      })
      .catch((e) => {
        alert('Error de conexión al actualizar la importancia');
        console.error(e);
      });
  }
  input.addEventListener('input', actualizarImportancia);
  input.addEventListener('change', actualizarImportancia);
});