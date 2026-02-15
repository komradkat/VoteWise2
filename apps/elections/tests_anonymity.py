from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import StudentProfile, YearLevel, Course
from apps.elections.models import Election, Position, Candidate, Vote, VoterReceipt

class AnonymityTests(TestCase):
    def setUp(self):
        # Create User and StudentProfile
        self.user = User.objects.create_user(username='voter', password='password')
        self.student = StudentProfile.objects.create(
            user=self.user,
            year_level=YearLevel.FIRST,
            course=Course.BSCS,
            is_eligible_to_vote=True
        )

        # Create Election
        self.election = Election.objects.create(
            name="Test Election",
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            is_active=True
        )

        # Create Position
        self.pos_president = Position.objects.create(name="President", order_on_ballot=1)

        # Create Candidate
        self.cand_user = User.objects.create_user(username='cand1', password='password')
        self.cand_profile = StudentProfile.objects.create(user=self.cand_user, year_level=YearLevel.FIRST, course=Course.BSCS)
        self.candidate = Candidate.objects.create(
            student_profile=self.cand_profile,
            position=self.pos_president,
            election=self.election,
            is_approved=True
        )

        self.client = Client()
        self.client.force_login(self.user)

    def test_vote_anonymity(self):
        """
        Test that the ballot_id stored in Vote records is DIFFERENT from the ballot_id stored in VoterReceipt.
        If they are the same, the vote is not anonymous.
        """
        response = self.client.post(f'/elections/{self.election.id}/vote/', {
            f'vote_{self.pos_president.id}': [self.candidate.id]
        })

        # Check if vote was successful
        self.assertEqual(response.status_code, 302) # Redirects to profile

        # Get the vote and the receipt
        vote = Vote.objects.first()
        receipt = VoterReceipt.objects.first()

        self.assertIsNotNone(vote)
        self.assertIsNotNone(receipt)

        # Assert that the IDs are NOT the same to ensure anonymity
        # If this fails, the system is vulnerable
        self.assertNotEqual(vote.ballot_id, receipt.ballot_id, "Vote anonymity compromised: Vote and Receipt share the same ID!")
