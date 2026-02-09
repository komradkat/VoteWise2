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
    
    // Update URL hash
    const hashMap = {
        'tab-profile': 'my-profile',
        'tab-votes': 'my-votes',
        'tab-notifications': 'notifications',
        'tab-settings': 'settings',
        'tab-security': 'security',
        'tab-help': 'help'
    };
    
    const hash = hashMap[tabId];
    if (hash) {
        // Use pushState to change URL without triggering scroll
        history.pushState(null, null, '#' + hash);
    } else {
        // Remove hash if no mapping
        history.pushState('', document.title, window.location.pathname);
    }
}

// Handle direct linking via hash on page load
document.addEventListener('DOMContentLoaded', function() {
    const hash = window.location.hash.substring(1);
    const tabMap = {
        'my-profile': 'tab-profile',
        'my-votes': 'tab-votes',
        'notifications': 'tab-notifications',
        'settings': 'tab-settings',
        'security': 'tab-security',
        'help': 'tab-help'
    };
    
    if (hash && tabMap[hash]) {
        const tabName = tabMap[hash];
        const navItem = document.querySelector(`[onclick*="'${tabName}'"]`);
        if (navItem) {
            switchTab(tabName, navItem);
        }
    }
});

// Handle hash changes (browser back/forward)
window.addEventListener('hashchange', function() {
    const hash = window.location.hash.substring(1);
    const tabMap = {
        'my-profile': 'tab-profile',
        'my-votes': 'tab-votes',
        'notifications': 'tab-notifications',
        'settings': 'tab-settings',
        'security': 'tab-security',
        'help': 'tab-help'
    };
    
    if (hash && tabMap[hash]) {
        const tabName = tabMap[hash];
        const navItem = document.querySelector(`[onclick*="'${tabName}'"]`);
        if (navItem) {
            switchTab(tabName, navItem);
        }
    } else {
        // No hash or invalid hash, show profile
        const navItem = document.querySelector('[onclick*="tab-profile"]');
        if (navItem) {
            switchTab('tab-profile', navItem);
        }
    }
});
