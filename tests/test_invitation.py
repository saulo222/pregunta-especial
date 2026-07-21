import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.invitation_main import app, email_limiter, ip_limiter


class InvitationAppTests(unittest.TestCase):
    def setUp(self) -> None:
        ip_limiter._attempts.clear()
        email_limiter._attempts.clear()
        self.client = TestClient(app)

    def test_home_page_loads(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("¿Quieres ser mi novia?", response.text)

    @patch("app.invitation_main.send_acceptance_emails", new_callable=AsyncMock)
    def test_yes_sends_email(self, send_mock: AsyncMock) -> None:
        response = self.client.post(
            "/api/invitation/respond",
            json={"email": "persona@example.com", "answer": "yes"},
        )

        self.assertEqual(response.status_code, 200)
        send_mock.assert_awaited_once_with("persona@example.com")

    def test_invalid_email_is_rejected(self) -> None:
        response = self.client.post(
            "/api/invitation/respond",
            json={"email": "correo-invalido", "answer": "yes"},
        )

        self.assertEqual(response.status_code, 422)

    def test_no_answer_is_rejected(self) -> None:
        response = self.client.post(
            "/api/invitation/respond",
            json={"email": "persona@example.com", "answer": "no"},
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
