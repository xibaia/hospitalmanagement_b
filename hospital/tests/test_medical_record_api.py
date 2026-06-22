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

    def test_doctor_can_create_record_for_assigned_patient(self):
        doctor_user, doctor = create_doctor(username="creator_doctor")
        _, patient = create_patient(username="assigned_create_patient", assigned_doctor=doctor)

        response = self.client.post(
            reverse("api-doctor-records"),
            {
                "patient": patient.id,
                "visit_type": "charity",
                "chief_complaint": "Tooth pain",
                "diagnosis": "Caries",
                "tooth_findings": [
                    {"tooth_number": 16, "finding_type": "caries", "note": "Deep caries"}
                ],
            },
            format="json",
            **auth_headers(doctor_user),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

    def test_doctor_cannot_create_record_for_unrelated_patient(self):
        doctor_user, _ = create_doctor(username="unrelated_creator_doctor")
        _, patient = create_patient(username="unrelated_create_patient")

        response = self.client.post(
            reverse("api-doctor-records"),
            {
                "patient": patient.id,
                "visit_type": "charity",
                "diagnosis": "Caries",
            },
            format="json",
            **auth_headers(doctor_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("patient", response.data["errors"])

    def test_doctor_cannot_change_record_patient_on_update(self):
        doctor_user, doctor = create_doctor(username="update_owner_doctor")
        _, patient = create_patient(username="original_record_patient", assigned_doctor=doctor)
        _, other_patient = create_patient(username="target_record_patient", assigned_doctor=doctor)
        record = create_record(patient=patient, doctor=doctor)

        response = self.client.put(
            reverse("api-doctor-record-detail", args=[record.id]),
            {"patient": other_patient.id, "diagnosis": "Updated diagnosis"},
            format="json",
            **auth_headers(doctor_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("patient", response.data["errors"])

    def test_doctor_record_rejects_invalid_tooth_number(self):
        doctor_user, doctor = create_doctor(username="tooth_validator_doctor")
        _, patient = create_patient(username="tooth_validator_patient", assigned_doctor=doctor)

        response = self.client.post(
            reverse("api-doctor-records"),
            {
                "patient": patient.id,
                "visit_type": "charity",
                "diagnosis": "Caries",
                "tooth_findings": [
                    {"tooth_number": 99, "finding_type": "caries", "note": "Invalid"}
                ],
            },
            format="json",
            **auth_headers(doctor_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("tooth_findings", response.data["errors"])
