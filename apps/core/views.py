from django.shortcuts import render

# Create your views here.
from apps.elections.models import Election, Position, Candidate, Vote, VoterReceipt
from django.db.models import Count

def home(request):
    return render(request, 'core/home.html')

def results(request):
    # Get all elections for dropdown
    all_elections = Election.objects.all().order_by('-start_time')
    
    # Determine which election to show
    election_id = request.GET.get('election_id')
    election = None
    
    if election_id:
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            pass
            
    if not election:
        # Default to active election or most recent one
        election = Election.objects.filter(is_active=True).first()
        if not election:
            election = Election.objects.order_by('-end_time').first()
    
    context = {
        'election': election,
        'all_elections': all_elections,
        'selected_election_id': election.id if election else None,
        'total_ballots': 0,
        'positions_data': []
    }
    
    if election:
        # Count total ballots (voters who participated)
        context['total_ballots'] = VoterReceipt.objects.filter(election=election).count()
        
        # Get all positions
        positions = Position.objects.filter(is_active=True).order_by('order_on_ballot')
        
        for pos in positions:
            # Get candidates for this position in this election
            candidates = Candidate.objects.filter(election=election, position=pos)
            
            # Skip positions with no candidates
            if not candidates.exists():
                continue
                
            candidates_data = []
            # Calculate total votes for this specific position to compute percentages
            pos_total_votes = Vote.objects.filter(election=election, position=pos).count()
            
            for cand in candidates:
                votes = Vote.objects.filter(election=election, candidate=cand).count()
                percentage = (votes / pos_total_votes * 100) if pos_total_votes > 0 else 0
                
                candidates_data.append({
                    'object': cand,
                    'name': cand.student_profile.user.get_full_name(),
                    'photo_url': cand.get_photo_url,
                    'votes': votes,
                    'percentage': round(percentage, 1),
                    'partylist': cand.partylist.short_code if cand.partylist else "Independent"
                })
            
            # Sort candidates by votes descending
            candidates_data.sort(key=lambda x: x['votes'], reverse=True)
            
            context['positions_data'].append({
                'name': pos.name,
                'candidates': candidates_data,
                'total_votes': pos_total_votes
            })
            
    return render(request, 'core/election-results.html', context)

def terms(request):
    return render(request, 'pages/terms.html')

def privacy(request):
    return render(request, 'pages/privacy.html')

def about(request):
    return render(request, 'pages/about.html')

def voter_guide(request):
    return render(request, 'pages/voter_guide.html')

def faq(request):
    return render(request, 'pages/faq.html')

def candidate_portal(request):
    return render(request, 'pages/candidate_portal.html')

def election_rules(request):
    return render(request, 'pages/election_rules.html')

def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns JSON response with application status.
    """
    from django.http import JsonResponse
    from django.db import connection
    
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'application': 'running'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)