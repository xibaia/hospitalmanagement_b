from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from hospital.tests.helpers import create_doctor


class DoctorDirectoryAPITests(APITestCase):
    def test_doctors_list_returns_only_approved_doctors(self):
        _, approved = create_doctor(username="approved_directory_doctor", status=True)
        create_doctor(username="pending_directory_doctor", status=False)

        response = self.client.get(reverse("api-doctors-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        doctor_names = {item["doctor_name"] for item in response.data["data"]}
        self.assertIn(approved.get_name, doctor_names)
        self.assertEqual(len(response.data["data"]), 1)
