document.addEventListener("DOMContentLoaded", () => {

    // ==================== SISTEMA DE FAVORITOS ====================

    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    let budgetMode = false;

    const favoritesToggle = document.getElementById('favoritesToggle');
    const favoritesDropdown = document.getElementById('favoritesDropdown');
    const favoritesBadge = document.getElementById('favoritesBadge');
    const favoritesList = document.getElementById('favoritesList');
    const btnBudget = document.getElementById('btnBudget');
    const budgetActions = document.getElementById('budgetActions');
    const btnCancelBudget = document.getElementById('btnCancelBudget');
    const btnGenerateBudget = document.getElementById('btnGenerateBudget');

    updateFavoritesBadge();
    renderFavorites();

    if (favoritesToggle && favoritesDropdown) {
        favoritesToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            favoritesDropdown.classList.toggle('show');
            // Cierra el carrito si está abierto (verificando si existe la variable)
            const cartDropdownEl = document.getElementById('cartDropdown');
            if (cartDropdownEl) cartDropdownEl.classList.remove('show');
        });

        document.addEventListener('click', (e) => {
            if (!favoritesDropdown.contains(e.target) && !favoritesToggle.contains(e.target)) {
                favoritesDropdown.classList.remove('show');
            }
        });
    }

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

        attachFavoriteItemListeners();
    }

    function attachFavoriteItemListeners() {
        document.querySelectorAll('.btn-add-cart').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                const product = favorites.find(fav => fav.id === id);
                if (product) {
                    addToCartSystem(product);
                    showNotification(`"${product.title}" agregado al carrito`, 'success');
                }
            });
        });

        document.querySelectorAll('.btn-remove-fav').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                removeFromFavorites(id);
            });
        });
    }

    function addToFavorites(product) {
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

    function removeFromFavorites(id) {
        favorites = favorites.filter(fav => fav.id !== id);
        localStorage.setItem('favorites', JSON.stringify(favorites));
        updateFavoritesBadge();
        renderFavorites();

        // Actualizar botón del modal si está abierto
        const modalFavBtn = document.getElementById('modal-favorite-btn');
        if (modalFavBtn && modalFavBtn.dataset.productId === id) {
            // Si usamos la función auxiliar de UI:
            if (typeof updateFavBtnUI === 'function') {
                updateFavBtnUI(modalFavBtn, false);
            } else {
                modalFavBtn.classList.remove('active');
                const icon = modalFavBtn.querySelector('i');
                if (icon) icon.className = 'bi bi-star';
            }
        }

        showNotification('Producto eliminado de favoritos', 'info');
    }

    // Helper para UI del botón favoritos
    function updateFavBtnUI(btn, isActive) {
        const icon = btn.querySelector('i');
        if (isActive) {
            btn.classList.add('active', 'btn-warning');
            btn.classList.remove('btn-outline-warning');
            if (icon) icon.className = 'bi bi-star-fill';
            btn.innerHTML = '<i class="bi bi-star-fill"></i> Quitar de Favoritos';
        } else {
            btn.classList.remove('active', 'btn-warning');
            btn.classList.add('btn-outline-warning');
            if (icon) icon.className = 'bi bi-star';
            btn.innerHTML = '<i class="bi bi-star"></i> Favoritos';
        }
    }

    if (btnBudget) {
        btnBudget.addEventListener('click', () => {
            budgetMode = !budgetMode;
            btnBudget.classList.toggle('active');
            budgetActions.classList.toggle('d-none', !budgetMode);
            renderFavorites();
        });
    }

    if (btnCancelBudget) {
        btnCancelBudget.addEventListener('click', () => {
            budgetMode = false;
            btnBudget.classList.remove('active');
            budgetActions.classList.add('d-none');
            renderFavorites();
        });
    }

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

        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="icon" type="image/png" href="/static/img/fav.png">
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

    // ==================== SISTEMA DE CARRITO ====================

    let cart = JSON.parse(localStorage.getItem('cart') || '[]');

    const cartToggle = document.getElementById('cartToggle');
    const cartDropdown = document.getElementById('cartDropdown');
    const cartBadge = document.getElementById('cartBadge');
    const cartList = document.getElementById('cartList');
    const cartFooter = document.getElementById('cartFooter');
    const cartTotalAmount = document.getElementById('cartTotalAmount');
    const btnClearCart = document.getElementById('btnClearCart');
    const btnCheckout = document.getElementById('btnCheckout');

    updateCartBadge();
    renderCart();

    if (cartToggle && cartDropdown) {
        cartToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            cartDropdown.classList.toggle('show');
            if (favoritesDropdown) favoritesDropdown.classList.remove('show');
        });

        document.addEventListener('click', (e) => {
            if (!cartDropdown.contains(e.target) && !cartToggle.contains(e.target)) {
                cartDropdown.classList.remove('show');
            }
        });
    }

    function updateCartBadge() {
        if (cartBadge) {
            const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
            if (totalItems > 0) {
                cartBadge.textContent = totalItems;
                cartBadge.classList.remove('d-none');
            } else {
                cartBadge.classList.add('d-none');
            }
        }
    }

    function calculateCartTotal() {
        return cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
    }

    function renderCart() {
        if (!cartList) return;

        if (cart.length === 0) {
            cartList.innerHTML = `
                <div class="empty-cart">
                    <i class="bi bi-cart-x"></i>
                    <p>Tu carrito está vacío</p>
                </div>
            `;
            if (cartFooter) cartFooter.classList.add('d-none');
            return;
        }

        cartList.innerHTML = cart.map(item => `
            <div class="cart-item" data-id="${item.id}">
                <img src="${item.image}" alt="${item.title}" class="cart-item-img">
                <div class="cart-item-info">
                    <div class="cart-item-title">${item.title}</div>
                    <div class="cart-item-price">$${item.price} c/u</div>
                    <div class="cart-item-controls">
                        <div class="quantity-controls">
                            <button class="btn-quantity btn-decrease" data-id="${item.id}">
                                <i class="bi bi-dash"></i>
                            </button>
                            <span class="quantity-display">${item.quantity}</span>
                            <button class="btn-quantity btn-increase" data-id="${item.id}">
                                <i class="bi bi-plus"></i>
                            </button>
                        </div>
                        <button class="btn-remove-cart" data-id="${item.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        if (cartFooter) {
            cartFooter.classList.remove('d-none');
            if (cartTotalAmount) {
                cartTotalAmount.textContent = `$${calculateCartTotal().toFixed(2)}`;
            }
        }

        attachCartItemListeners();
    }

    function attachCartItemListeners() {
        document.querySelectorAll('.btn-increase').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                updateCartItemQuantity(id, 1);
            });
        });

        document.querySelectorAll('.btn-decrease').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                updateCartItemQuantity(id, -1);
            });
        });

        document.querySelectorAll('.btn-remove-cart').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                removeFromCart(id);
            });
        });
    }

    function addToCartSystem(product) {
        const existingItem = cart.find(item => item.id === product.id);

        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({ ...product, quantity: 1 });
        }

        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartBadge();
        renderCart();
        return true;
    }

    function updateCartItemQuantity(id, change) {
        const item = cart.find(item => item.id === id);

        if (item) {
            item.quantity += change;

            if (item.quantity <= 0) {
                removeFromCart(id);
                return;
            }

            localStorage.setItem('cart', JSON.stringify(cart));
            updateCartBadge();
            renderCart();
        }
    }

    function removeFromCart(id) {
        cart = cart.filter(item => item.id !== id);
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartBadge();
        renderCart();
        showNotification('Producto eliminado del carrito', 'info');
    }

    if (btnClearCart) {
        btnClearCart.addEventListener('click', () => {
            if (cart.length === 0) return;

            if (confirm('¿Estás seguro de que quieres vaciar el carrito?')) {
                cart = [];
                localStorage.setItem('cart', JSON.stringify(cart));
                updateCartBadge();
                renderCart();
                showNotification('Carrito vaciado', 'info');
            }
        });
    }

    if (btnCheckout) {
        btnCheckout.addEventListener('click', async () => {
            if (cart.length === 0) {
                showNotification('Tu carrito está vacío', 'warning');
                return;
            }

            btnCheckout.disabled = true;
            btnCheckout.classList.add('loading');

            try {
                const items = cart.map(item => ({
                    title: item.title,
                    quantity: item.quantity,
                    unit_price: parseFloat(item.price),
                    currency_id: "ARS"
                }));

                const response = await fetch('/crear-preferencia/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ items })
                });

                if (!response.ok) {
                    throw new Error('Error al crear la preferencia de pago');
                }

                const data = await response.json();
                window.location.href = data.init_point;

            } catch (error) {
                console.error('Error:', error);
                showNotification('Error al procesar la compra. Intenta nuevamente.', 'warning');
                btnCheckout.disabled = false;
                btnCheckout.classList.remove('loading');
            }
        });
    }

    // ==================== SISTEMA DE NOTIFICACIONES ====================

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

    // ==================== MODAL DE PRODUCTO (Lógica Unificada) ====================

    const productModalElement = document.getElementById('productModal');

    if (productModalElement) {
        const modalInstance = new bootstrap.Modal(productModalElement);

        // ---------------------------------------------------------
        // HELPER: Función para abrir el modal de vendedor
        // AHORA ACEPTA "productContext" PARA CONFIGURAR EL CHAT
        // ---------------------------------------------------------
        window.openSellerModalById = function (sellerId, sellerName, productContext = null) {
            const modalEl = document.getElementById('sellerModal');
            if (!modalEl || !sellerId) return;

            const modalSeller = bootstrap.Modal.getOrCreateInstance(modalEl);

            // Elementos de info del vendedor
            const nameEl = document.getElementById('seller-name');
            const emailEl = document.getElementById('seller-email');
            const locEl = document.getElementById('seller-localidad');
            const telEl = document.getElementById('seller-telefono');
            const countEl = document.getElementById('seller-products-count');

            // Elemento botón de chat (AHORA VIVE AQUÍ)
            const chatBtn = document.getElementById('modal-chat-btn');

            // 1. Resetear UI
            if (nameEl) nameEl.textContent = sellerName || '—';
            if (emailEl) emailEl.textContent = 'Cargando...';
            if (locEl) locEl.textContent = 'Cargando...';
            if (telEl) telEl.textContent = 'Cargando...';
            if (countEl) countEl.textContent = '...';

            // 2. Configurar Botón de Chat dentro de este modal
            if (chatBtn) {
                if (productContext) {
                    chatBtn.classList.remove('d-none');
                    // Limpiamos eventos anteriores clonando o reasignando
                    chatBtn.onclick = function () {
                        const params = new URLSearchParams({
                            product: productContext.id || '',
                            title: productContext.title || '',
                            price: productContext.price || '',
                            brand: productContext.marca || ''
                        });
                        window.location.href = `/chat/start/${sellerId}/?${params.toString()}`;
                    };
                } else {
                    // Si abrimos el modal sin contexto de producto, ocultamos el botón
                    chatBtn.classList.add('d-none');
                }
            }

            modalSeller.show();

            // 3. Fetch de datos extra
            fetch(`/api/seller/${sellerId}/`, { headers: { 'Accept': 'application/json' } })
                .then(r => r.ok ? r.json() : Promise.reject(r))
                .then(data => {
                    if (nameEl && data.name) nameEl.textContent = data.name;
                    if (emailEl) emailEl.textContent = data.email || '—';
                    if (locEl) locEl.textContent = data.localidad || '—';
                    if (telEl) telEl.textContent = data.telefono || '—';
                    if (countEl) countEl.textContent = (data.products_count != null) ? data.products_count : 0;
                })
                .catch(err => console.error("Error cargando vendedor", err));
        };

        function openProductModal(cardElement) {
            // 1. OBTENER DATOS 
            const img = cardElement.querySelector('.product-img')?.src || cardElement.querySelector('img')?.src || '';

            const title = cardElement.dataset.title || (cardElement.querySelector('.product-title')?.textContent || '').trim();

            let rawPrice = cardElement.dataset.price || (cardElement.querySelector('.product-price')?.textContent || '');
            const price = rawPrice.replace('$', '').replace(',', '.').trim();

            const description = cardElement.dataset.description || (cardElement.querySelector('.product-description')?.textContent || '').trim();
            const brand = cardElement.dataset.brand || (cardElement.querySelector('.product-brand')?.textContent || '').replace('Marca:', '').trim();

            let sellerId = cardElement.dataset.sellerId;
            let sellerName = cardElement.dataset.sellerName;

            if (!sellerId) {
                const cardSellerBtn = cardElement.querySelector('button[data-seller-id]');
                sellerId = cardSellerBtn?.dataset.sellerId || '';
                sellerName = cardSellerBtn?.dataset.sellerName ||
                    (cardElement.querySelector('.product-seller')?.textContent.trim() || 'Vendedor');
            }

            const productId = title.toLowerCase().replace(/\s+/g, '-');

            // Objeto producto
            const productObj = {
                id: productId,
                title: title,
                price: price,
                image: img,
                marca: brand,
                seller: sellerName
            };

            // 2. RELLENAR LA UI DEL MODAL
            const elImg = document.getElementById('modal-product-image');
            if (elImg) elImg.src = img;

            const elTitle = document.getElementById('modal-product-title');
            if (elTitle) elTitle.textContent = title;

            const elMarca = document.getElementById('modal-product-marca');
            if (elMarca) elMarca.textContent = brand;

            const elPrice = document.getElementById('modal-product-price');
            if (elPrice) elPrice.textContent = price;

            const elDesc = document.getElementById('modal-product-description');
            if (elDesc) elDesc.textContent = description;

            const elSell = document.getElementById('modal-product-seller');
            if (elSell) elSell.textContent = sellerName;

            // 3. CONFIGURAR BOTÓN "AGREGAR AL CARRITO"
            const addToCartBtn = document.getElementById('modal-cart-btn');
            if (addToCartBtn) {
                addToCartBtn.onclick = function () {
                    addToCartSystem(productObj);
                    showNotification(`"${title}" agregado al carrito`, 'success');
                    modalInstance.hide();
                };
            }

            // 4. CONFIGURAR BOTÓN "FAVORITOS"
            const modalFavBtn = document.getElementById('modal-favorite-btn');
            if (modalFavBtn) {
                const isFav = favorites.some(f => f.id === productId);
                updateFavBtnUI(modalFavBtn, isFav);

                modalFavBtn.onclick = function () {
                    const currentFavState = favorites.some(f => f.id === productId);
                    if (currentFavState) {
                        removeFromFavorites(productId);
                        updateFavBtnUI(modalFavBtn, false);
                    } else {
                        addToFavorites(productObj);
                        updateFavBtnUI(modalFavBtn, true);
                    }
                };
            }

            // 5. CONFIGURAR BOTÓN "PUBLICADO POR" (En el modal de producto)
            const sellerProfileBtn = document.getElementById('modal-seller-btn');
            if (sellerProfileBtn) {
                sellerProfileBtn.disabled = !sellerId;
                sellerProfileBtn.onclick = function () {
                    // IMPORTANTE: Pasamos el productObj para que el chat funcione
                    if (sellerId) window.openSellerModalById(sellerId, sellerName, productObj);
                };
            }

            // 7. MOSTRAR MODAL
            modalInstance.show();
        }

        // --- HELPERS PARA CREAR CONTEXTO DESDE LA TARJETA (PARA BOTÓN VENDEDOR) ---
        function getContextFromCard(card) {
            const title = card.dataset.title || (card.querySelector('.product-title')?.textContent || '').trim();
            let rawPrice = card.dataset.price || (card.querySelector('.product-price')?.textContent || '');
            const price = rawPrice.replace('$', '').replace(',', '.').trim();
            const brand = card.dataset.brand || (card.querySelector('.product-brand')?.textContent || '').replace('Marca:', '').trim();
            const productId = title.toLowerCase().replace(/\s+/g, '-');

            return {
                id: productId,
                title: title,
                price: price,
                marca: brand
            };
        }

        // CASO A: LISTA DE PRODUCTOS (Página Explorar)
        const productCards = document.querySelectorAll('.product-card');
        if (productCards.length > 0) {
            productCards.forEach(card => {
                card.addEventListener('click', (e) => {
                    // 1. ¿El clic fue en el botón del vendedor?
                    const sellerBtn = e.target.closest('button[data-seller-id]');
                    if (sellerBtn) {
                        e.stopPropagation();
                        e.preventDefault();

                        const sId = sellerBtn.dataset.sellerId;
                        const sName = sellerBtn.dataset.sellerName;
                        const context = getContextFromCard(card); // Obtenemos datos del producto

                        window.openSellerModalById(sId, sName, context);
                        return;
                    }
                    // 2. Si es otro botón/enlace, ignorar
                    if (e.target.closest('button') || e.target.closest('a')) return;
                    
                    // 3. Abrir modal de producto
                    openProductModal(card);
                });
            });
        }

        // CASO B: CARRUSEL DEL HOME
        const homeCards = document.querySelectorAll('.carousel-card-trigger');
        if (homeCards.length > 0) {
            homeCards.forEach(card => {
                card.addEventListener('click', (e) => {
                    // Misma lógica para el botón vendedor si existiera en el Home (aunque ahí está oculto)
                    const sellerBtn = e.target.closest('button[data-seller-id]');
                    if (sellerBtn) {
                        e.stopPropagation(); e.preventDefault();
                        // En Home los datos están en dataset del contenedor principal (card), no botones internos
                        // pero el helper getContextFromCard maneja dataset también.
                        const context = getContextFromCard(card);
                        const sId = sellerBtn.dataset.sellerId || card.dataset.sellerId;
                        const sName = sellerBtn.dataset.sellerName || card.dataset.sellerName;
                        window.openSellerModalById(sId, sName, context);
                        return;
                    }
                    
                    if (e.target.closest('button') || e.target.closest('a')) return;
                    openProductModal(card);
                });
            });
        }

        // ==================== MODAL DEL VENDEDOR (Clicks externos) ====================
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('#modal-seller-btn');
            if (btn) {
                e.stopPropagation();
            }
        });
    }

    // ==================== BÚSQUEDA Y VISTAS ====================

    const toggleBtn = document.querySelector('.toggle-view-btn');
    const productsContainer = document.querySelector('.products-container');

    if (toggleBtn && productsContainer) {
        toggleBtn.addEventListener('click', () => {
            const isList = productsContainer.classList.toggle('list-view');
            productsContainer.classList.toggle('grid-view', !isList);

            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.className = isList ? 'bi bi-grid-3x3-gap' : 'bi bi-list-ul';
            }
        });
    }

    // === BÚSQUEDA Y VISTAS (CON ORDENAMIENTO) ===

    const searchBtn = document.getElementById("searchbtn");
    const searchBox = document.getElementById("searchbox");
    const sortOptions = document.getElementById("sortOptions");

    function performSearchAndSort() {
        if (!searchBox || !sortOptions) return;

        const query = searchBox.value.trim();
        const sortValue = sortOptions.value;
        const params = new URLSearchParams();

        if (query) params.append('q', query);
        params.append('sort', sortValue);

        window.location.href = window.location.pathname + '?' + params.toString();
    }

    if (searchBtn) {
        searchBtn.addEventListener("click", performSearchAndSort);
    }

    if (sortOptions) {
        sortOptions.addEventListener("change", performSearchAndSort);
    }


    // ==================== ADD/MOD PRODUCT - PREVIEW DE IMAGEN ====================

    const selectImageBtn = document.getElementById("selectImageBtn");
    const imageInput = document.getElementById("id_image");
    const imagePreview = document.getElementById("imagePreview");

    if (selectImageBtn && imageInput && imagePreview) {
        selectImageBtn.addEventListener("click", () => {
            imageInput.click();
        });

        imageInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (ev) {
                    imagePreview.src = ev.target.result;
                }
                reader.readAsDataURL(file);
            } else {
                imagePreview.src = imagePreview.dataset.placeholder || "";
            }
        });
    }

    // ==================== ADD/MOD PRODUCT - CONTROLES DE STOCK ====================

    const stockInput = document.getElementById('id_stock');

    window.incrementStock = function () {
        if (stockInput) {
            let currentValue = parseInt(stockInput.value) || 0;
            stockInput.value = currentValue + 1;
        }
    }

    window.decrementStock = function () {
        if (stockInput) {
            let currentValue = parseInt(stockInput.value) || 0;
            if (currentValue > 0) {
                stockInput.value = currentValue - 1;
            }
        }
    }

    // ==================== ADD PRODUCT - CÓDIGO DE BARRAS DESDE URL ====================

    const barcodeInput = document.getElementById('id_barcode');
    if (barcodeInput) {
        const urlParams = new URLSearchParams(window.location.search);
        const barcodeParam = urlParams.get('barcode');
        if (barcodeParam) {
            barcodeInput.value = barcodeParam;
        }
    }

    // ==================== UTILIDADES ====================

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

    // Dropdown del usuario
    const avatarBtn = document.getElementById("userAvatarBtn");
    const userDropdown = document.getElementById("userDropdown");

    if (avatarBtn && userDropdown) {
        avatarBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle("show");
        });

        document.addEventListener("click", (e) => {
            if (!userDropdown.contains(e.target) && !avatarBtn.contains(e.target)) {
                userDropdown.classList.remove("show");
            }
        });
    }

}); // <-- Cierre correcto del DOMContentLoaded


    // ==================== BÚSQUEDA POR VOZ ====================

document.addEventListener('DOMContentLoaded', () => {
    // Verificar compatibilidad del navegador
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn("Búsqueda por voz no soportada en este navegador.");
        // Opcional: Ocultar el botón si no es compatible
        const voiceButton = document.getElementById('voice-search-button');
        if(voiceButton) voiceButton.style.display = 'none';
        return;
    }

    // Obtener referencias a los elementos
    const voiceButton = document.getElementById('voice-search-button');
    const searchInput = document.querySelector('.search-input'); // Usamos la clase del input

    // Crear la instancia de reconocimiento
    const recognition = new SpeechRecognition();
    recognition.lang = 'es-AR'; // ¡Importante! Configurar el idioma (Español Argentina)
    recognition.interimResults = false; // No queremos resultados parciales
    recognition.maxAlternatives = 1; // Solo la mejor transcripción

    // Configurar el clic del botón
    voiceButton.addEventListener('click', () => {
        try {
            recognition.start();
            voiceButton.innerHTML = '🎧'; // Cambia el ícono a "Escuchando"
            voiceButton.classList.add('listening');
        } catch(e) {
            console.error("Error al iniciar el reconocimiento de voz:", e);
            alert("No se pudo iniciar el reconocimiento de voz. ¿Ya diste permiso?");
        }
    });

    // Cuando el reconocimiento termina
    recognition.onend = () => {
        voiceButton.innerHTML = '🎤'; // Vuelve al ícono original
        voiceButton.classList.remove('listening');
    };

    // Cuando se obtiene un resultado (la transcripción)
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;

        // Pone el texto transcripto en la barra de búsqueda
        searchInput.value = transcript;

        // ¡AQUÍ ESTÁ LA MAGIA!
        // Envía el formulario automáticamente
        if (searchInput.form) {
             searchInput.form.submit();
        } else {
             console.error("El input de búsqueda no está dentro de un <form>");
        }
    };

    // Manejo de errores
    recognition.onerror = (event) => {
        if (event.error === 'no-speech') {
            alert("No se detectó voz. Intentá otra vez.");
        } else if (event.error === 'audio-capture') {
            alert("Error al capturar el audio. ¿El micrófono funciona?");
        } else if (event.error === 'not-allowed') {
            alert("Permiso denegado para el micrófono. Habilitalo en la configuración del navegador.");
        }
    };

});