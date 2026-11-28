import unittest
from email.message import Message
from io import BytesIO
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request

from scraper import ScopedRedirectHandler


class FakeCrawler:
    def __init__(self, robots_allowed=True):
        self.robots_allowed = robots_allowed

    def in_scope(self, url):
        host = (urlparse(url).hostname or "").lower()
        return host == "example.go.id" or host.endswith(".example.go.id")

    def robots_ok(self, url):
        return self.robots_allowed and url.startswith("https://")


class ScopedRedirectHandlerTests(unittest.TestCase):
    def setUp(self):
        self.request = Request("https://docs.example.go.id/page")
        self.headers = Message()

    def redirect(self, target, robots_allowed=True):
        handler = ScopedRedirectHandler(FakeCrawler(robots_allowed))
        return handler.redirect_request(
            self.request, BytesIO(), 302, "Found", self.headers, target
        )

    def test_allows_in_scope_https_redirect(self):
        redirected = self.redirect("/document.pdf")

        self.assertEqual(redirected.full_url, "https://docs.example.go.id/document.pdf")

    def test_rejects_redirect_outside_allowed_domain(self):
        with self.assertRaises(HTTPError) as raised:
            self.redirect("https://example.com/document.pdf")
        raised.exception.close()

    def test_rejects_https_downgrade(self):
        with self.assertRaises(HTTPError) as raised:
            self.redirect("http://docs.example.go.id/document.pdf")
        raised.exception.close()

    def test_rejects_redirect_disallowed_by_robots(self):
        with self.assertRaises(HTTPError) as raised:
            self.redirect("/private/document.pdf", robots_allowed=False)
        raised.exception.close()


if __name__ == "__main__":
    unittest.main()
