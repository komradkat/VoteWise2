from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import StudentProfile, YearLevel, Course
from apps.elections.models import Election, Position, Candidate, Vote
from django.db.utils import IntegrityError

class VotingLogicTests(TestCase):
    def setUp(self):
        # Create User and StudentProfile
        self.user = User.objects.create_user(username='voter', password='password')
        self.student = StudentProfile.objects.create(
            user=self.user,
            year_level=YearLevel.FIRST,
            course=Course.BSCS
        )

        # Create Election
        self.election = Election.objects.create(
            name="Test Election",
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            is_active=True
        )

        # Create Positions
        self.pos_president = Position.objects.create(name="President", order_on_ballot=1)
        self.pos_vp = Position.objects.create(name="Vice President", order_on_ballot=2)

        # Create Candidates
        # We need dummy users for candidates too
        self.cand_user1 = User.objects.create_user(username='cand1', password='password')
        self.cand_profile1 = StudentProfile.objects.create(user=self.cand_user1, year_level=1, course='BSCS')
        self.cand_pres = Candidate.objects.create(
            student_profile=self.cand_profile1,
            position=self.pos_president,
            election=self.election
        )

        self.cand_user2 = User.objects.create_user(username='cand2', password='password')
        self.cand_profile2 = StudentProfile.objects.create(user=self.cand_user2, year_level=1, course='BSCS')
        self.cand_vp = Candidate.objects.create(
            student_profile=self.cand_profile2,
            position=self.pos_vp,
            election=self.election
        )
        
        self.cand_user3 = User.objects.create_user(username='cand3', password='password')
        self.cand_profile3 = StudentProfile.objects.create(user=self.cand_user3, year_level=1, course='BSCS')
        self.cand_pres_2 = Candidate.objects.create(
            student_profile=self.cand_profile3,
            position=self.pos_president, # Another candidate for President
            election=self.election
        )

    def test_can_vote_for_multiple_positions(self):
        """
        Test that a voter can vote for different positions in the same election.
        """
        # Vote for President
        vote1 = Vote.objects.create(
            voter=self.student,
            election=self.election,
            candidate=self.cand_pres
        )
        
        # Vote for Vice President
        vote2 = Vote.objects.create(
            voter=self.student,
            election=self.election,
            candidate=self.cand_vp
        )
        
        self.assertEqual(Vote.objects.count(), 2)
        self.assertEqual(vote1.position, self.pos_president)
        self.assertEqual(vote2.position, self.pos_vp)

    def test_cannot_vote_twice_for_same_position(self):
        """
        Test that a voter cannot vote twice for the same position.
        """
        # Vote for President
        Vote.objects.create(
            voter=self.student,
            election=self.election,
            candidate=self.cand_pres
        )
        
        # Attempt to vote for President again (different candidate)
        with self.assertRaises(IntegrityError):
            Vote.objects.create(
                voter=self.student,
                election=self.election,
                candidate=self.cand_pres_2
            )
