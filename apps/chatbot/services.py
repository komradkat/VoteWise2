"""
Service layer for Gemini AI integration.
Handles API calls and context building for unbiased candidate information.
"""
import time
from typing import Dict, List, Optional
from django.conf import settings
from apps.elections.models import Election, Candidate

# Placeholder for Gemini API - will be replaced when user provides API key
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# System prompt for bias mitigation
SYSTEM_PROMPT = """You are an impartial election information assistant for VoteWise, a student voting system. 
Your role is to provide factual, unbiased information about candidates based solely on their official 
platforms and qualifications.

CRITICAL RULES:
1. NEVER express preference for any candidate
2. Present ALL candidates' information equally and fairly
3. Stick ONLY to factual information from candidate profiles
4. If asked for recommendations or "who to vote for", politely decline and encourage informed decision-making
5. Cite specific candidate statements when possible
6. If you don't have information about something, say so clearly
7. Maintain a neutral, professional tone at all times

You will be provided with candidate information in the following format:
- Name, Position, Partylist, and Biography/Platform

Answer user questions based on this information while maintaining complete neutrality."""


def get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key from settings."""
    return getattr(settings, 'GEMINI_API_KEY', 'YOUR_API_KEY_HERE')


def build_candidate_context(election: Election) -> str:
    """
    Build context string with candidate information for the AI.
    
    Args:
        election: Election object to get candidates from
        
    Returns:
        Formatted string with candidate information
    """
    candidates = Candidate.objects.filter(
        election=election,
        is_approved=True
    ).select_related('student_profile__user', 'position', 'partylist')
    
    if not candidates.exists():
        return "No approved candidates found for this election."
    
    context = f"Election: {election.name}\n\n"
    context += "CANDIDATES:\n\n"
    
    # Group by position for better organization
    positions = {}
    for candidate in candidates:
        pos_name = candidate.position.name
        if pos_name not in positions:
            positions[pos_name] = []
        positions[pos_name].append(candidate)
    
    for position_name, position_candidates in positions.items():
        context += f"=== {position_name} ===\n\n"
        for candidate in position_candidates:
            user = candidate.student_profile.user
            context += f"Candidate: {user.get_full_name()}\n"
            context += f"Position: {candidate.position.name}\n"
            
            if candidate.partylist:
                context += f"Partylist: {candidate.partylist.name} ({candidate.partylist.short_code})\n"
                context += f"Partylist Platform: {candidate.partylist.platform}\n"
            else:
                context += "Partylist: Independent\n"
            
            context += f"Biography/Platform: {candidate.biography or 'No platform statement provided.'}\n"
            context += "\n"
        
        context += "\n"
    
    return context


def get_gemini_response(user_message: str, election: Optional[Election] = None) -> Dict[str, any]:
    """
    Get response from Gemini AI with candidate context.
    
    Args:
        user_message: User's question
        election: Optional election for context
        
    Returns:
        Dictionary with 'response', 'success', and 'error' keys
    """
    start_time = time.time()
    
    # Check if Gemini is available
    if not GEMINI_AVAILABLE:
        return {
            'success': False,
            'response': None,
            'error': 'Gemini AI library not installed. Please install google-generativeai package.',
            'response_time_ms': 0
        }
    
    # Check API key
    api_key = get_gemini_api_key()
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        return {
            'success': False,
            'response': None,
            'error': 'Gemini API key not configured. Please add GEMINI_API_KEY to your settings.',
            'response_time_ms': 0
        }
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Build context
        context = ""
        if election:
            context = build_candidate_context(election)
        
        # Create full prompt
        full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nUser Question: {user_message}\n\nAssistant:"
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'response': response.text,
            'error': None,
            'response_time_ms': response_time_ms
        }
        
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return {
            'success': False,
            'response': None,
            'error': f'Error calling Gemini API: {str(e)}',
            'response_time_ms': response_time_ms
        }


def get_mock_response(user_message: str, election: Optional[Election] = None) -> Dict[str, any]:
    """
    Mock response for testing when API key is not available.
    
    Args:
        user_message: User's question
        election: Optional election for context
        
    Returns:
        Dictionary with mock response
    """
    context = ""
    if election:
        context = build_candidate_context(election)
    
    mock_response = f"""[MOCK RESPONSE - Gemini API not configured]

I would help you with information about the candidates, but the Gemini API key is not yet configured.

Your question: "{user_message}"

Available candidate information:
{context}

To enable the AI chatbot, please:
1. Get a Gemini API key from https://makersuite.google.com/app/apikey
2. Add it to your Django settings as GEMINI_API_KEY
3. Install the package: pip install google-generativeai
"""
    
    return {
        'success': True,
        'response': mock_response,
        'error': None,
        'response_time_ms': 100
    }
