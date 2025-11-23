// Voting Interface JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const candidateCards = document.querySelectorAll('.candidate-card');
    const submitButton = document.querySelector('.submit-button');
    const modalOverlay = document.querySelector('.modal-overlay');
    const confirmButton = document.querySelector('.modal-button.confirm');
    const cancelButton = document.querySelector('.modal-button.cancel');
    
    // Track selections per position
    const selections = {};
    
    // Initialize selections object
    document.querySelectorAll('.position-section').forEach(section => {
        const positionId = section.dataset.positionId;
        const maxWinners = parseInt(section.dataset.maxWinners) || 1;
        selections[positionId] = {
            maxWinners: maxWinners,
            selected: []
        };
    });
    
    // Handle candidate card clicks
    candidateCards.forEach(card => {
        card.addEventListener('click', function() {
            const positionId = this.dataset.positionId;
            const candidateId = this.dataset.candidateId;
            const position = selections[positionId];
            
            if (this.classList.contains('selected')) {
                // Deselect
                this.classList.remove('selected');
                position.selected = position.selected.filter(id => id !== candidateId);
            } else {
                // Check if we can select more
                if (position.selected.length < position.maxWinners) {
                    this.classList.add('selected');
                    position.selected.push(candidateId);
                } else {
                    // Show alert if max reached
                    showAlert(`You can only select ${position.maxWinners} candidate(s) for this position.`);
                }
            }
            
            updateSubmitButton();
            updateVoteSummary();
        });
    });
    
    // Update submit button state
    function updateSubmitButton() {
        let allPositionsFilled = true;
        
        for (const positionId in selections) {
            if (selections[positionId].selected.length === 0) {
                allPositionsFilled = false;
                break;
            }
        }
        
        submitButton.disabled = !allPositionsFilled;
    }
    
    // Update vote summary
    function updateVoteSummary() {
        const totalSelected = Object.values(selections).reduce((sum, pos) => sum + pos.selected.length, 0);
        const totalPositions = Object.keys(selections).length;
        
        const summaryElement = document.querySelector('.vote-summary p');
        if (summaryElement) {
            summaryElement.innerHTML = `<span class="selected-count">${totalSelected}</span> candidate(s) selected across ${totalPositions} position(s)`;
        }
    }
    
    // Show confirmation modal
    submitButton.addEventListener('click', function() {
        if (!this.disabled) {
            showConfirmationModal();
        }
    });
    
    function showConfirmationModal() {
        // Build selections list
        const selectionsList = document.querySelector('.modal-selections');
        selectionsList.innerHTML = '';
        
        document.querySelectorAll('.position-section').forEach(section => {
            const positionId = section.dataset.positionId;
            const positionName = section.querySelector('.position-header h2').textContent;
            const selectedCandidates = selections[positionId].selected;
            
            if (selectedCandidates.length > 0) {
                const item = document.createElement('div');
                item.className = 'selection-item';
                
                const candidateNames = selectedCandidates.map(candidateId => {
                    const card = document.querySelector(`.candidate-card[data-candidate-id="${candidateId}"]`);
                    return card.querySelector('.candidate-name').textContent;
                }).join(', ');
                
                item.innerHTML = `
                    <strong>${positionName}</strong>
                    <span>${candidateNames}</span>
                `;
                selectionsList.appendChild(item);
            }
        });
        
        modalOverlay.classList.add('active');
    }
    
    // Cancel modal
    cancelButton.addEventListener('click', function() {
        modalOverlay.classList.remove('active');
    });
    
    // Close modal on overlay click
    modalOverlay.addEventListener('click', function(e) {
        if (e.target === modalOverlay) {
            modalOverlay.classList.remove('active');
        }
    });
    
    // Confirm and submit
    confirmButton.addEventListener('click', function() {
        // Create form and submit
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = window.location.href;
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
        
        // Add selections
        for (const positionId in selections) {
            selections[positionId].selected.forEach(candidateId => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = `vote_${positionId}`;
                input.value = candidateId;
                form.appendChild(input);
            });
        }
        
        document.body.appendChild(form);
        form.submit();
    });
    
    // Alert helper
    function showAlert(message) {
        // Simple alert for now, can be enhanced with custom modal
        alert(message);
    }
    
    // Initialize
    updateSubmitButton();
    updateVoteSummary();
});
