from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from hospital.models import ActivityParticipant
from hospital.tests.helpers import (
    auth_headers,
    create_activity,
    create_doctor,
    create_patient,
)


class ActivityAPITests(APITestCase):
    def test_patient_can_join_active_activity_once(self):
        patient_user, _ = create_patient(username="activity_patient")
        activity = create_activity()

        response = self.client.post(
            reverse("api-activity-join", args=[activity.id]),
            {"role": "doctor"},
            format="json",
            **auth_headers(patient_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        participant = ActivityParticipant.objects.get(activity=activity, user=patient_user)
        self.assertEqual(participant.role, "volunteer")

        duplicate = self.client.post(
            reverse("api-activity-join", args=[activity.id]),
            {"role": "volunteer"},
            format="json",
            **auth_headers(patient_user),
        )

        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(duplicate.data["success"])

    def test_doctor_can_join_as_doctor(self):
        doctor_user, _ = create_doctor(username="activity_doctor")
        activity = create_activity(leader=doctor_user)

        response = self.client.post(
            reverse("api-activity-join", args=[activity.id]),
            {"role": "doctor"},
            format="json",
            **auth_headers(doctor_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        participant = ActivityParticipant.objects.get(activity=activity, user=doctor_user)
        self.assertEqual(participant.role, "doctor")

    def test_user_can_leave_joined_activity(self):
        patient_user, _ = create_patient(username="leave_activity_patient")
        activity = create_activity()
        ActivityParticipant.objects.create(
            activity=activity,
            user=patient_user,
            role="volunteer",
        )

        response = self.client.delete(
            reverse("api-activity-leave", args=[activity.id]),
            **auth_headers(patient_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            ActivityParticipant.objects.filter(activity=activity, user=patient_user).exists()
        )
