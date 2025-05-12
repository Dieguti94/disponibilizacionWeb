// Array para guardar los candidatos temporalmente
let candidatos = [];

// Referencias a los elementos del DOM
const formCandidato = document.getElementById("form-candidato");
const tablaCandidatos = document.getElementById("tabla-candidatos").getElementsByTagName("tbody")[0];
const inputCandidatos = document.getElementById("candidatos");

// Botón de agregar candidato
document.getElementById("agregar-candidato").addEventListener("click", () => {
    // Obtener los valores ingresados
    const nombre = document.getElementById("nombre").value;
    const apellido = document.getElementById("apellido").value;
    const email = document.getElementById("email").value;
    const telefono = document.getElementById("telefono").value;
    const experiencia = document.getElementById("experiencia").value;
    const educacion = document.getElementById("educacion").value;
    const tecnologias = document.getElementById("tecnologias").value;
    const habilidades = document.getElementById("habilidades").value;

    // Crear un objeto para el candidato
    const candidato = { nombre, apellido, email, telefono, experiencia, educacion, tecnologias, habilidades };

    // Agregar el candidato al array
    candidatos.push(candidato);

    // Actualizar la tabla
    const fila = tablaCandidatos.insertRow();
    fila.innerHTML = `
        <td>${nombre}</td>
        <td>${apellido}</td>
        <td>${email}</td>
        <td>${telefono}</td>
        <td>${experiencia}</td>
        <td>${educacion}</td>
        <td>${tecnologias}</td>
        <td>${habilidades}</td>
    `;

    // Limpiar el formulario
    formCandidato.reset();

    // Actualizar el input oculto con los datos
    inputCandidatos.value = JSON.stringify(candidatos);
});
