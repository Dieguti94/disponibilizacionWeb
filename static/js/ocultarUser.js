document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const userMenuWrapper = document.querySelector('.user-menu-wrapper');
    function toggleUserMenu() {
        if (menuToggle && userMenuWrapper) {
            if (menuToggle.checked && window.innerWidth < 530) {
                userMenuWrapper.style.display = 'none';
            } else {
                userMenuWrapper.style.display = '';
            }
        }
    }
    if (menuToggle && userMenuWrapper) {
        menuToggle.addEventListener('change', toggleUserMenu);
        window.addEventListener('resize', toggleUserMenu);
    }
    // Ejecutar al cargar por si ya está abierto en mobile
    toggleUserMenu();
});