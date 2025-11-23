document.addEventListener('DOMContentLoaded', function() {
    // Add form-control class to inputs rendered by Django
    document.querySelectorAll('input').forEach(input => {
        input.classList.add('form-control');
    });
});
