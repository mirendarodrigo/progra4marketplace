// === PREVIEW DE AVATAR AL INSTANTE (GLOBAL) ===
// Funciona aunque el script se cargue antes/depues: usa event delegation y busca IDs al vuelo.
(function () {
  // Helper: aplicar una URL de objeto a ambos previews (img o box) y al navbar
  function applyPreview(url) {
    try {
      // 1) IMG de preview (si existe)
      var img = document.getElementById('avatarPreviewImg');
      if (img) {
        img.src = url;
        img.onload = function () { try { URL.revokeObjectURL(url); } catch (_) {} };
      }

      // 2) BOX con background (si existe)
      var box = document.getElementById('avatarPreviewBox');
      if (box) {
        box.style.setProperty('background-image', 'url("' + url + '")', 'important');
        box.style.backgroundSize = 'cover';
        box.style.backgroundPosition = 'center';
        // Si solo hubo box (sin img), liberamos luego
        if (!img) setTimeout(function(){ try { URL.revokeObjectURL(url); } catch(_){} }, 10000);
      }

      // 3) Avatar del navbar (si existe)
      var nav = document.getElementById('navbarAvatarImg');
      if (nav) {
        nav.src = url;
        nav.onload = function () { try { URL.revokeObjectURL(url); } catch (_) {} };
      }
    } catch (e) {
      // noop
    }
  }

  // Delegación global: cualquier <input type="file" id="profile-photo-input"> que cambie
  document.addEventListener('change', function (e) {
    var t = e.target;
    if (!t || t.id !== 'profile-photo-input') return;

    var file = t.files && t.files[0];
    if (!file) return;

    var url = URL.createObjectURL(file);
    applyPreview(url);
  });

  // Soporte: permitir re-seleccionar el mismo archivo y seguir disparando 'change'
  document.addEventListener('click', function (e) {
    var t = e.target;
    // Si clickeaste el propio input (visible) o un label que lo dispara
    if ((t && t.id === 'profile-photo-input') || (t && t.getAttribute && t.getAttribute('for') === 'profile-photo-input')) {
      var input = document.getElementById('profile-photo-input');
      if (input) input.value = null;
    }
  });

  // Drag & drop sobre el contenedor del preview si existe
  function enableDrop(targetEl) {
    if (!targetEl) return;
    var container = targetEl.tagName === 'IMG' ? targetEl.parentElement : targetEl;

    ['dragenter', 'dragover'].forEach(function (ev) {
      container.addEventListener(ev, function (e) {
        e.preventDefault(); e.stopPropagation();
        container.classList && container.classList.add('border-primary');
      });
    });
    ['dragleave', 'drop'].forEach(function (ev) {
      container.addEventListener(ev, function (e) {
        e.preventDefault(); e.stopPropagation();
        container.classList && container.classList.remove('border-primary');
      });
    });
    container.addEventListener('drop', function (e) {
      var file = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (!file) return;

      // Reflejar en el input (para que el form lo envíe al guardar)
      var input = document.getElementById('profile-photo-input');
      if (input) {
        var dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
      }

      var url = URL.createObjectURL(file);
      applyPreview(url);
    });
  }

  // Intentamos activar drop en ambos tipos de preview
  // (si no existen en esta página, no pasa nada)
  enableDrop(document.getElementById('avatarPreviewImg'));
  enableDrop(document.getElementById('avatarPreviewBox'));
})();