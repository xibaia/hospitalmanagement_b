from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from hospital.models import Patient
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    auth_headers,
    create_doctor,
    create_patient,
)


class PatientAuthAPITests(APITestCase):
    def test_patient_register_success_creates_inactive_patient(self):
        _, doctor = create_doctor(username="approved_doctor")

        response = self.client.post(
            reverse("api-patient-register"),
            {
                "first_name": "Test",
                "last_name": "Patient",
                "username": "new_patient",
                "password": DEFAULT_PASSWORD,
                "confirm_password": DEFAULT_PASSWORD,
                "mobile": "13800138001",
                "address": "Registration address",
                "symptoms": "Registration symptoms",
                "assigned_doctor_id": doctor.user_id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

        patient = Patient.objects.get(user__username="new_patient")
        self.assertFalse(patient.status)
        self.assertEqual(patient.assignedDoctorId, doctor.user_id)
        self.assertTrue(
            Group.objects.get(name="PATIENT").user_set.filter(username="new_patient").exists()
        )

    def test_patient_login_success_returns_token(self):
        create_patient(username="active_patient")

        response = self.client.post(
            reverse("api-patient-login"),
            {"username": "active_patient", "password": DEFAULT_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("token", response.data["data"])

    def test_patient_login_rejects_wrong_password(self):
        create_patient(username="wrong_password_patient")

        response = self.client.post(
            reverse("api-patient-login"),
            {"username": "wrong_password_patient", "password": "bad-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_patient_info_requires_token(self):
        response = self.client.get(reverse("api-patient-info"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_doctor_token_cannot_read_patient_info(self):
        doctor_user, _ = create_doctor(username="doctor_not_patient")

        response = self.client.get(
            reverse("api-patient-info"),
            **auth_headers(doctor_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DoctorAuthAPITests(APITestCase):
    def test_doctor_login_success_returns_token(self):
        create_doctor(username="active_doctor")

        response = self.client.post(
            reverse("api-doctor-login"),
            {"username": "active_doctor", "password": DEFAULT_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("token", response.data["data"])

    def test_patient_token_cannot_access_doctor_patients(self):
        patient_user, _ = create_patient(username="not_a_doctor")

        response = self.client.get(
            reverse("api-doctor-patients"),
            **auth_headers(patient_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
