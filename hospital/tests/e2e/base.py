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

    def assert_page_contains(self, text):
        self.assertIn(text, self.page.content())

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
