from django.test import TransactionTestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import connection, transaction
from datetime import timedelta
import concurrent.futures
import threading
import uuid

from apps.accounts.models import StudentProfile, YearLevel, Course, Section
from apps.elections.models import Election, Position, Candidate, Partylist, Vote, VoterReceipt
from apps.elections.views import vote_view

class ConcurrentVotingLoadTests(TransactionTestCase):
    """
    Simulates high concurrency voting to ensure race conditions 
    are handled correctly by the database and view logic.
    Using TransactionTestCase to allow persistence of threads' DB operations.
    """
    
    def setUp(self):
        self.factory = RequestFactory()
        
        # 1. Setup Election
        self.election = Election.objects.create(
            name="Load Test Election",
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=24),
            is_active=True
        )
        
        # 2. Setup Positions & Candidates
        self.pos_president = Position.objects.create(name="President", order_on_ballot=1, number_of_winners=1)
        self.party = Partylist.objects.create(name="Test Party", short_code="TP")
        
        # Create a candidate profile first
        self.cand_user = User.objects.create_user(username='candidate1', password='password')
        self.cand_profile = StudentProfile.objects.create(
            user=self.cand_user,
            student_id="CAND-001",
            year_level=YearLevel.FOURTH,
            course=Course.BSCS,
            is_eligible_to_vote=True
        )
        
        self.candidate = Candidate.objects.create(
            student_profile=self.cand_profile,
            position=self.pos_president,
            election=self.election,
            partylist=self.party,
            is_approved=True
        )
        
        # 3. Pre-create Voters
        # Adjust count based on DB capacity
        db_engine = connection.settings_dict['ENGINE']
        if 'sqlite' in db_engine:
            self.TOTAL_VOTERS = 10
        else:
            self.TOTAL_VOTERS = 50
            
        self.voters = []
        self.voter_profiles = []
        for i in range(self.TOTAL_VOTERS):
            user = User.objects.create_user(username=f'voter{i}', password='password')
            profile = StudentProfile.objects.create(
                user=user,
                student_id=f"VOTER-{i:03d}",
                year_level=YearLevel.FIRST,
                course=Course.BSIT,
                is_eligible_to_vote=True
            )
            self.voters.append(user)
            self.voter_profiles.append(profile)

    def test_concurrent_voting_success(self):
        """
        Simulate 50 users voting at the "same time".
        Verify all votes are recorded and no race conditions cause errors.
        """
        success_count = 0
        failure_count = 0
        errors = []

        def cast_vote(user):
            # Each thread needs to close old connections to avoid "database is locked" in SQLite
            # though TransactionTestCase handles some of this, explicit hygiene helps in threads
            connection.close()
            
            nonlocal success_count, failure_count
            try:
                # Prepare a POST request
                data = {
                    f'vote_{self.pos_president.id}': [str(self.candidate.id)]
                }
                
                request = self.factory.post(
                    f'/elections/vote/{self.election.id}/',
                    data=data
                )
                request.user = user
                
                # Mock messages framework
                from django.contrib.messages.storage.fallback import FallbackStorage
                setattr(request, 'session', 'session')
                setattr(request, '_messages', FallbackStorage(request))
                
                # Call the view directly
                response = vote_view(request, self.election.id)
                
                if response.status_code == 302: # Redirect usually means success or invalid form
                     success_count += 1
                else:
                     failure_count += 1
                     errors.append(f"Status {response.status_code}")
                     
            except Exception as e:
                failure_count += 1
                errors.append(str(e))
            finally:
                connection.close()

        # Determine safe concurrency level based on DB
        if 'sqlite' in db_engine:
            print("\n[Admin] SQLite detected: Skipping high-concurrency test as it does not support row-locking.")
            self.skipTest("SQLite cannot handle concurrent writes required for this test. Run with PostgreSQL.")
        else:
            # Postgres/MySQL can handle real load
            MAX_WORKERS = 50
            print(f"\n[Admin] Detected Production DB ({db_engine}): using 50 threads.")

        # Run concurrent threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(cast_vote, user) for user in self.voters]
            concurrent.futures.wait(futures)
            
        # Assertions
        print(f"\nResults: Success={success_count}, Failures={failure_count}")
        if errors:
            print(f"Sample Errors: {errors[:3]}")
            
        self.assertEqual(success_count, self.TOTAL_VOTERS, f"All {self.TOTAL_VOTERS} voters should successfully cast votes")
        
        # Verify DB Counts
        self.assertEqual(Vote.objects.count(), self.TOTAL_VOTERS)
        self.assertEqual(VoterReceipt.objects.count(), self.TOTAL_VOTERS)
        self.assertEqual(self.candidate.received_votes.count(), self.TOTAL_VOTERS)

    def test_double_voting_prevention(self):
        """
        Simulate the SAME user trying to vote twice in parallel. 
        Only one should succeed.
        """
        same_user = self.voters[0]
        results = []
        
        def try_vote():
            connection.close()
            try:
                data = {f'vote_{self.pos_president.id}': [str(self.candidate.id)]}
                request = self.factory.post(f'/elections/vote/{self.election.id}/', data=data)
                request.user = same_user
                from django.contrib.messages.storage.fallback import FallbackStorage
                setattr(request, 'session', 'session')
                setattr(request, '_messages', FallbackStorage(request))
                
                response = vote_view(request, self.election.id)
                # Success redirect vs "Already voted" redirect. 
                # We check the actual DB receipt creation to confirm only 1 happened.
                return "OK"
            except Exception as e:
                return str(e)
            finally:
                connection.close()

        # Launch 5 concurrent attempts for the SAME user
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(try_vote) for _ in range(5)]
            concurrent.futures.wait(futures)
        
        # Check DB State
        receipt_count = VoterReceipt.objects.filter(voter=same_user.student_profile, election=self.election).count()
        self.assertEqual(receipt_count, 1, "User should only have 1 receipt even with concurrent requests")
