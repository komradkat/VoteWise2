document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('click', function(event) {

    const btn = event.target.closest('.toggle-password');
    if (!btn) return;

    // Find the actual password field next to the button
    const wrapper = btn.closest('.input-wrapper');
    const input = wrapper.querySelector('input[type="password"], input[type="text"]');
    const icon = btn.querySelector("i");

    if (!input) {
        console.error("No password input found inside .input-wrapper");
        return;
    }

    const isHidden = input.type === 'password';
    input.type = isHidden ? 'text' : 'password';

    // Toggle eye/eye-slash icon
    if (icon) {
        icon.classList.toggle("fa-eye");
        icon.classList.toggle("fa-eye-slash");
    }
});

    // 2. Focus first input on load (Keep this part)
    document.querySelector('input[name="username"]')?.focus();

    // 3. Form submit animation (Keep this part)
    document.querySelector('.auth-form')?.addEventListener('submit', function() {
        const btn = this.querySelector('.cta-button');
        if (btn) {
            btn.innerHTML = 'Logging in...';
            btn.disabled = true;
        }
    });
});