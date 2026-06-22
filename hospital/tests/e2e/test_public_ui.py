from hospital.tests.e2e.base import WebUITestCase


class PublicWebUITests(WebUITestCase):
    def test_home_page_loads(self):
        self.goto("/")

        self.assert_page_contains("You’ll Love the Way We Care for You")

    def test_public_entry_pages_load(self):
        pages = [
            ("/aboutus", "About Us !"),
            ("/contactus", "Send Us Your Valuable Feedback !"),
            ("/adminclick", "Hello, Admin"),
            ("/doctorclick", "Hello, Doctor"),
            ("/patientclick", "Hello, Patient"),
        ]

        for path, expected_text in pages:
            with self.subTest(path=path):
                self.goto(path)

                self.assert_page_contains(expected_text)
