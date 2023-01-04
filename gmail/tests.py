from django.urls import reverse
from rest_framework import status
from gmail.common import get_labels
from rest_framework.test import APITestCase

class Labels(APITestCase):
    def test_get_all_account_labels(self):
        url=reverse("gmail:labels")
        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_get_account_labels_type_system(self):
        labels=get_labels(type="system")
        label=labels.get("labels")[0]
        self.assertEqual(label.get("type"),"system")

    def test_get_account_labels_type_user(self):
        labels=get_labels(type="user")
        label=labels.get("labels")[0]
        self.assertEqual(label.get("type"),"user")

class Filters(APITestCase):
    def test_get_all_account_filters(self):
        url=reverse("gmail:filters")
        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

class Senders(APITestCase):
    def test_get_senders(self):
        url=reverse("gmail:senders")
        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

class CleanUp(APITestCase):
    def test_account_clean_up(self):
        url=reverse("gmail:clean-up-mailbox")
        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)