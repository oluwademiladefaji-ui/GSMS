#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create BUAdmin superuser if it doesn't exist
python manage.py shell << 'EOF'
from accounts.models import User
if not User.objects.filter(username='BUAdmin').exists():
    User.objects.create_superuser(username='BUAdmin', email='admin@bu.edu', password='Admin')
    print("BUAdmin created.")
else:
    print("BUAdmin already exists.")
EOF
