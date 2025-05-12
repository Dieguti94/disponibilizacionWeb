document.addEventListener("DOMContentLoaded", () => {
    const tablaContainer = document.querySelector(".tabla-container");
    let isDragging = false;
    let startX, scrollLeft;

    tablaContainer.addEventListener("mousedown", (e) => {
        isDragging = true;
        startX = e.pageX - tablaContainer.offsetLeft;
        scrollLeft = tablaContainer.scrollLeft;
        tablaContainer.style.cursor = "grabbing";
    });

    tablaContainer.addEventListener("mouseleave", () => {
        isDragging = false;
        tablaContainer.style.cursor = "grab";
    });

    tablaContainer.addEventListener("mouseup", () => {
        isDragging = false;
        tablaContainer.style.cursor = "grab";
    });

    tablaContainer.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        e.preventDefault();
        const x = e.pageX - tablaContainer.offsetLeft;
        const walk = (x - startX) * 2;
        tablaContainer.scrollLeft = scrollLeft - walk;
    });
});
