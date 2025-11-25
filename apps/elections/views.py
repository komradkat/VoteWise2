from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Prefetch
from .models import Election, Position, Candidate, Vote, VoterReceipt

def elections_list(request):
    """
    Display all active elections.
    """
    now = timezone.now()
    
    # Get active elections
    active_elections = Election.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    ).order_by('end_time')
    
    # Get upcoming elections
    upcoming_elections = Election.objects.filter(
        is_active=True,
        start_time__gt=now
    ).order_by('start_time')
    
    # Get past elections
    past_elections = Election.objects.filter(
        end_time__lt=now
    ).order_by('-end_time')[:5]  # Show last 5
    
    context = {
        'active_elections': active_elections,
        'upcoming_elections': upcoming_elections,
        'past_elections': past_elections,
    }
    return render(request, 'elections/elections_list.html', context)

@login_required
def vote_view(request, election_id):
    """
    Main voting interface for an election.
    """
    election = get_object_or_404(Election, id=election_id, is_active=True)
    student_profile = getattr(request.user, 'student_profile', None)
    
    # Check if user has a student profile
    if not student_profile:
        messages.error(request, 'You must have a student profile to vote.')
        return redirect('accounts:profile')
    
    # Check if election is currently active (time-based)
    now = timezone.now()
    if now < election.start_time:
        messages.warning(request, 'This election has not started yet.')
        return redirect('home')
    if now > election.end_time:
        messages.warning(request, 'This election has ended.')
        return redirect('home')
    
    # Get all positions for this election with properly filtered candidates
    positions = Position.objects.filter(
        is_active=True,
        candidates__election=election
    ).distinct().prefetch_related(
        Prefetch(
            'candidates',
            queryset=Candidate.objects.filter(
                election=election,
                is_approved=True
            ).select_related('student_profile__user', 'partylist')
        )
    )
    
    # Check if user has already voted in this election
    existing_votes = VoterReceipt.objects.filter(
        voter=student_profile,
        election=election
    )
    
    if existing_votes.exists():
        messages.info(request, 'You have already voted in this election.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Generate a unique ballot ID for this voting session
                import uuid
                ballot_id = uuid.uuid4()
                
                # Process votes for each position
                votes_cast = []
                
                for position in positions:
                    # Get selected candidate(s) for this position
                    vote_key = f'vote_{position.id}'
                    selected_candidates = request.POST.getlist(vote_key)
                    
                    # Validate number of selections
                    if len(selected_candidates) == 0:
                        messages.error(request, f'Please select a candidate for {position.name}.')
                        return redirect('elections:vote', election_id=election_id)
                    
                    if len(selected_candidates) > position.number_of_winners:
                        messages.error(request, f'You can only select {position.number_of_winners} candidate(s) for {position.name}.')
                        return redirect('elections:vote', election_id=election_id)
                    
                    # Create vote records for each selected candidate
                    for candidate_id in selected_candidates:
                        candidate = get_object_or_404(
                            Candidate,
                            id=candidate_id,
                            position=position,
                            election=election,
                            is_approved=True
                        )
                        
                        # Create anonymous vote record
                        vote = Vote.objects.create(
                            election=election,
                            candidate=candidate,
                            position=position,
                            ballot_id=ballot_id
                        )
                        votes_cast.append(vote)
                
                # Create ONE receipt for the entire voting session
                receipt = VoterReceipt.objects.create(
                    voter=student_profile,
                    election=election,
                    ballot_id=ballot_id,
                    encrypted_choices='{}',  # TODO: Implement encryption
                    voter_ip_address=get_client_ip(request)
                )
                
                messages.success(request, f'Your vote has been successfully recorded! You voted for {len(votes_cast)} candidate(s).')
                return redirect('accounts:profile')
                
        except Exception as e:
            messages.error(request, f'An error occurred while processing your vote: {str(e)}')
            return redirect('elections:vote', election_id=election_id)
    
    context = {
        'election': election,
        'positions': positions,
    }
    return render(request, 'elections/vote.html', context)


def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
