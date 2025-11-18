from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Payout

class PayoutSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Payout
        fields = (
            'id', 'external_ref', 'partner_code', 'amount', 'currency',
            'occurred_at', 'description', 'status', 'created_at'
        )
        read_only_fields = ('id', 'status', 'created_at', 'updated_at')
        validators = []