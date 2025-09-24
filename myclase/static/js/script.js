document.addEventListener("DOMContentLoaded", () => {
    // Toggle de lista/grid
    const toggleBtn = document.querySelector('.toggle-view-btn');
    const productsContainer = document.querySelector('.products-container');

    if (toggleBtn && productsContainer) {
        toggleBtn.addEventListener('click', () => {
            const isList = productsContainer.classList.toggle('list-view');
            productsContainer.classList.toggle('grid-view', !isList);

            // Cambiar icono
            const icon = toggleBtn.querySelector('i');
            if(icon){
                icon.className = isList ? 'bi bi-grid-3x3-gap' : 'bi bi-list-ul';
            }
        });
    }

    // Botón de filtro
    const filterBtn = document.querySelector('.filter-btn');
    if (filterBtn) {
        filterBtn.addEventListener('click', () => {
            alert("Función de filtros aún no implementada");
        });
    }

    // Botón de búsqueda
    const searchBtn = document.getElementById("searchbtn");
    const searchBox = document.getElementById("searchbox"); // tu input con id="searchbox"
    if (searchBtn && searchBox) {
        searchBtn.addEventListener("click", () => {
            const query = searchBox.value.trim();
            const url = query ? `?q=${encodeURIComponent(query)}` : window.location.pathname;
            window.location.href = url;
        });
    }

    // 🔹 NUEVO: Botón para seleccionar imagen y vista previa
    const selectImageBtn = document.getElementById("selectImageBtn");
    const imageInput = document.getElementById("id_image");
    const imagePreview = document.getElementById("imagePreview");

    if(selectImageBtn && imageInput && imagePreview){
        selectImageBtn.addEventListener("click", () => {
            imageInput.click();
        });

        imageInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if(file){
                const reader = new FileReader();
                reader.onload = function(ev){
                    imagePreview.src = ev.target.result;
                }
                reader.readAsDataURL(file);
            } else {
                // placeholder si no hay imagen seleccionada
                imagePreview.src = imagePreview.dataset.placeholder || "";
            }
        });
    }
});
