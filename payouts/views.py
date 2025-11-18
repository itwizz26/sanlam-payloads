from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Count
from dateutil import parser
from django.db import models

from .models import Payout
from .serializers import PayoutSerializer

class PayoutViewSet(viewsets.ModelViewSet):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer
    http_method_names = ['get', 'post', 'head'] 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        payout, created = Payout.objects.get_or_create(
            external_ref=data['external_ref'],
            partner_code=data['partner_code'],
            defaults=data 
        )

        if created:
            http_status = status.HTTP_201_CREATED
            message = "Payout intake successful."
        else:
            http_status = status.HTTP_200_OK
            message = "Payout already exists."

        response_data = self.get_serializer(payout).data
        response_data['message'] = message

        return Response(response_data, status=http_status)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not all([start_date_str, end_date_str]):
            return Response(
                {"error": "Both 'start_date' and 'end_date' parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date = parser.parse(start_date_str.strip())
            end_date = parser.parse(end_date_str.strip())
            if start_date is None or end_date is None:
                 raise ValueError
        except ValueError:
            return Response(
                {"error": "Dates must be in a valid ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(
            occurred_at__gte=start_date,
            occurred_at__lt=end_date
        )

        grouped_summary = queryset.values('status').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        ).order_by('status')

        overall_totals = queryset.aggregate(
            grand_total=Sum('amount'),
            total_payout_count=Count('id')
        )

        response_data = {
            "date_range": {
                "start": start_date_str,
                "end": end_date_str
            },
            "summary_by_status": list(grouped_summary),
            "overall_totals": overall_totals
        }

        return Response(response_data, status=status.HTTP_200_OK)