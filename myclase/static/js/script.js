document.addEventListener("DOMContentLoaded", () => {
    // ==================== SISTEMA DE FAVORITOS ====================
    
    // Array para almacenar favoritos
    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    let budgetMode = false;
    
    // Elementos del DOM
    const favoritesToggle = document.getElementById('favoritesToggle');
    const favoritesDropdown = document.getElementById('favoritesDropdown');
    const favoritesBadge = document.getElementById('favoritesBadge');
    const favoritesList = document.getElementById('favoritesList');
    const btnBudget = document.getElementById('btnBudget');
    const budgetActions = document.getElementById('budgetActions');
    const btnCancelBudget = document.getElementById('btnCancelBudget');
    const btnGenerateBudget = document.getElementById('btnGenerateBudget');
    
    // Inicializar favoritos
    updateFavoritesBadge();
    renderFavorites();
    
    // Toggle dropdown de favoritos
    if (favoritesToggle && favoritesDropdown) {
        favoritesToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            favoritesDropdown.classList.toggle('show');
        });
        
        // Cerrar al hacer click fuera
        document.addEventListener('click', (e) => {
            if (!favoritesDropdown.contains(e.target) && !favoritesToggle.contains(e.target)) {
                favoritesDropdown.classList.remove('show');
            }
        });
    }
    
    // Actualizar badge de favoritos
    function updateFavoritesBadge() {
        if (favoritesBadge) {
            const count = favorites.length;
            if (count > 0) {
                favoritesBadge.textContent = count;
                favoritesBadge.classList.remove('d-none');
            } else {
                favoritesBadge.classList.add('d-none');
            }
        }
    }
    
    // Renderizar lista de favoritos
    function renderFavorites() {
        if (!favoritesList) return;
        
        if (favorites.length === 0) {
            favoritesList.innerHTML = `
                <div class="empty-favorites">
                    <i class="bi bi-star"></i>
                    <p>No tienes favoritos aún</p>
                </div>
            `;
            return;
        }
        
        favoritesList.innerHTML = favorites.map(fav => `
            <div class="favorite-item ${budgetMode ? 'budget-mode' : ''}" data-id="${fav.id}">
                ${budgetMode ? `<input type="checkbox" class="budget-checkbox" data-id="${fav.id}">` : ''}
                <img src="${fav.image}" alt="${fav.title}" class="favorite-item-img">
                <div class="favorite-item-info">
                    <div class="favorite-item-title">${fav.title}</div>
                    <div class="favorite-item-price">$${fav.price}</div>
                    <div class="favorite-item-actions">
                        <button class="btn btn-add-cart" data-id="${fav.id}">
                            <i class="bi bi-cart-plus"></i> Carrito
                        </button>
                        <button class="btn btn-remove-fav" data-id="${fav.id}">
                            <i class="bi bi-trash"></i> Quitar
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Agregar event listeners a los botones
        attachFavoriteItemListeners();
    }
    
    // Agregar listeners a items de favoritos
    function attachFavoriteItemListeners() {
        // Botones de agregar al carrito
        document.querySelectorAll('.btn-add-cart').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                addToCart(id);
            });
        });
        
        // Botones de quitar de favoritos
        document.querySelectorAll('.btn-remove-fav').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                removeFromFavorites(id);
            });
        });
    }
    
    // Agregar producto a favoritos
    function addToFavorites(product) {
        // Verificar si ya existe
        if (favorites.some(fav => fav.id === product.id)) {
            showNotification('El producto ya está en favoritos', 'info');
            return false;
        }
        
        favorites.push(product);
        localStorage.setItem('favorites', JSON.stringify(favorites));
        updateFavoritesBadge();
        renderFavorites();
        
        showNotification('Producto agregado a favoritos', 'success');
        return true;
    }
    
    // Quitar producto de favoritos
    function removeFromFavorites(id) {
        favorites = favorites.filter(fav => fav.id !== id);
        localStorage.setItem('favorites', JSON.stringify(favorites));
        updateFavoritesBadge();
        renderFavorites();
        
        // Actualizar botón del modal si está abierto
        const modalFavBtn = document.getElementById('modal-favorite-btn');
        if (modalFavBtn) {
            const currentProductId = modalFavBtn.dataset.productId;
            if (currentProductId === id) {
                modalFavBtn.classList.remove('active');
                const icon = modalFavBtn.querySelector('i');
                if (icon) icon.className = 'bi bi-star';
            }
        }
        
        showNotification('Producto eliminado de favoritos', 'info');
    }
    
    // Agregar al carrito
    function addToCart(id) {
        const product = favorites.find(fav => fav.id === id);
        if (product) {
            console.log('Agregando al carrito:', product);
            showNotification(`"${product.title}" agregado al carrito`, 'success');
            
            // Aquí irá tu petición AJAX al backend
            /*
            fetch('/api/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ product_id: id, quantity: 1 })
            });
            */
        }
    }
    
    // Modo presupuesto
    if (btnBudget) {
        btnBudget.addEventListener('click', () => {
            budgetMode = !budgetMode;
            btnBudget.classList.toggle('active');
            
            if (budgetMode) {
                budgetActions.classList.remove('d-none');
            } else {
                budgetActions.classList.add('d-none');
            }
            
            renderFavorites();
        });
    }
    
    // Cancelar presupuesto
    if (btnCancelBudget) {
        btnCancelBudget.addEventListener('click', () => {
            budgetMode = false;
            btnBudget.classList.remove('active');
            budgetActions.classList.add('d-none');
            renderFavorites();
        });
    }
    
    // Generar presupuesto
    if (btnGenerateBudget) {
        btnGenerateBudget.addEventListener('click', () => {
            const selectedCheckboxes = document.querySelectorAll('.budget-checkbox:checked');
            const selectedIds = Array.from(selectedCheckboxes).map(cb => cb.dataset.id);
            
            if (selectedIds.length === 0) {
                showNotification('Selecciona al menos un producto', 'warning');
                return;
            }
            
            const selectedProducts = favorites.filter(fav => selectedIds.includes(fav.id));
            generateBudget(selectedProducts);
        });
    }
    
    // Generar presupuesto
    function generateBudget(products) {
        const total = products.reduce((sum, p) => sum + parseFloat(p.price), 0);
        
        let budgetHTML = `
            <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; border: 3px solid #ffd97d; border-radius: 15px; background: white;">
                <div style="background: linear-gradient(135deg, #f56416 0%, #772014 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
                    <h2 style="margin: 0;">PRESUPUESTO</h2>
                    <p style="margin: 5px 0 0;">LocalMarket</p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <p><strong>Fecha:</strong> ${new Date().toLocaleDateString()}</p>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background: #ffd97d;">
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Producto</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Marca</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: right;">Precio</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${products.map(p => `
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;">${p.title}</td>
                                <td style="padding: 10px; border: 1px solid #ddd;">${p.marca || 'N/A'}</td>
                                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">$${p.price}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                    <tfoot>
                        <tr style="background: #f8f9fa; font-weight: bold;">
                            <td colspan="2" style="padding: 12px; border: 1px solid #ddd; text-align: right;">TOTAL:</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: right; color: #f56416; font-size: 1.2em;">$${total.toFixed(2)}</td>
                        </tr>
                    </tfoot>
                </table>
                
                <div style="text-align: center; color: #7c7c7c; font-size: 0.9em;">
                    <p>Gracias por su preferencia</p>
                </div>
            </div>
        `;
        
        // Abrir en nueva ventana
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Presupuesto - LocalMarket</title>
                <meta charset="utf-8">
            </head>
            <body>
                ${budgetHTML}
                <div style="text-align: center; margin-top: 20px;">
                    <button onclick="window.print()" style="background: linear-gradient(135deg, #f56416 0%, #772014 100%); color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 1em; cursor: pointer; font-weight: 600;">
                        Imprimir Presupuesto
                    </button>
                </div>
            </body>
            </html>
        `);
        printWindow.document.close();
        
        showNotification('Presupuesto generado', 'success');
    }
    
    // Sistema de notificaciones
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        Object.assign(notification.style, {
            position: 'fixed',
            top: '100px',
            right: '20px',
            background: type === 'success' ? 'linear-gradient(135deg, #ffd97d 0%, #fff689 100%)' : 
                       type === 'warning' ? 'linear-gradient(135deg, #f56416 0%, #772014 100%)' :
                       'linear-gradient(135deg, #7c7c7c 0%, #5a5a5a 100%)',
            color: type === 'warning' ? 'white' : '#772014',
            padding: '15px 20px',
            borderRadius: '10px',
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
            zIndex: '9999',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontWeight: '600',
            animation: 'slideIn 0.3s ease'
        });
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    // Agregar estilos de animación
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(400px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // ==================== MODAL DE PRODUCTO ====================
    
    const productModal = document.getElementById('productModal');
    const productCards = document.querySelectorAll('.product-card');

    if (productModal && productCards.length > 0) {
        const modalInstance = new bootstrap.Modal(productModal);
        
        productCards.forEach(card => {
            card.addEventListener('click', function() {
                // Obtener datos del producto
                const img = this.querySelector('.product-img').src;
                const title = this.querySelector('.product-title').textContent.trim();
                const marca = this.querySelector('.product-brand').textContent.replace('Marca:', '').trim();
                const price = this.querySelector('.product-price').textContent.trim().replace('$', '');
                const description = this.querySelector('.product-description').textContent.trim();
                const seller = this.querySelector('.product-seller').textContent.trim();
                
                // Generar ID único
                const productId = title.toLowerCase().replace(/\s+/g, '-');
                
                // Llenar el modal
                document.getElementById('modal-product-image').src = img;
                document.getElementById('modal-product-title').textContent = title;
                document.getElementById('modal-product-marca').textContent = marca;
                document.getElementById('modal-product-price').textContent = price;
                document.getElementById('modal-product-description').textContent = description;
                document.getElementById('modal-product-seller').textContent = seller;
                
                // Actualizar botón de favoritos
                const modalFavBtn = document.getElementById('modal-favorite-btn');
                if (modalFavBtn) {
                    modalFavBtn.dataset.productId = productId;
                    modalFavBtn.dataset.productData = JSON.stringify({
                        id: productId,
                        title: title,
                        marca: marca,
                        price: price,
                        image: img,
                        seller: seller
                    });
                    
                    const isFavorite = favorites.some(fav => fav.id === productId);
                    if (isFavorite) {
                        modalFavBtn.classList.add('active');
                        modalFavBtn.querySelector('i').className = 'bi bi-star-fill';
                    } else {
                        modalFavBtn.classList.remove('active');
                        modalFavBtn.querySelector('i').className = 'bi bi-star';
                    }
                }
                
                modalInstance.show();
            });
        });
    }
    
    // Botón de favoritos en el modal
    const modalFavoriteBtn = document.getElementById('modal-favorite-btn');
    if (modalFavoriteBtn) {
        modalFavoriteBtn.addEventListener('click', function() {
            const productData = JSON.parse(this.dataset.productData || '{}');
            const productId = this.dataset.productId;
            
            const isFavorite = favorites.some(fav => fav.id === productId);
            
            if (isFavorite) {
                removeFromFavorites(productId);
                this.classList.remove('active');
                this.querySelector('i').className = 'bi bi-star';
            } else {
                addToFavorites(productData);
                this.classList.add('active');
                this.querySelector('i').className = 'bi bi-star-fill';
            }
        });
    }
    
    // Botón de carrito en el modal
    const modalCartBtn = document.getElementById('modal-cart-btn');
    if (modalCartBtn) {
        modalCartBtn.addEventListener('click', function() {
            const productTitle = document.getElementById('modal-product-title').textContent;
            
            this.innerHTML = '<i class="bi bi-check-lg"></i> <span>¡Agregado!</span>';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = '<i class="bi bi-cart-plus"></i> <span>Agregar al Carrito</span>';
                this.disabled = false;
            }, 2000);
            
            showNotification(`"${productTitle}" agregado al carrito`, 'success');
        });
    }
    
    // ==================== BÚSQUEDA Y VISTAS ====================
    
    // Toggle de lista/grid
    const toggleBtn = document.querySelector('.toggle-view-btn');
    const productsContainer = document.querySelector('.products-container');

    if (toggleBtn && productsContainer) {
        toggleBtn.addEventListener('click', () => {
            const isList = productsContainer.classList.toggle('list-view');
            productsContainer.classList.toggle('grid-view', !isList);

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
    const searchBox = document.getElementById("searchbox");
    if (searchBtn && searchBox) {
        searchBtn.addEventListener("click", () => {
            const query = searchBox.value.trim();
            const url = query ? `?q=${encodeURIComponent(query)}` : window.location.pathname;
            window.location.href = url;
        });
    }

    // Botón para seleccionar imagen y vista previa
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
                imagePreview.src = imagePreview.dataset.placeholder || "";
            }
        });
    }
    
    // Función auxiliar para obtener el CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});