// Voting Interface JavaScript (Wizard Layout)
document.addEventListener('DOMContentLoaded', function() {
    console.log('Voting JS: Wizard Layout Initialized');
    
    // Elements
    const positionSections = document.querySelectorAll('.position-section');
    const reviewSection = document.getElementById('review-section');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const currentStepSpan = document.getElementById('current-step');
    const totalStepsSpan = document.getElementById('total-steps');
    const finalSubmitBtn = document.getElementById('final-submit-btn');
    const modalOverlay = document.querySelector('.modal-overlay');
    const confirmButton = document.querySelector('.modal-button.confirm');
    const cancelButton = document.querySelector('.modal-button.cancel');
    
    // State
    let currentStep = 0;
    const totalSteps = positionSections.length + 1; // +1 for review
    const selections = {};
    
    // Initialize selections object
    positionSections.forEach((section, index) => {
        const positionId = section.dataset.positionId;
        const maxWinners = parseInt(section.dataset.maxWinners) || 1;
        selections[positionId] = {
            maxWinners: maxWinners,
            selected: [],
            name: section.querySelector('.position-header h2').textContent
        };
        
        // Show first section
        if (index === 0) section.classList.add('active');
    });
    
    // Update total steps UI
    totalStepsSpan.textContent = totalSteps;
    
    // Navigation Handlers
    function updateStep(direction) {
        // Hide current
        if (currentStep < positionSections.length) {
            positionSections[currentStep].classList.remove('active');
        } else {
            reviewSection.classList.remove('active');
        }
        
        // Update index
        if (direction === 'next') {
            currentStep++;
        } else {
            currentStep--;
        }
        
        // Show new
        if (currentStep < positionSections.length) {
            positionSections[currentStep].classList.add('active');
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            reviewSection.classList.add('active');
            populateReview();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        updateNavigationUI();
        updateProgressBar();
    }
    
    function updateNavigationUI() {
        currentStepSpan.textContent = currentStep + 1;
        
        // Prev Button
        prevBtn.disabled = currentStep === 0;
        
        // Next Button
        if (currentStep === totalSteps - 1) {
            nextBtn.style.display = 'none';
        } else {
            nextBtn.style.display = 'flex';
            nextBtn.innerHTML = 'Next <i class="fas fa-arrow-right"></i>';
        }
    }
    
    // Button Listeners
    prevBtn.addEventListener('click', () => updateStep('prev'));
    nextBtn.addEventListener('click', () => updateStep('next'));
    
    // Candidate Selection Logic
    document.querySelectorAll('.candidate-card').forEach(card => {
        card.addEventListener('click', function() {
            const positionId = this.dataset.positionId;
            const candidateId = this.dataset.candidateId;
            const position = selections[positionId];
            
            if (this.classList.contains('selected')) {
                // Deselect
                this.classList.remove('selected');
                position.selected = position.selected.filter(id => id !== candidateId);
            } else {
                // Check limit
                if (position.selected.length < position.maxWinners) {
                    this.classList.add('selected');
                    position.selected.push(candidateId);
                    
                    // Auto-advance if max reached (optional, maybe too aggressive for wizard?)
                    // Let's keep it manual for wizard to allow review, or maybe just highlight 'Next'
                } else {
                    showAlert(`You can only select ${position.maxWinners} candidate(s) for this position.`);
                }
            }
            
            updateProgressBar();
        });
    });
    
    // Populate Review Section
    function populateReview() {
        const list = document.querySelector('.review-list');
        list.innerHTML = '';
        
        for (const positionId in selections) {
            const pos = selections[positionId];
            const item = document.createElement('div');
            item.className = 'review-item';
            
            let selectionText = '<span class="review-selection">No selection</span>';
            if (pos.selected.length > 0) {
                const names = pos.selected.map(id => {
                    const card = document.querySelector(`.candidate-card[data-candidate-id="${id}"]`);
                    return card.querySelector('.candidate-name').textContent;
                }).join(', ');
                selectionText = `<span class="review-selection selected">${names}</span>`;
            }
            
            item.innerHTML = `
                <span class="review-position">${pos.name}</span>
                ${selectionText}
            `;
            list.appendChild(item);
        }
    }
    
    // Final Submit
    finalSubmitBtn.addEventListener('click', function() {
        showConfirmationModal();
    });
    
    // Modal Logic (Reused)
    function showConfirmationModal() {
        const selectionsList = document.querySelector('.modal-selections');
        selectionsList.innerHTML = '';
        
        let hasSelections = false;
        
        for (const positionId in selections) {
            const pos = selections[positionId];
            if (pos.selected.length > 0) {
                hasSelections = true;
                const item = document.createElement('div');
                item.className = 'selection-item';
                
                const names = pos.selected.map(id => {
                    const card = document.querySelector(`.candidate-card[data-candidate-id="${id}"]`);
                    return card.querySelector('.candidate-name').textContent;
                }).join(', ');
                
                item.innerHTML = `
                    <strong>${pos.name}</strong>
                    <span>${names}</span>
                `;
                selectionsList.appendChild(item);
            }
        }
        
        if (!hasSelections) {
            selectionsList.innerHTML = '<div class="selection-item"><span>No candidates selected.</span></div>';
        }
        
        modalOverlay.classList.add('active');
    }
    
    cancelButton.addEventListener('click', () => modalOverlay.classList.remove('active'));
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) modalOverlay.classList.remove('active');
    });
    
    confirmButton.addEventListener('click', function() {
        // Submit Form
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = window.location.href;
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
        
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

    // Progress Bar
    function updateProgressBar() {
        // Calculate progress based on steps completed (visited) or just current step?
        // Let's do current step / total steps
        const progress = ((currentStep + 1) / totalSteps) * 100;
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }

    // Toast Helper
    function showAlert(message, type = 'error') {
        const container = document.querySelector('.toast-container');
        if (!container) { alert(message); return; }

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        const icon = type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle';
        
        toast.innerHTML = `<i class="fas ${icon} toast-icon"></i><span class="toast-message">${message}</span>`;
        container.appendChild(toast);
        
        requestAnimationFrame(() => toast.classList.add('show'));
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    updateNavigationUI();
    updateProgressBar();
});
