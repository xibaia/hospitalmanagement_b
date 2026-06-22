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
    def test_activities_list_returns_participant_count_and_joined_state(self):
        patient_user, _ = create_patient(username="activity_list_patient")
        activity = create_activity(name="List activity")
        ActivityParticipant.objects.create(
            activity=activity,
            user=patient_user,
            role="volunteer",
        )

        response = self.client.get(
            reverse("api-activities-list"),
            **auth_headers(patient_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["data"][0]["id"], activity.id)
        self.assertEqual(response.data["data"][0]["participant_count"], 1)
        self.assertTrue(response.data["data"][0]["is_joined"])

    def test_activity_detail_hides_participants_for_patient(self):
        patient_user, _ = create_patient(username="activity_detail_patient")
        doctor_user, _ = create_doctor(username="activity_detail_doctor")
        activity = create_activity(name="Detail activity")
        ActivityParticipant.objects.create(
            activity=activity,
            user=doctor_user,
            role="doctor",
        )

        response = self.client.get(
            reverse("api-activity-detail", args=[activity.id]),
            **auth_headers(patient_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["participant_count"], 1)
        self.assertNotIn("participants", response.data["data"])

    def test_activity_detail_shows_participants_for_doctor(self):
        doctor_user, _ = create_doctor(username="activity_detail_visible_doctor")
        patient_user, _ = create_patient(username="activity_detail_visible_patient")
        activity = create_activity(name="Doctor detail activity")
        ActivityParticipant.objects.create(
            activity=activity,
            user=patient_user,
            role="volunteer",
        )

        response = self.client.get(
            reverse("api-activity-detail", args=[activity.id]),
            **auth_headers(doctor_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["participant_count"], 1)
        self.assertEqual(len(response.data["data"]["participants"]), 1)

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

    def test_pending_doctor_token_cannot_read_draft_activity_as_doctor(self):
        pending_doctor_user, _ = create_doctor(
            username="pending_activity_doctor",
            status=False,
        )
        draft_activity = create_activity(
            name="Draft activity",
            status="draft",
        )

        response = self.client.get(
            reverse("api-activity-detail", args=[draft_activity.id]),
            **auth_headers(pending_doctor_user),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_pending_doctor_join_role_is_downgraded_to_volunteer(self):
        pending_doctor_user, _ = create_doctor(
            username="pending_join_activity_doctor",
            status=False,
        )
        activity = create_activity()

        response = self.client.post(
            reverse("api-activity-join", args=[activity.id]),
            {"role": "doctor"},
            format="json",
            **auth_headers(pending_doctor_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        participant = ActivityParticipant.objects.get(activity=activity, user=pending_doctor_user)
        self.assertEqual(participant.role, "volunteer")

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
