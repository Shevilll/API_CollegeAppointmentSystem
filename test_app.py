import unittest
import json
import sqlite3
from main import app, init_db, db_path


class FlaskAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # def test_register_user(self):
    #     response = self.app.post(
    #         "/api/v1/register",
    #         data=json.dumps(
    #             {
    #                 "username": "P1",
    #                 "password": "P1",
    #                 "role": "professor",
    #             }
    #         ),
    #         content_type="application/json",
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"User registered successfully", response.data)

    # def test_login_user(self):
    #     self.app.post(
    #         "/api/v1/register",
    #         data=json.dumps(
    #             {
    #                 "username": "S1",
    #                 "password": "S1",
    #                 "role": "student",
    #             }
    #         ),
    #         content_type="application/json",
    #     )

    #     response = self.app.post(
    #         "/api/v1/login",
    #         data=json.dumps({"username": "S1", "password": "S1"}),
    #         content_type="application/json",
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"token", response.data)

    # def test_set_availability(self):
    #     login_response = self.app.post(
    #         "/api/v1/login",
    #         data=json.dumps({"username": "P1", "password": "P1"}),
    #         content_type="application/json",
    #     )
    #     token = json.loads(login_response.data)["token"]

    #     response = self.app.post(
    #         "/api/v1/set_availability",
    #         data=json.dumps({"date": "2024-12-22", "time_slot": "10:00-11:00"}),
    #         headers={"Authorization": token},
    #         content_type="application/json",
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"Availability set successfully", response.data)

    # def test_view_professors(self):
    #     response = self.app.get("/api/v1/view_professors")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"P1", response.data)

    # def test_book_appointment(self):
    #     # Login as student and get token
    #     login_response = self.app.post(
    #         "/api/v1/login",
    #         data=json.dumps({"username": "S1", "password": "S1"}),
    #         content_type="application/json",
    #     )
    #     token = json.loads(login_response.data)["token"]

    #     # Book an appointment
    #     response = self.app.post(
    #         "/api/v1/book_appointment",
    #         data=json.dumps(
    #             {
    #                 "professor_id": 1,
    #                 "date": "2024-12-22",
    #                 "time_slot": "10:00-11:00",
    #             }
    #         ),
    #         headers={"Authorization": token},
    #         content_type="application/json",
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"Appointment booked successfully", response.data)

    # def test_view_professor_appointments(self):
    #     # Login as professor and get token
    #     login_response = self.app.post(
    #         "/api/v1/login",
    #         data=json.dumps({"username": "P1", "password": "P1"}),
    #         content_type="application/json",
    #     )
    #     token = json.loads(login_response.data)["token"]

    #     # View appointments
    #     response = self.app.get(
    #         "/api/v1/view_professor_appointments", headers={"Authorization": token}
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"S1", response.data)

    # def test_cancel_appointment(self):
    #     # Login as professor and get token
    #     login_response = self.app.post(
    #         "/api/v1/login",
    #         data=json.dumps({"username": "P1", "password": "P1"}),
    #         content_type="application/json",
    #     )
    #     token = json.loads(login_response.data)["token"]

    #     # Cancel an appointment
    #     response = self.app.delete(
    #         "/api/v1/cancel_appointment/1",
    #         headers={"Authorization": token},
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"Appointment canceled successfully", response.data)
