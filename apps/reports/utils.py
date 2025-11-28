import io
import base64
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.db.models import Count
from apps.elections.models import Election, Vote, VoterReceipt, Candidate, Position
from apps.accounts.models import StudentProfile
from apps.chatbot.services import get_gemini_api_key, GEMINI_AVAILABLE
try:
    import google.generativeai as genai
except ImportError:
    genai = None
from django.utils import timezone

def get_election_data(election_id):
    """
    Fetches comprehensive data for a specific election.
    """
    try:
        election = Election.objects.get(pk=election_id)
    except Election.DoesNotExist:
        return None

    # Turnout Stats
    eligible_voters = StudentProfile.objects.filter(is_eligible_to_vote=True).count()
    ballots_cast = VoterReceipt.objects.filter(election=election).count()
    turnout_percentage = (ballots_cast / eligible_voters * 100) if eligible_voters > 0 else 0

    # Results per position
    positions = Position.objects.filter(is_active=True).order_by('order_on_ballot')
    results = {}
    
    for position in positions:
        candidates = Candidate.objects.filter(election=election, position=position)
        if not candidates.exists():
            continue
            
        candidate_votes = []
        for candidate in candidates:
            votes = Vote.objects.filter(election=election, candidate=candidate).count()
            candidate_votes.append({
                'name': candidate.student_profile.user.get_full_name(),
                'votes': votes,
                'party': candidate.partylist.short_code if candidate.partylist else 'Independent',
                'percentage': (votes / ballots_cast * 100) if ballots_cast > 0 else 0
            })
        
        # Sort by votes desc
        candidate_votes.sort(key=lambda x: x['votes'], reverse=True)
        results[position.name] = candidate_votes

    return {
        'election': election,
        'eligible_voters': eligible_voters,
        'ballots_cast': ballots_cast,
        'turnout_percentage': round(turnout_percentage, 2),
        'results': results
    }

def generate_charts(election_data):
    """
    Generates bar charts for each position using matplotlib (OO interface).
    Returns a dictionary of {position_name: base64_image_string}.
    """
    charts = {}
    results = election_data['results']
    
    for position, candidates in results.items():
        if not candidates:
            continue
            
        try:
            names = [c['name'] for c in candidates]
            votes = [c['votes'] for c in candidates]
            
            # Create figure using OO interface (no pyplot)
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvasAgg(fig)
            ax = fig.add_subplot(111)
            
            # Plot
            bars = ax.bar(names, votes, color='#2563eb')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            ax.set_title(f'Results for {position}', fontsize=14, pad=20)
            ax.set_ylabel('Votes Cast')
            ax.set_xlabel('Candidates')
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)
            
            # Rotate x-axis labels if many candidates
            if len(names) > 3:
                fig.autofmt_xdate(rotation=45)
                
            fig.tight_layout()
            
            # Save to buffer
            buffer = io.BytesIO()
            canvas.print_png(buffer)
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            
            # Encode
            graphic = base64.b64encode(image_png).decode('utf-8')
            charts[position] = graphic
            
        except Exception as e:
            print(f"Error generating chart for {position}: {e}")
            # Continue without this chart
            continue
        
    return charts

def generate_narrative_report(election_data):
    """
    Uses Gemini API to generate a factual, unbiased narrative report.
    """
    if not GEMINI_AVAILABLE:
        return "AI Narrative generation unavailable: Google Generative AI library not installed."
        
    api_key = get_gemini_api_key()
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        return "AI Narrative generation unavailable: API Key not configured."
        
    election = election_data['election']
    results = election_data['results']
    
    # Build data string for the prompt
    data_summary = f"""
    ELECTION: {election.name}
    STATUS: {election.status}
    TURNOUT: {election_data['ballots_cast']} out of {election_data['eligible_voters']} eligible voters ({election_data['turnout_percentage']}%)
    
    RESULTS BY POSITION:
    """
    
    for position, candidates in results.items():
        data_summary += f"\nPOSITION: {position}\n"
        for i, c in enumerate(candidates, 1):
            data_summary += f"{i}. {c['name']} ({c['party']}): {c['votes']} votes ({c['percentage']:.1f}%)\n"
            
    # Construct the prompt
    prompt = f"""
    You are an impartial election analyst for VoteWise. Write a formal, factual, and unbiased narrative report for the election described below.
    
    DATA:
    {data_summary}
    
    INSTRUCTIONS:
    1. Start with an "Executive Summary" section summarizing the overall turnout and key outcomes.
    2. Provide a "Results Analysis" section breaking down the results by position. Highlight the winners and the margins of victory. Mention if races were close or decisive.
    3. Include a "Conclusion" section wrapping up the report.
    4. TONE: Professional, objective, data-driven. Avoid emotional language or bias.
    5. FORMAT: Use Markdown formatting (headers, bullet points).
    6. DISCLAIMER: You MUST begin the report with the following exact disclaimer in bold: "**DISCLAIMER: This narrative report was generated by AI based on the official election data provided.**"
    
    Do not include any information not present in the data provided.
    """
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating narrative: {str(e)}"
