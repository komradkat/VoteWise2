function switchTab(tabId, element) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });

    // Show selected tab pane
    document.getElementById(tabId).classList.add('active');

    // Update active nav state
    document.querySelectorAll('.dashboard-nav-item').forEach(item => {
        item.classList.remove('active');
    });
    element.classList.add('active');
}
