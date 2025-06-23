// login.js - scripts para la página de login

// Control de tabulación y animación de paneles
const container = document.querySelector('.container');
const aboutBtn = document.querySelector('.about-btn');
const loginBtn = document.querySelector('.login-btn');
const sobreNosotrosLink = document.querySelector('.boton-violeta-neon');

function updateTabIndexes() {
    if (container.classList.contains('active')) {
        aboutBtn.tabIndex = "-1";
        loginBtn.tabIndex = "0";
        sobreNosotrosLink.tabIndex = "0";
    } else {
        aboutBtn.tabIndex = "0";
        loginBtn.tabIndex = "-1";
        sobreNosotrosLink.tabIndex = "-1";
    }
}
aboutBtn.addEventListener('click', () => {
    container.classList.add('active');
    document.querySelector('.contact-info').classList.remove('d-none');
    updateTabIndexes();
});
loginBtn.addEventListener('click', () => {
    container.classList.remove('active');
    document.querySelector('.contact-info').classList.add('d-none');
    updateTabIndexes();
});
updateTabIndexes();

// Validación campos vacíos
document.querySelector('.form-signin').addEventListener('submit', function(e) {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    if (!username || !password) {
        e.preventDefault();
        Swal.fire({
            icon: 'warning',
            title: 'Campos vacíos',
            text: 'Por favor completá usuario y contraseña.',
            confirmButtonColor: '#6f42c1'
        });
    }
});
