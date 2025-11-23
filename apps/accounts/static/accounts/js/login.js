document.addEventListener('DOMContentLoaded', function() {
    
    // --- START OF EVENT DELEGATION WORKAROUND ---
    
    // Attach ONE listener to the whole document body
    document.body.addEventListener('click', function(event) {
        
        // Check if the clicked element (or its closest ancestor) is the toggle button
        const btn = event.target.closest('.toggle-password');
        
        if (btn) {
            // Found the button! Now find the input field by its ID
            const input = document.getElementById('id_password'); 

            if (input) {
                // Toggle the input type
                const type = input.type === 'password' ? 'text' : 'password';
                input.type = type;
                
                // Update the button text
                btn.textContent = type === 'text' ? 'Hide' : 'Show';
            } else {
                console.error("Input field 'id_password' not found.");
            }
        }
    });

    // --- END OF EVENT DELEGATION WORKAROUND ---

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