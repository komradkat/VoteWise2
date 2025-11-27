import os
import django
from django.utils import timezone
from datetime import timedelta
import random
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_config.settings')
django.setup()

from apps.elections.models import Election, Position, Candidate, Vote, VoterReceipt
from apps.accounts.models import StudentProfile, Course, YearLevel, Section
from django.contrib.auth.models import User

def create_test_data():
    print("Creating test data for results verification...")
    
    # Create 3 elections
    now = timezone.now()
    
    # 1. Active Election
    e1, _ = Election.objects.get_or_create(
        name="2025 Student Council Election",
        defaults={
            'start_time': now - timedelta(days=1),
            'end_time': now + timedelta(days=1),
            'is_active': True
        }
    )
    
    # 2. Past Election
    e2, _ = Election.objects.get_or_create(
        name="2024 Student Council Election",
        defaults={
            'start_time': now - timedelta(days=365),
            'end_time': now - timedelta(days=364),
            'is_active': False
        }
    )
    
    # 3. Upcoming Election
    e3, _ = Election.objects.get_or_create(
        name="2026 Student Council Election",
        defaults={
            'start_time': now + timedelta(days=365),
            'end_time': now + timedelta(days=366),
            'is_active': True
        }
    )
    
    elections = [e1, e2] # Only add data for active and past
    
    # Create Position
    pos, _ = Position.objects.get_or_create(name="President", defaults={'number_of_winners': 1, 'is_active': True, 'order_on_ballot': 1})
    
    # Create dummy candidates and votes for e1 and e2
    for election in elections:
        print(f"Setting up {election.name}...")
        
        # Candidate 1
        u1, _ = User.objects.get_or_create(username=f"cand_{election.id}_1", defaults={'first_name': 'Alice', 'last_name': 'Candidate'})
        sp1, _ = StudentProfile.objects.get_or_create(user=u1, defaults={'course': Course.BSCS, 'year_level': YearLevel.THIRD})
        
        c1, _ = Candidate.objects.get_or_create(
            election=election, 
            position=pos,
            student_profile=sp1,
            defaults={
                'is_approved': True,
                'biography': 'Platform A'
            }
        )

        # Candidate 2
        u2, _ = User.objects.get_or_create(username=f"cand_{election.id}_2", defaults={'first_name': 'Bob', 'last_name': 'Candidate'})
        sp2, _ = StudentProfile.objects.get_or_create(user=u2, defaults={'course': Course.BSIT, 'year_level': YearLevel.THIRD})

        c2, _ = Candidate.objects.get_or_create(
            election=election, 
            position=pos,
            student_profile=sp2,
            defaults={
                'is_approved': True,
                'biography': 'Platform B'
            }
        )
            
        # Cast some votes
        # Vote for C1
        for i in range(5):
            Vote.objects.create(election=election, position=pos, candidate=c1, ballot_id=uuid.uuid4())
            
        # Vote for C2
        for i in range(3):
            Vote.objects.create(election=election, position=pos, candidate=c2, ballot_id=uuid.uuid4())
            
        # Create Receipts to count total ballots
        for i in range(8):
             # We need a voter for the receipt, but for total count check we might just need count
             # But the model requires a voter. Let's create a dummy one or just skip if too complex
             # The view counts VoterReceipt objects.
             u, _ = User.objects.get_or_create(username=f"voter_{election.id}_{i}")
             sp, _ = StudentProfile.objects.get_or_create(user=u, defaults={'course': Course.BSCS, 'year_level': YearLevel.FIRST})
             VoterReceipt.objects.get_or_create(election=election, voter=sp, defaults={'ballot_id': uuid.uuid4()})

    print("Test data created successfully.")

if __name__ == '__main__':
    create_test_data()
