#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "from accounts.models import User; User.objects.create_superuser('BUAdmin', 'admin@bu.edu', 'Admin') if not filter(lambda u: u.username=='BUAdmin', User.objects.all()) else None"
