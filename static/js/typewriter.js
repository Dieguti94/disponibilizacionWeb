document.addEventListener("DOMContentLoaded", () => {
    const titles = [
        { id: "typewriter", text: "Predicción de Candidatos" },
        { id: "typewriter-crear-csv", text: "Crear CSV" },
        { id: "typewriter-nuevo-archivo", text: "Crear un nuevo archivo CSV" },
        { id: "typewriter-actualizar", text: "Actualizar el Modelo de Predicción" },
    ];

    titles.forEach((title, index) => {
        const element = document.getElementById(title.id);
        let i = 0;

        function typeWriter() {
            if (i < title.text.length) {
                element.textContent += title.text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        }

        setTimeout(typeWriter, index * 2000); 
    });
});
