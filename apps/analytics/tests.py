import json
from django.test import TestCase, Client
from django.urls import reverse
from apps.analytics.models import AnalyticsEvent

class AnalyticsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_record_valid_event(self):
        payload = {
            'event': 'project_view',
            'path': '/projects/documind/',
            'target': 'DocuMind'
        }
        response = self.client.post(
            reverse('analytics_event'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AnalyticsEvent.objects.count(), 1)
        ev = AnalyticsEvent.objects.first()
        self.assertEqual(ev.event_name, 'project_view')
        self.assertEqual(ev.path, '/projects/documind/')

    def test_reject_invalid_event_type(self):
        payload = {
            'event': 'suspicious_tracking',
            'path': '/'
        }
        response = self.client.post(
            reverse('analytics_event'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(AnalyticsEvent.objects.count(), 0)
