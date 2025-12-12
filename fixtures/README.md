# 2022 Philippine National Election Data Fixture

This directory contains a complete data dump of the 2022 Philippine National Elections with real candidate information.

## Contents

### `philippine_2022_election.json`

Complete Django fixture containing:

- **2 Positions**: President, Vice President
- **13 Political Parties**: PFP, Liberal, Aksyon, PLM, LAKAS, NPC, PROMDI, PDSP, KTPNAN, DPP, Buhay, WPP, Independent
- **1 Election Event**: 2022 Philippine National Elections (May 9, 2022)
- **19 User Accounts**: One for each candidate
- **19 Student Profiles**: Linked to user accounts
- **19 Candidates**:
  - 10 Presidential candidates
  - 9 Vice-Presidential candidates

## Presidential Candidates

1. **Ferdinand "Bongbong" Marcos Jr.** (PFP) - 🏆 Winner
2. **Leni Robredo** (Independent)
3. **Manny Pacquiao** (PROMDI)
4. **Isko Moreno** (Aksyon Demokratiko)
5. **Panfilo "Ping" Lacson** (Independent)
6. **Leody De Guzman** (PLM)
7. **Norberto Gonzales** (PDSP)
8. **Faisal Mangondato** (KTPNAN)
9. **Ernesto Abella** (Independent)
10. **Jose Montemayor Jr.** (DPP)

## Vice-Presidential Candidates

1. **Sara Duterte-Carpio** (Lakas-CMD) - 🏆 Winner
2. **Francis "Kiko" Pangilinan** (Liberal Party)
3. **Vicente "Tito" Sotto III** (NPC)
4. **Willie Ong** (Aksyon Demokratiko)
5. **Lito Atienza** (Buhay/PROMDI)
6. **Walden Bello** (PLM)
7. **Rizalito David** (DPP)
8. **Manny SD Lopez** (WPP)
9. **Carlos Serapio** (KTPNAN)

## Loading the Data

### Option 1: Using the Load Script (Recommended)

```bash
# Interactive mode (will prompt to clear existing data)
python load_philippine_election.py

# Automatically clear existing data
python load_philippine_election.py --clear

# Skip clearing (will fail if data conflicts exist)
python load_philippine_election.py --no-clear
```

### Option 2: Direct Fixture Load

```bash
# This will fail if positions with order_on_ballot 1 and 2 already exist
python manage.py loaddata fixtures/philippine_2022_election.json
```

### Option 3: Clear Data Manually First

```python
# In Django shell
python manage.py shell

from elections.models import *
from accounts.models import StudentProfile
from django.contrib.auth.models import User

# Clear election data
Vote.objects.all().delete()
VoterReceipt.objects.all().delete()
Candidate.objects.all().delete()
Election.objects.all().delete()
Position.objects.all().delete()
Partylist.objects.all().delete()

# Clear candidate user accounts (IDs 101-119)
StudentProfile.objects.filter(pk__gte=101, pk__lte=119).delete()
User.objects.filter(pk__gte=101, pk__lte=119).delete()

exit()

# Then load fixture
python manage.py loaddata fixtures/philippine_2022_election.json
```

## Verification

After loading, verify the data:

```bash
python manage.py shell
```

```python
from elections.models import Election, Candidate

# Get the election
election = Election.objects.get(name="2022 Philippine National Elections")

# Count candidates
presidential = Candidate.objects.filter(election=election, position__name="President").count()
vp = Candidate.objects.filter(election=election, position__name="Vice President").count()

print(f"Presidential candidates: {presidential}")  # Should be 10
print(f"VP candidates: {vp}")  #  Should be 9
```

Or visit Django admin at `/admin/elections/candidate/`

## Notes

- User passwords are set to invalid hashes - these are candidate profiles, not login accounts
- Student IDs follow pattern: `2022-PRES-XXX` for presidential, `2022-VP-XXX` for VP candidates
- Photos are not included - placeholder images will be used
- The election is set to inactive (`is_active=false`) and dated in the past
- All candidates are marked as approved (`is_approved=true`)

## Data Source

Candidate information sourced from:
- Commission on Elections (COMELEC) official records
- Wikipedia: 2022 Philippine presidential election
- Philippine Star election coverage
- Vote Pilipinas election database

## License

This data is provided for educational and demonstration purposes only.
