from hospital.tests.e2e.base import WebUITestCase


class PublicWebUITests(WebUITestCase):
    def test_home_page_loads(self):
        self.goto("/")

        self.assert_page_contains("You’ll Love the Way We Care for You")
