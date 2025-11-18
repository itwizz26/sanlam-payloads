from django.db import models

class Payout(models.Model):
    STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('PROCESSED', 'Processed'),
        ('FLAGGED', 'Flagged'),
    ]

    external_ref = models.CharField(max_length=255)
    partner_code = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2) 
    currency = models.CharField(max_length=3)
    occurred_at = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RECEIVED'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('external_ref', 'partner_code') 
        ordering = ['-occurred_at']

    def __str__(self):
        return f"{self.partner_code}:{self.external_ref} - {self.amount} {self.currency}"