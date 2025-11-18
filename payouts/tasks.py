import random
from celery import shared_task
from django.utils import timezone
from .models import Payout
import time

@shared_task
def classify_payout(payout_id):
    """
    Task to classify a Payout asynchronously and update its status.
    """
    try:
        payout = Payout.objects.get(pk=payout_id)
    except Payout.DoesNotExist:
        return f"Payout {payout_id} not found."

    time.sleep(random.uniform(0.5, 2.0))

    if payout.amount > 1000 and payout.partner_code.startswith('E'):
        new_status = 'FLAGGED'
    else:
        new_status = 'PROCESSED'

    if payout.status == 'RECEIVED':
        payout.status = new_status
        payout.save(update_fields=['status'])
        return f"Payout {payout_id} classified as {new_status}."

    return f"Payout {payout_id} skipped classification (Current status: {payout.status})."