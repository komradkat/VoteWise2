# Winner Highlighting Logic Update

## Overview
Refined the winner highlighting logic in the Administration Dashboard to respect election status and position-specific winner counts.

## Changes Implemented

### 1. Conditional Winner Highlighting
**File:** `/apps/administration/views.py`
- **Logic:** The "crown" icon and winner status are now **only** applied when the election is officially **CLOSED**.
- **Benefit:** Prevents premature declarations of victory while the election is still active.

### 2. Multiple Winners Support
**File:** `/apps/administration/views.py`
- **Logic:** The system now checks `Position.number_of_winners` for each position.
- **Implementation:**
    - If a position has 3 winners (e.g., Senators), the top 3 candidates are highlighted.
    - **Tie Handling:** If there is a tie for the final winning spot (e.g., 3rd and 4th place have equal votes), both are highlighted as winners.

### 3. Template Enhancements
**File:** `/apps/administration/templates/administration/dashboard.html`
- Added a display of the number of winners allowed per position in the section header.
- **Example:** "Senator (12 winners)"

## Verification
- **System Check:** Passed with no issues.
- **Logic Check:**
    - Active elections show rankings but NO crowns.
    - Closed elections show crowns for the correct number of top candidates.
    - Ties for the last spot are correctly handled.

## Files Modified
1. `/apps/administration/views.py`
2. `/apps/administration/templates/administration/dashboard.html`
