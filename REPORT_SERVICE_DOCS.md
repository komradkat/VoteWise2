# Election Report Generation Service

## Overview
A new `reports` app has been added to generate comprehensive PDF reports for elections. This service leverages the existing Gemini API integration to provide AI-generated narrative analysis alongside statistical data and visualizations.

## Key Features

### 1. **PDF Report Generation**
- **Library**: Uses `ReportLab` for professional-grade PDF creation.
- **Content**:
  - **Executive Summary**: AI-generated overview of the election.
  - **Turnout Statistics**: Tables showing eligible voters, ballots cast, and turnout percentage.
  - **Visualizations**: Bar charts for each position showing candidate performance.
  - **Detailed Results**: Tables with exact vote counts and percentages.

### 2. **AI Integration**
- **Service**: Uses Google's Gemini API (via `google-generativeai`).
- **Functionality**: Generates a factual, unbiased narrative report based on the election data.
- **Safety**: Includes disclaimers that the narrative is AI-generated.
- **Fallback**: Gracefully handles cases where the API key is missing or the library is not installed.

### 3. **Data Visualization**
- **Library**: Uses `matplotlib` to generate high-quality bar charts.
- **Integration**: Charts are generated in-memory and embedded directly into the PDF.

## Implementation Details

### **New App: `apps.reports`**
- **`utils.py`**: Contains core logic:
  - `get_election_data(election_id)`: Fetches stats from `Vote`, `VoterReceipt`, etc.
  - `generate_charts(election_data)`: Creates matplotlib charts.
  - `generate_narrative_report(election_data)`: Calls Gemini API.
- **`views.py`**: Handles the HTTP request, assembles the PDF using ReportLab components (`SimpleDocTemplate`, `Table`, `Image`, `Paragraph`), and returns the file download.
- **`urls.py`**: Defines the endpoint `election/<id>/pdf/`.

### **Integration**
- **Admin Dashboard**: Added a "Generate Report" button to the election status card in the admin dashboard.
- **Settings**: Registered `apps.reports` in `INSTALLED_APPS`.

## Usage
1. Navigate to the **Admin Dashboard**.
2. Locate the **Current Election** card.
3. Click the **Generate Report** button (PDF icon).
4. The system will generate and download a PDF report named `election_report_<id>.pdf`.

## Dependencies
- `reportlab`: For PDF generation.
- `matplotlib`: For chart generation.
- `google-generativeai`: For AI narrative (optional).
