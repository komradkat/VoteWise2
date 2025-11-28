from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import uuid
import json

from .models import ChatConversation, ChatMessage
from .services import get_gemini_response, get_mock_response, get_gemini_api_key
from apps.elections.models import Election
from apps.core.logging import logger


def chatbot_view(request):
    """
    Main chatbot interface.
    """
    # Get active elections for selection
    active_elections = Election.objects.filter(is_active=True).order_by('-start_time')
    
    # Get or create session ID for anonymous users
    session_id = request.session.get('chatbot_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['chatbot_session_id'] = session_id
    
    # Get selected election (default to first active)
    election_id = request.GET.get('election_id')
    selected_election = None
    if election_id:
        selected_election = get_object_or_404(Election, id=election_id)
    elif active_elections.exists():
        selected_election = active_elections.first()
    
    # Get or create conversation
    conversation = None
    if request.user.is_authenticated:
        conversation, _ = ChatConversation.objects.get_or_create(
            user=request.user,
            election=selected_election,
            session_id=session_id
        )
    else:
        conversation, _ = ChatConversation.objects.get_or_create(
            session_id=session_id,
            defaults={'election': selected_election}
        )
    
    # Get conversation history
    # messages = conversation.messages.all()
    messages = []
    
    context = {
        'active_elections': active_elections,
        'selected_election': selected_election,
        'conversation': conversation,
        'messages': messages,
        'api_configured': get_gemini_api_key() != 'YOUR_API_KEY_HERE'
    }
    
    return render(request, 'chatbot/chat.html', context)


@require_http_methods(["POST"])
@csrf_exempt  # For now - should use proper CSRF in production
def chat_api(request):
    """
    API endpoint for sending/receiving chat messages.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        election_id = data.get('election_id')
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        if not session_id:
            return JsonResponse({'error': 'Session ID is required'}, status=400)
        
        # Get or create conversation
        conversation = ChatConversation.objects.filter(session_id=session_id).first()
        if not conversation:
            election = None
            if election_id:
                election = Election.objects.filter(id=election_id).first()
            
            conversation = ChatConversation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                election=election
            )
        
        # Save user message - DISABLED for privacy/no-history requirement
        # user_msg = ChatMessage.objects.create(
        #     conversation=conversation,
        #     role='user',
        #     content=user_message
        # )
        
        # Get AI response
        election = conversation.election
        
        # Use mock response if API key not configured
        api_key = get_gemini_api_key()
        if api_key == 'YOUR_API_KEY_HERE':
            result = get_mock_response(user_message, election)
        else:
            result = get_gemini_response(user_message, election)
        
        if result['success']:
            # Save assistant message - DISABLED for privacy/no-history requirement
            # assistant_msg = ChatMessage.objects.create(
            #     conversation=conversation,
            #     role='assistant',
            #     content=result['response'],
            #     response_time_ms=result['response_time_ms']
            # )
            

            
            # Log successful interaction (metadata only)
            user_id = request.user.username if request.user.is_authenticated else "anonymous"
            logger.info(f"Chat interaction successful", user=user_id, category="CHATBOT", extra_data={'response_time_ms': result['response_time_ms'], 'election_id': election_id})
            
            return JsonResponse({
                'success': True,
                'message': result['response'],
                'response_time_ms': result['response_time_ms']
            })
        else:
            logger.error(f"Chatbot error: {result['error']}", category="CHATBOT")
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected chatbot error: {str(e)}", category="CHATBOT")
        return JsonResponse({'error': str(e)}, status=500)


def chat_history(request):
    """
    View conversation history for logged-in users.
    """
    if not request.user.is_authenticated:
        return render(request, 'chatbot/history.html', {'conversations': []})
    
    conversations = ChatConversation.objects.filter(
        user=request.user
    ).prefetch_related('messages').order_by('-last_activity')
    
    return render(request, 'chatbot/history.html', {'conversations': conversations})


@require_http_methods(["POST"])
def flag_message(request, message_id):
    """
    Allow users to flag messages as potentially biased.
    """
    try:
        message = get_object_or_404(ChatMessage, id=message_id)
        message.flagged_as_biased = True
        message.save()
        
        return JsonResponse({'success': True, 'message': 'Message flagged for review'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
