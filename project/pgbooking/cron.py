# pgbooking/cron.py
from django_cron import CronJobBase, Schedule
from django.utils import timezone
from .models import ownerregistration

class DeleteUnapprovedOwnersCronJob(CronJobBase):
    RUN_EVERY_MINS = 60  # Check every 60 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'pgbooking.delete_unapproved_owners'

    def do(self):
        now = timezone.now()
        expired_owners = ownerregistration.objects.filter(approved=False, auto_delete_time__lt=now)
        expired_owners.delete()
