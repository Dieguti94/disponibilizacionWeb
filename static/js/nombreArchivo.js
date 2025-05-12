document.addEventListener("DOMContentLoaded", () => {
    // Obtener el input de archivo y el párrafo donde se mostrará el nombre
    const archivoInput = document.getElementById("archivo_csv");
    const nombreArchivo = document.getElementById("nombre-archivo");

    // Agregar evento para mostrar el nombre del archivo
    archivoInput.addEventListener("change", function () {
        if (archivoInput.files.length > 0) {
            nombreArchivo.textContent = `Archivo seleccionado: ${archivoInput.files[0].name}`;
        } else {
            nombreArchivo.textContent = ""; // Limpiar el texto si no se selecciona nada
        }
    });
});