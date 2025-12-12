#!/usr/bin/env python
"""
Load 2022 Philippine National Election Data

This script safely loads the Philippine election fixture data.
It can either clear existing election data or use different primary keys.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_config.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def clear_election_data():
    """Clear existing election-related data to avoid conflicts."""
    from django.apps import apps
    from elections.models import Vote, VoterReceipt, Candidate, Election, Position, Partylist
    from accounts.models import StudentProfile
    from django.contrib.auth.models import User
    
    print("🗑️  Clearing existing election data...")
    
    # Delete in order of dependencies
    Vote.objects.all().delete()
    VoterReceipt.objects.all().delete()
    Candidate.objects.all().delete()
    Election.objects.all().delete()
    Position.objects.all().delete()
    Partylist.objects.all().delete()
    
    # Only delete student profiles that were created for... this fixture (IDs 101-119)
    StudentProfile.objects.filter(pk__gte=101, pk__lte=119).delete()
    User.objects.filter(pk__gte=101, pk__lte=119).delete()
    
    print("✅ Existing data cleared")

def load_fixture():
    """Load the Philippine election fixture."""
    print("📥 Loading 2022 Philippine National Election data...")
    call_command('loaddata', 'fixtures/philippine_2022_election.json', verbosity=2)
    print("✅ Fixture loaded successfully!")

def show_summary():
    """Display a summary of loaded data."""
    from elections.models import Election, Candidate, Position
    
    election = Election.objects.get(pk=1)
    print(f"\n{'='*60}")
    print(f"📊 {election.name}")
    print(f"{'='*60}")
    
    for position in Position.objects.all().order_by('order_on_ballot'):
        candidates = Candidate.objects.filter(election=election, position=position)
        print(f"\n🏛️  {position.name} ({candidates.count()} candidates):")
        for candidate in candidates:
            party = f" ({candidate.partylist.short_code})" if candidate.partylist else ""
            print(f"   • {candidate.student_profile.user.get_full_name()}{party}")
    
    print(f"\n{'='*60}")
    print(f"Total Candidates: {Candidate.objects.filter(election=election).count()}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Load 2022 Philippine election data')
    parser.add_argument('--clear', action='store_true', 
                       help='Clear existing election data before loading')
    parser.add_argument('--no-clear', action='store_true',
                       help='Skip clearing (will fail if data exists)')
    
    args = parser.parse_args()
    
    try:
        if args.no_clear:
            print("⚠️  Skipping data clear (may fail if conflicts exist)")
        elif args.clear or input("Clear existing election data? (y/N): ").lower() == 'y':
            clear_election_data()
        
        load_fixture()
        show_summary()
        
        print("✨ Success! You can now view the candidates in Django admin or the app.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
