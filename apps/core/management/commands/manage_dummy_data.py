import random
import uuid
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from apps.accounts.models import StudentProfile, ElectionAdmin, YearLevel, Course, Section, AdminType
from apps.elections.models import Election, Position, Partylist, Candidate, Vote, VoterReceipt, ElectionTimeline
from apps.administration.models import AuditLog
from apps.core.models import SystemSettings

class Command(BaseCommand):
    help = 'Populate or clear dummy data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            help='Action to perform: "populate" or "clear"',
            required=True,
            choices=['populate', 'clear']
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'clear':
            self.clear_data()
        elif action == 'populate':
            self.populate_data()

    def clear_data(self):
        self.stdout.write('Clearing dummy data...')
        
        with transaction.atomic():
            # Delete in order of dependencies to avoid protection errors
            # Though cascading deletes might handle some, explicit is safer for clarity
            Vote.objects.all().delete()
            VoterReceipt.objects.all().delete()
            Candidate.objects.all().delete()
            Partylist.objects.all().delete()
            
            # Delete votes first before positions/elections if on_delete=PROTECT
            # But we just deleted Votes above.
            
            Position.objects.all().delete()
            Election.objects.all().delete()
            
            AuditLog.objects.all().delete()
            SystemSettings.objects.all().delete()
            
            # Delete profiles
            StudentProfile.objects.all().delete()
            ElectionAdmin.objects.all().delete()
            
            # Delete non-superuser users
            count, _ = User.objects.filter(is_superuser=False).delete()
            
        self.stdout.write(self.style.SUCCESS(f'Successfully cleared data. Deleted {count} users and related records.'))

    def populate_data(self):
        self.stdout.write('Populating dummy data...')
        
        with transaction.atomic():
            # 1. Create Positions
            positions_data = [
                {'name': 'President', 'order': 1, 'winners': 1},
                {'name': 'Vice President', 'order': 2, 'winners': 1},
                {'name': 'Secretary', 'order': 3, 'winners': 1},
                {'name': 'Treasurer', 'order': 4, 'winners': 1},
                {'name': 'Auditor', 'order': 5, 'winners': 1},
                {'name': 'Senator', 'order': 6, 'winners': 6},
            ]
            positions = {}
            for p in positions_data:
                pos, created = Position.objects.get_or_create(
                    name=p['name'],
                    defaults={'order_on_ballot': p['order'], 'number_of_winners': p['winners']}
                )
                positions[p['name']] = pos
            self.stdout.write(f'Created {len(positions)} positions.')

            # 2. Create Partylists
            partylists_data = [
                {'name': 'Visionary Alliance', 'code': 'VISA', 'platform': 'Innovation and Progress'},
                {'name': 'United Student Action', 'code': 'USA', 'platform': 'Unity and Service'},
            ]
            partylists = []
            for pl in partylists_data:
                p, _ = Partylist.objects.get_or_create(
                    name=pl['name'],
                    defaults={'short_code': pl['code'], 'platform': pl['platform']}
                )
                partylists.append(p)
            self.stdout.write(f'Created {len(partylists)} partylists.')

            # 3. Create Elections
            # Active Election
            active_election = Election.objects.create(
                name=f"Student Council Election {timezone.now().year}",
                start_time=timezone.now() - timedelta(days=1),
                end_time=timezone.now() + timedelta(days=2),
                is_active=True
            )
            
            # Create Timeline Events for Active Election
            timeline_events = [
                {
                    'title': 'Filing of Candidacy',
                    'start_time': active_election.start_time - timedelta(days=14),
                    'end_time': active_election.start_time - timedelta(days=7),
                    'description': 'Period for students to file their certificates of candidacy.',
                    'order': 1
                },
                {
                    'title': 'Campaign Period',
                    'start_time': active_election.start_time - timedelta(days=6),
                    'end_time': active_election.start_time - timedelta(days=1),
                    'description': 'Official campaign period for approved candidates.',
                    'order': 2
                },
                {
                    'title': 'Voting Period',
                    'start_time': active_election.start_time,
                    'end_time': active_election.end_time,
                    'description': 'Election day voting.',
                    'order': 3
                }
            ]
            
            for event in timeline_events:
                ElectionTimeline.objects.create(
                    election=active_election,
                    title=event['title'],
                    start_time=event['start_time'],
                    end_time=event['end_time'],
                    description=event['description'],
                    order=event['order']
                )
            
            # Past Election
            Election.objects.create(
                name=f"Student Council Election {timezone.now().year - 1}",
                start_time=timezone.now() - timedelta(days=365),
                end_time=timezone.now() - timedelta(days=364),
                is_active=False
            )
            self.stdout.write('Created 2 elections (1 Active with Timeline, 1 Past).')

            # 4. Create Users & Students
            first_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles', 'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
            
            students = []
            for i in range(50):
                first = random.choice(first_names)
                last = random.choice(last_names)
                username = f"{first.lower()}{last.lower()}{i}"
                student_id = f"2025-{1000+i}"
                
                user = User.objects.create_user(username=username, password='password123', first_name=first, last_name=last, email=f"{username}@example.com")
                
                profile = StudentProfile.objects.create(
                    user=user,
                    student_id=student_id,
                    year_level=random.choice(YearLevel.values),
                    course=random.choice(Course.values),
                    section=random.choice(Section.values),
                    is_eligible_to_vote=True
                )
                students.append(profile)
            
            self.stdout.write(f'Created {len(students)} student users.')

            # 5. Create Admins
            admin_users_data = [
                {'username': 'admin_staff', 'first': 'Admin', 'last': 'Staff', 'type': AdminType.EMPLOYEE, 'emp_id': 'EMP-001'},
                {'username': 'admin_instructor', 'first': 'Prof', 'last': 'Garcia', 'type': AdminType.INSTRUCTOR, 'emp_id': 'INS-001'},
                {'username': 'admin_student', 'first': 'Student', 'last': 'Leader', 'type': AdminType.STUDENT, 'emp_id': None},
            ]
            
            for admin_data in admin_users_data:
                admin_user = User.objects.create_user(
                    username=admin_data['username'],
                    password='password123',
                    first_name=admin_data['first'],
                    last_name=admin_data['last'],
                    email=f"{admin_data['username']}@example.com",
                    is_staff=True
                )
                ElectionAdmin.objects.create(
                    user=admin_user,
                    admin_type=admin_data['type'],
                    employee_id=admin_data['emp_id'],
                    is_active=True
                )
            
            self.stdout.write(f'Created {len(admin_users_data)} Election Admins (all with password: password123).')


            # 6. Create Candidates for Active Election
            # Pick 2 candidates per position (except Senator, pick 10)
            candidates_pool = students[:20] # First 20 students are candidates
            remaining_students = students[20:] # Rest are voters
            
            cand_idx = 0
            
            # President
            for pl in partylists:
                if cand_idx < len(candidates_pool):
                    Candidate.objects.create(
                        student_profile=candidates_pool[cand_idx],
                        position=positions['President'],
                        election=active_election,
                        partylist=pl,
                        is_approved=True,
                        biography="I will serve with integrity."
                    )
                    cand_idx += 1
            
            # VP
            for pl in partylists:
                if cand_idx < len(candidates_pool):
                    Candidate.objects.create(
                        student_profile=candidates_pool[cand_idx],
                        position=positions['Vice President'],
                        election=active_election,
                        partylist=pl,
                        is_approved=True,
                        biography="Vote for progress."
                    )
                    cand_idx += 1
            
            # Secretary
            for pl in partylists:
                if cand_idx < len(candidates_pool):
                    Candidate.objects.create(
                        student_profile=candidates_pool[cand_idx],
                        position=positions['Secretary'],
                        election=active_election,
                        partylist=pl,
                        is_approved=True,
                        biography="Organized and reliable."
                    )
                    cand_idx += 1
            
            # Treasurer
            for pl in partylists:
                if cand_idx < len(candidates_pool):
                    Candidate.objects.create(
                        student_profile=candidates_pool[cand_idx],
                        position=positions['Treasurer'],
                        election=active_election,
                        partylist=pl,
                        is_approved=True,
                        biography="Responsible with finances."
                    )
                    cand_idx += 1
            
            # Auditor
            for pl in partylists:
                if cand_idx < len(candidates_pool):
                    Candidate.objects.create(
                        student_profile=candidates_pool[cand_idx],
                        position=positions['Auditor'],
                        election=active_election,
                        partylist=pl,
                        is_approved=True,
                        biography="Ensuring transparency."
                    )
                    cand_idx += 1
            
            # Senators (Random mix)
            for _ in range(8):
                if cand_idx < len(candidates_pool):
                    Candidate.objects.create(
                        student_profile=candidates_pool[cand_idx],
                        position=positions['Senator'],
                        election=active_election,
                        partylist=random.choice(partylists),
                        is_approved=True,
                        biography="Voice of the students."
                    )
                    cand_idx += 1
            
            self.stdout.write('Registered candidates for the active election.')

            # 7. Simulate Voting
            # Have 20 students cast votes
            all_candidates = list(Candidate.objects.filter(election=active_election))
            
            for voter in remaining_students[:20]:
                # Pick 1 for each position: President, VP, Secretary, Treasurer, Auditor, and 3 Senators
                choices = []
                
                # President
                pres_cands = [c for c in all_candidates if c.position.name == 'President']
                if pres_cands:
                    choices.append(random.choice(pres_cands))
                
                # VP
                vp_cands = [c for c in all_candidates if c.position.name == 'Vice President']
                if vp_cands:
                    choices.append(random.choice(vp_cands))
                
                # Secretary
                sec_cands = [c for c in all_candidates if c.position.name == 'Secretary']
                if sec_cands:
                    choices.append(random.choice(sec_cands))
                
                # Treasurer
                treas_cands = [c for c in all_candidates if c.position.name == 'Treasurer']
                if treas_cands:
                    choices.append(random.choice(treas_cands))
                
                # Auditor
                aud_cands = [c for c in all_candidates if c.position.name == 'Auditor']
                if aud_cands:
                    choices.append(random.choice(aud_cands))
                
                # Senators
                sen_cands = [c for c in all_candidates if c.position.name == 'Senator']
                if len(sen_cands) >= 3:
                    choices.extend(random.sample(sen_cands, 3))
                
                # Cast Votes
                for choice in choices:
                    Vote.objects.create(
                        election=active_election,
                        candidate=choice,
                        position=choice.position,
                        ballot_id=uuid.uuid4() # Just for linking if needed
                    )
                
                # Create Receipt
                VoterReceipt.objects.create(
                    voter=voter,
                    election=active_election,
                    ballot_id=uuid.uuid4(),
                    encrypted_choices=f"Encrypted data for {len(choices)} votes"
                )
                
            self.stdout.write('Simulated voting for 20 students.')
            
            # 8. Create Audit Logs
            admin_user = User.objects.get(username='admin_staff')
            audit_actions = [
                {'action': 'ELECTION_CREATED', 'details': f'Created election: {active_election.name}'},
                {'action': 'CANDIDATE_APPROVED', 'details': 'Approved multiple candidates for election'},
                {'action': 'VOTER_VERIFIED', 'details': 'Verified student voter registrations'},
                {'action': 'SYSTEM_LOGIN', 'details': 'Admin logged into system'},
                {'action': 'SETTINGS_UPDATED', 'details': 'Updated system settings'},
            ]
            
            for i, audit_data in enumerate(audit_actions):
                AuditLog.objects.create(
                    user=admin_user if i % 2 == 0 else None,  # Some system actions
                    action=audit_data['action'],
                    details=audit_data['details'],
                    ip_address='127.0.0.1' if i % 2 == 0 else None
                )
            
            self.stdout.write(f'Created {len(audit_actions)} audit log entries.')

            # 9. Create System Settings
            SystemSettings.objects.get_or_create(
                school_name="ACLC College of Tacloban",
                defaults={
                    'allow_registration': True,
                    'maintenance_mode': False
                }
            )
            self.stdout.write('Initialized System Settings.')
            
        self.stdout.write(self.style.SUCCESS('Dummy data population complete!'))
