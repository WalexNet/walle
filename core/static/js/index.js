const temaOscuro = () => {
    document.querySelector("body").setAttribute("data-bs-theme", "dark");
    document.querySelector("#dl-icon").setAttribute("class", "bi bi-sun-fill");
}

const temaClaro = () => {
    document.querySelector("body").setAttribute("data-bs-theme", "ligth");
    document.querySelector("#dl-icon").setAttribute("class", "bi bi-moon-fill");
}

const cambiarTema = () => {
    document.querySelector("body").getAttribute("data-bs-theme") === "ligth" ? temaOscuro() : temaClaro();
}