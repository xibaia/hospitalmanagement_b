import os
from pathlib import Path

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright


os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


class WebUITestCase(StaticLiveServerTestCase):
    browser = None
    playwright = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        if cls.browser:
            cls.browser.close()
            cls.browser = None
        if cls.playwright:
            cls.playwright.stop()
            cls.playwright = None
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.page = self.browser.new_page()

    def tearDown(self):
        failed = self._test_has_failed()
        if failed:
            self._save_failure_screenshot()
        if getattr(self, "page", None):
            self.page.close()
            self.page = None
        super().tearDown()

    def goto(self, path):
        self.page.goto(f"{self.live_server_url}{path}")
        self.page.wait_for_load_state("networkidle")

    def login(self, login_path, username, password):
        self.goto(login_path)
        self.page.locator('input[name="username"]').fill(username)
        self.page.locator('input[name="password"]').fill(password)
        self.page.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("networkidle")

    def logout(self):
        response = self.page.request.post(
            f"{self.live_server_url}/logout",
            headers={"X-CSRFToken": self._csrf_token()},
        )
        self.assertEqual(response.status, 200)

    def assert_url_contains(self, path):
        self.assertIn(path, self.page.url)

    def assert_page_contains(self, text):
        self.assertIn(text, self.page.content())

    def submit_first_form(self):
        submit = self.page.locator(
            'form button[type="submit"], form input[type="submit"]'
        )
        if submit.count() == 0:
            submit = self.page.locator('button[type="submit"], input[type="submit"]')
        submit.first.click()
        self.page.wait_for_load_state("networkidle")

    def select_first_real_option(self, selector):
        select = self.page.locator(selector)
        values = select.locator("option").evaluate_all(
            "(options) => options.map((option) => option.value).filter(Boolean)"
        )
        self.assertGreater(len(values), 0)
        select.select_option(values[0])
        return values[0]

    def click_form_action(self, action_fragment):
        button = self.page.locator(
            f'form[action*="{action_fragment}"] button[type="submit"]'
        )
        self.assertEqual(button.count(), 1)
        button.click()
        self.page.wait_for_load_state("networkidle")

    def _csrf_token(self):
        for cookie in self.page.context.cookies(self.live_server_url):
            if cookie["name"] == "csrftoken":
                return cookie["value"]
        self.fail("Missing CSRF cookie before logout")

    def _test_has_failed(self):
        outcome = getattr(self, "_outcome", None)
        if not outcome:
            return False
        result = getattr(outcome, "result", None)
        if not result:
            return False
        test_id = self.id()
        return any(test.id() == test_id for test, _ in result.failures + result.errors)

    def _save_failure_screenshot(self):
        if not getattr(self, "page", None):
            return
        screenshot_dir = Path("test-artifacts/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / f"{self.id().replace('.', '_')}.png"
        try:
            self.page.screenshot(path=str(screenshot_path), full_page=True)
        except Exception:
            pass
