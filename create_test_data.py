import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_config.settings')
django.setup()

from apps.elections.models import Election, ElectionTimeline

# Clear existing
Election.objects.all().delete()

now = timezone.now()

# Election 1: Active, ongoing
e1 = Election.objects.create(
    name="Student Council Election 2025",
    start_time=now - timedelta(days=2),
    end_time=now + timedelta(days=5),
    is_active=True
)

ElectionTimeline.objects.create(
    election=e1,
    title="Filing of Candidacy",
    start_time=now - timedelta(days=10),
    end_time=now - timedelta(days=5),
    description="Submit your COC at the office.",
    order=1
)

ElectionTimeline.objects.create(
    election=e1,
    title="Campaign Period",
    start_time=now - timedelta(days=4),
    end_time=now - timedelta(days=1),
    description="Campaigning is allowed.",
    order=2
)

ElectionTimeline.objects.create(
    election=e1,
    title="Voting Period",
    start_time=now,
    end_time=now + timedelta(days=5),
    description="Cast your votes.",
    order=3
)

# Election 2: Upcoming
e2 = Election.objects.create(
    name="Special Election 2025",
    start_time=now + timedelta(days=10),
    end_time=now + timedelta(days=15),
    is_active=True
)

ElectionTimeline.objects.create(
    election=e2,
    title="Filing of Candidacy",
    start_time=now + timedelta(days=5),
    end_time=now + timedelta(days=8),
    description="Submit COCs.",
    order=1
)

print("Test data created.")
