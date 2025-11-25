/**
 * Admin Lists JavaScript
 * Handles search and filtering for administration list views.
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const filterSelects = document.querySelectorAll('.filter-select');
    const tableRows = document.querySelectorAll('.data-row');
    const noResults = document.getElementById('noResults');
    const emptyState = document.getElementById('emptyState');

    if (!searchInput && filterSelects.length === 0) return;

    function filterTable() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        let visibleCount = 0;

        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            let matchesFilters = true;

            // Check all dropdown filters
            filterSelects.forEach(select => {
                const filterType = select.dataset.filter; // e.g., 'election', 'status'
                const filterValue = select.value;
                const rowValue = row.dataset[filterType];

                if (filterValue && rowValue !== filterValue) {
                    matchesFilters = false;
                }
            });

            const matchesSearch = text.includes(searchTerm);

            if (matchesSearch && matchesFilters) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Show "No Results" if rows exist but all are filtered out
        // Only show if we actually have rows (not the empty state)
        if (tableRows.length > 0) {
            if (noResults) {
                noResults.style.display = visibleCount === 0 ? '' : 'none';
            }
        }
    }

    if (searchInput) {
        searchInput.addEventListener('keyup', filterTable);
    }

    filterSelects.forEach(select => {
        select.addEventListener('change', filterTable);
    });
});
