document.querySelectorAll(".input-importancia").forEach(input => {
    input.addEventListener("change", () => {
    const id = input.dataset.id;
    const tipo = input.dataset.tipo;
    const valor = parseInt(input.value);

    if (![0, 1, 2, 3].includes(valor)) {
        alert("Solo se permiten valores entre 0 y 3");
        input.value = 0;
        return;
    }

    fetch(`/importancia/${tipo}/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ importancia: valor })
    })
    .then(res => {
        if (!res.ok) throw new Error("No se pudo actualizar");
    })
    .catch(err => alert("Ups: " + err.message));
    });
});
