from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from hospital.tests.helpers import (
    auth_headers,
    create_doctor,
    create_patient,
    create_record,
)


class PatientMedicalRecordAPITests(APITestCase):
    def test_patient_records_only_returns_current_patient_records(self):
        _, doctor = create_doctor(username="record_doctor")
        patient_user, patient = create_patient(
            username="record_patient",
            assigned_doctor=doctor,
        )
        _, other_patient = create_patient(username="other_record_patient")
        own_record = create_record(patient=patient, doctor=doctor)
        create_record(patient=other_patient, doctor=doctor)

        response = self.client.get(
            reverse("api-patient-records"),
            **auth_headers(patient_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        returned_ids = {item["id"] for item in response.data["data"]}
        self.assertEqual(returned_ids, {own_record.id})


class DoctorMedicalRecordAPITests(APITestCase):
    def test_doctor_records_only_returns_own_records(self):
        doctor_user, doctor = create_doctor(username="owning_doctor")
        _, other_doctor = create_doctor(username="other_doctor")
        _, patient = create_patient(username="doctor_record_patient", assigned_doctor=doctor)
        own_record = create_record(patient=patient, doctor=doctor)
        create_record(patient=patient, doctor=other_doctor)

        response = self.client.get(
            reverse("api-doctor-records"),
            **auth_headers(doctor_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        returned_ids = {item["id"] for item in response.data["data"]}
        self.assertEqual(returned_ids, {own_record.id})
