import pytest
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from datetime import datetime, timezone
from payouts.models import Payout

@pytest.fixture
def sample_payout_data():
    """Data for a standard payout submission."""
    return {
        "external_ref": "test-payout-123",
        "partner_code": "ACME",
        "amount": "150.75",
        "currency": "EUR",
        "occurred_at": "2025-11-17T10:30:00Z",
        "description": "Initial January test payout"
    }


@pytest.mark.django_db
def test_intake_new_payout(client, sample_payout_data):
    """
    Covers: Intake of a new payout.
    Should result in HTTP 201 CREATED and one database record.
    """
    url = reverse('payout-list')
    response = client.post(url, sample_payout_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert Payout.objects.count() == 1
    assert response.data['message'] == "Payout intake successful."
    assert Decimal(response.data['amount']) == Decimal("150.75")


@pytest.mark.django_db
def test_intake_resubmission_duplicate(client, sample_payout_data):
    """
    Covers: Resubmission of the same payout (idempotency check).
    Should result in HTTP 200 OK and still only one database record.
    """
    url = reverse('payout-list')
    client.post(
        url,
        sample_payout_data,
        format='json'
    )
    response_2 = client.post(
        url,
        sample_payout_data,
        format='json'
    )

    assert response_2.status_code == status.HTTP_200_OK
    assert response_2.data['message'] == "Payout already exists."
    assert Payout.objects.count() == 1


@pytest.fixture
def summary_test_data(db):
    """Sets up a dataset with multiple statuses and date ranges."""

    Payout.objects.create(
        external_ref="p1",
        partner_code="acme",
        amount=Decimal("100.00"),
        currency="USD",
        occurred_at=datetime(2025, 11, 17, 14, 0, tzinfo=timezone.utc),
        status="RECEIVED"
    )
    Payout.objects.create(
        external_ref="p2",
        partner_code="acme",
        amount=Decimal("50.00"),
        currency="USD",
        occurred_at=datetime(2025, 11, 17, 15, 0, tzinfo=timezone.utc),
        status="PROCESSED"
    )
    Payout.objects.create(
        external_ref="p3",
        partner_code="bravo",
        amount=Decimal("75.00"),
        currency="USD",
        occurred_at=datetime(2025, 11, 18, 17, 0, tzinfo=timezone.utc),
        status="PROCESSED"
    )
    Payout.objects.create(
        external_ref="p4",
        partner_code="bravo",
        amount=Decimal("200.00"),
        currency="USD",
        occurred_at=datetime(2025, 11, 19, 0, 0, tzinfo=timezone.utc),
        status="FLAGGED"
    )
    Payout.objects.create(
        external_ref="p5",
        partner_code="early",
        amount=Decimal("10.00"),
        currency="USD",
        occurred_at=datetime(2025, 11, 15, 15, 0, tzinfo=timezone.utc),
        status="RECEIVED"
    )

@pytest.mark.django_db
def test_summary_calculations_correct_range(client, summary_test_data):
    """
    Covers: Summary calculations for a representative date range, including filtering.
    """
    url = reverse('payout-summary')
    query_params = {
        'start_date': '2025-11-17T00:00:00Z',
        'end_date': '2025-11-19T00:00:00Z'
    }

    response = client.get(
        url,
        query_params
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.data
    expected_grand_total = Decimal("225.00")

    assert Decimal(data['overall_totals']['grand_total']) == expected_grand_total
    assert data['overall_totals']['total_payout_count'] == 3

    grouped_summary = {
        item['status']: {
            'amount': Decimal(item['total_amount']),
            'count': item['count']
        }
        for item in data['summary_by_status']
    }

    assert grouped_summary['RECEIVED']['amount'] == Decimal("100.00")
    assert grouped_summary['RECEIVED']['count'] == 1
    assert grouped_summary['PROCESSED']['amount'] == Decimal("125.00")
    assert grouped_summary['PROCESSED']['count'] == 2
    assert 'FLAGGED' not in grouped_summary