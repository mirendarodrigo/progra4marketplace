document.addEventListener("DOMContentLoaded", () => {
    const resultEl = document.getElementById("result");

    Quagga.init({
        inputStream: {
            name: "Live",
            type: "LiveStream",
            target: document.querySelector("#scanner-container"),
            constraints: {
                facingMode: "environment"
            }
        },
        decoder: {
            readers: ["ean_reader", "upc_reader", "code_128_reader"]
        }
    }, function(err) {
        if (err) {
            console.error(err);
            return;
        }
        Quagga.start();
    });

    let scanning = true;

    Quagga.onDetected(function(data) {
        if (!scanning) return;

        let code = data.codeResult.code;
        resultEl.textContent = code;
        scanning = false; // pausar detección

        // Consultar en el backend si el código existe
        fetch(`/scanner/check_barcode/?barcode=${code}`)
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    mostrarModalExistente(data, code);
                } else {
                    mostrarModalNuevo(code);
                }
            })
            .catch(err => {
                console.error("Error al consultar:", err);
                scanning = true;
            });
    });

    // --- Funciones auxiliares ---

    function mostrarModalExistente(producto, code) {
        const modal = document.getElementById("modal");
        modal.innerHTML = `
            <div class="modal-content">
                <h4>${producto.title}</h4>
                <p><strong>Marca:</strong> ${producto.marca}</p>
                <p><strong>Precio:</strong> $${producto.price}</p>
                <p><strong>Stock:</strong> ${producto.stock}</p>
                ${producto.image ? `<img src="${producto.image}" alt="${producto.title}" style="max-width: 150px; border-radius: 8px; margin: 1rem 0;">` : ""}
                <div class="modal-actions">
                    <button id="modificarBtn" class="modal-btn modal-btn-primary">Modificar</button>
                    <button id="cancelarBtn" class="modal-btn modal-btn-secondary">Cancelar</button>
                </div>
            </div>
        `;
        modal.style.display = "flex";

        document.getElementById("modificarBtn").onclick = () => {
            // Redirigir a la vista de modificar producto (mod_product)
            window.location.href = `/productos/${producto.id}/modificar/`;
        };

        document.getElementById("cancelarBtn").onclick = () => {
            cerrarModal();
        };
    }

    function mostrarModalNuevo(code) {
        const modal = document.getElementById("modal");
        modal.innerHTML = `
            <div class="modal-content">
                <h4>¡Producto nuevo!</h4>
                <p><strong>Código:</strong> ${code}</p>
                <p>Este código de barras no está registrado en el sistema.</p>
                <div class="modal-actions">
                    <button id="agregarBtn" class="modal-btn modal-btn-primary">Agregar Producto</button>
                    <button id="descartarBtn" class="modal-btn modal-btn-secondary">Descartar</button>
                </div>
            </div>
        `;
        modal.style.display = "flex";

        document.getElementById("agregarBtn").onclick = () => {
            // Redirigir a add_product con el código de barras
            window.location.href = `/productos/add/?barcode=${code}`;
        };

        document.getElementById("descartarBtn").onclick = () => {
            cerrarModal();
        };
    }

    function cerrarModal() {
        const modal = document.getElementById("modal");
        modal.style.display = "none";
        modal.innerHTML = "";
        scanning = true;
        Quagga.start(); // reanudar el escáner
    }
});