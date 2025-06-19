document.addEventListener('DOMContentLoaded', function() {
    const menuIcon = document.querySelector('.menu-icon');
    const logo = document.querySelector('.logo');
    let isSticky = false;

    function checkLogoVisibility() {
        if (!logo || !menuIcon) return;
        const rect = logo.getBoundingClientRect();
        if (rect.bottom < 0 && !isSticky) {
            // Oculta, mueve y muestra en la nueva posición
            menuIcon.classList.add('hide-menu');
            setTimeout(() => {
                menuIcon.classList.add('sticky-left');
                menuIcon.classList.remove('hide-menu');
                isSticky = true;
            }, 200); // Solo espera el fade out
        } else if (rect.bottom >= 0 && isSticky) {
            // Oculta, mueve y muestra en la posición original
            menuIcon.classList.add('hide-menu');
            setTimeout(() => {
                menuIcon.classList.remove('sticky-left');
                menuIcon.classList.remove('hide-menu');
                isSticky = false;
            }, 200);
        }
    }

    window.addEventListener('scroll', checkLogoVisibility);
    checkLogoVisibility();
});