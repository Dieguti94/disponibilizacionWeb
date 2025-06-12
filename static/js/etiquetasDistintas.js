document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  if (!form) return;

  form.addEventListener("submit", function (event) {
    const tec1 = document.getElementById("tecnologias").value;
    const tec2 = document.getElementById("tecnologias2").value;
    const hab1 = document.getElementById("habilidades").value;
    const hab2 = document.getElementById("habilidades2").value;

    if (tec1 && tec2 && tec1 === tec2) {
      alert("Tecnología 2 no puede ser igual a Tecnología 1");
      event.preventDefault();
      return;
    }

    if (hab1 && hab2 && hab1 === hab2) {
      alert("Habilidad 2 no puede ser igual a Habilidad 1");
      event.preventDefault();
      return;
    }
  });
});
