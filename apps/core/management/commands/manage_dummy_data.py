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
                {'name': 'Future Leaders', 'code': 'FUT', 'platform': 'Empowering Tomorrow'},
            ]
            partylists = []
            for pl in partylists_data:
                p, _ = Partylist.objects.get_or_create(
                    name=pl['name'],
                    defaults={'short_code': pl['code'], 'platform': pl['platform']}
                )
                partylists.append(p)
            self.stdout.write(f'Created {len(partylists)} partylists.')

            # 3. Create Elections (3 Active, 1 Past)
            active_elections = []
            
            # Active 1: Main Student Council
            e1 = Election.objects.create(
                name=f"Student Council Election {timezone.now().year}",
                start_time=timezone.now() - timedelta(days=1),
                end_time=timezone.now() + timedelta(days=2),
                is_active=True
            )
            active_elections.append(e1)
            
            # Active 2: Special Election
            e2 = Election.objects.create(
                name=f"Special Election {timezone.now().year}",
                start_time=timezone.now() - timedelta(hours=12),
                end_time=timezone.now() + timedelta(days=5),
                is_active=True
            )
            active_elections.append(e2)
            
            # Active 3: Club Officers
            e3 = Election.objects.create(
                name=f"Club Officers Election {timezone.now().year}",
                start_time=timezone.now() - timedelta(days=2),
                end_time=timezone.now() + timedelta(days=1),
                is_active=True
            )
            active_elections.append(e3)

            # Create Timeline Events for Main Election
            timeline_events = [
                {
                    'title': 'Filing of Candidacy',
                    'start_time': e1.start_time - timedelta(days=14),
                    'end_time': e1.start_time - timedelta(days=7),
                    'description': 'Period for students to file their certificates of candidacy.',
                    'order': 1
                },
                {
                    'title': 'Campaign Period',
                    'start_time': e1.start_time - timedelta(days=6),
                    'end_time': e1.start_time - timedelta(days=1),
                    'description': 'Official campaign period for approved candidates.',
                    'order': 2
                },
                {
                    'title': 'Voting Period',
                    'start_time': e1.start_time,
                    'end_time': e1.end_time,
                    'description': 'Election day voting.',
                    'order': 3
                }
            ]
            
            for event in timeline_events:
                ElectionTimeline.objects.create(
                    election=e1,
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
            self.stdout.write('Created 4 elections (3 Active, 1 Past).')

            # 4. Create Users & Students (100 voters)
            first_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles', 'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen', 'Lisa', 'Nancy', 'Betty', 'Helen', 'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson']
            
            students = []
            for i in range(100):
                first = random.choice(first_names)
                last = random.choice(last_names)
                username = f"{first.lower()}{last.lower()}{i}"
                student_id = f"2025-{1000+i}"
                
                # Ensure unique username
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{i}"
                
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
                if not User.objects.filter(username=admin_data['username']).exists():
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
            
            self.stdout.write(f'Created Election Admins (all with password: password123).')


            # 6. Create Candidates for Active Elections
            # We need at least 20 candidates total. Let's distribute them.
            # E1: 20 candidates (Full slate)
            # E2: 10 candidates
            # E3: 10 candidates
            
            candidates_pool = students[:50] # Use first 50 students as candidate pool
            remaining_students = students[50:] # Rest are voters
            
            cand_idx = 0
            
            for election in active_elections:
                self.stdout.write(f'Registering candidates for {election.name}...')
                
                # For each position, register candidates
                # President (2 candidates)
                for _ in range(2):
                    if cand_idx < len(candidates_pool):
                        Candidate.objects.create(
                            student_profile=candidates_pool[cand_idx],
                            position=positions['President'],
                            election=election,
                            partylist=random.choice(partylists),
                            is_approved=True,
                            biography="I will serve with integrity."
                        )
                        cand_idx += 1
                
                # VP (2 candidates)
                for _ in range(2):
                    if cand_idx < len(candidates_pool):
                        Candidate.objects.create(
                            student_profile=candidates_pool[cand_idx],
                            position=positions['Vice President'],
                            election=election,
                            partylist=random.choice(partylists),
                            is_approved=True,
                            biography="Vote for progress."
                        )
                        cand_idx += 1
                
                # Senators (6 candidates)
                for _ in range(6):
                    if cand_idx < len(candidates_pool):
                        Candidate.objects.create(
                            student_profile=candidates_pool[cand_idx],
                            position=positions['Senator'],
                            election=election,
                            partylist=random.choice(partylists),
                            is_approved=True,
                            biography="Voice of the students."
                        )
                        cand_idx += 1
                
                # Reset index if we run out (allow students to run in multiple elections if needed, though typically not allowed, but for dummy data it's fine)
                if cand_idx >= len(candidates_pool):
                    cand_idx = 0
            
            self.stdout.write('Registered candidates for all active elections.')

            # 7. Simulate Voting
            # Have 40 students cast votes in each election
            
            for election in active_elections:
                self.stdout.write(f'Simulating voting for {election.name}...')
                election_candidates = list(Candidate.objects.filter(election=election))
                
                for voter in remaining_students[:40]:
                    choices = []
                    
                    # Pick 1 for President
                    pres_cands = [c for c in election_candidates if c.position.name == 'President']
                    if pres_cands:
                        choices.append(random.choice(pres_cands))
                    
                    # Pick 1 for VP
                    vp_cands = [c for c in election_candidates if c.position.name == 'Vice President']
                    if vp_cands:
                        choices.append(random.choice(vp_cands))
                    
                    # Pick 3 Senators
                    sen_cands = [c for c in election_candidates if c.position.name == 'Senator']
                    if len(sen_cands) >= 3:
                        choices.extend(random.sample(sen_cands, 3))
                    elif sen_cands:
                        choices.extend(sen_cands)
                    
                    # Cast Votes
                    ballot_id = uuid.uuid4()
                    for choice in choices:
                        Vote.objects.create(
                            election=election,
                            candidate=choice,
                            position=choice.position,
                            ballot_id=ballot_id
                        )
                    
                    # Create Receipt
                    VoterReceipt.objects.create(
                        voter=voter,
                        election=election,
                        ballot_id=ballot_id,
                        encrypted_choices=f"Encrypted data for {len(choices)} votes"
                    )
                
            self.stdout.write('Simulated voting for 40 students in each election.')
            
            # 8. Create Audit Logs
            admin_user = User.objects.get(username='admin_staff')
            audit_actions = [
                {'action': 'ELECTION_CREATED', 'details': f'Created election: {e1.name}'},
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
