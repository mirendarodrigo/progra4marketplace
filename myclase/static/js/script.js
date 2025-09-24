document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.querySelector('.toggle-view-btn');
    const productsContainer = document.querySelector('.products-container');

    toggleBtn.addEventListener('click', () => {
        const isList = productsContainer.classList.toggle('list-view');
        productsContainer.classList.toggle('grid-view', !isList);

        // Cambiar icono
        const icon = toggleBtn.querySelector('i');
        icon.className = isList ? 'bi bi-grid-3x3-gap' : 'bi bi-list-ul';
    });

    const filterBtn = document.querySelector('.filter-btn');
    filterBtn.addEventListener('click', () => {
        alert("Función de filtros aún no implementada");
    });
});
