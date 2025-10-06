document.addEventListener("DOMContentLoaded", () => {
    const resultEl = document.getElementById("result");

    Quagga.init({
        inputStream: {
            type: "LiveStream",
            constraints: {
                width: 640,
                height: 480,
                facingMode: "environment" 
            },
            target: document.querySelector('#scanner-container')
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

    Quagga.onDetected(function(data) {
        let code = data.codeResult.code;
        resultEl.textContent = code;
        alert("Código detectado: " + code);
        // Quagga.stop(); // 
    });
});
