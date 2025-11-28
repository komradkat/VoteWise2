---
description: How to generate election reports manually via shell
---

1. Open the Django shell:
   ```bash
   python manage.py shell
   ```

2. Run the following code to generate a report for a specific election (e.g., ID 1):
   ```python
   from apps.reports.views import generate_election_report
   from django.test import RequestFactory
   from apps.elections.models import Election

   # Create a mock request
   factory = RequestFactory()
   request = factory.get('/reports/election/1/pdf/')
   request.user = User.objects.get(username='admin') # Ensure admin user exists

   # Generate report
   response = generate_election_report(request, 1)
   
   # Save to file
   with open('election_report_1.pdf', 'wb') as f:
       f.write(response.content)
   ```

3. Verify the `election_report_1.pdf` file is created.
