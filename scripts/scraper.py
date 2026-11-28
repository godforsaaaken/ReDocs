#!/usr/bin/env python3
"""Polite crawler that collects public documents (PDF / scanned images) from
government websites for the ReDocs local test set.

Standard library only. It obeys robots.txt (including Crawl-delay), waits
between requests, stays inside the domains you allow, checks that each download
really is a PDF/image, and records where every file came from.

Suggested location: scripts/scraper.py. Output defaults to pairs/gov-docs/,
which your .gitignore already excludes. Run with --dry-run first.

Examples:
    python scripts/scrape_gov_docs.py --seed <listing-page-url> --dry-run
    python scripts/scrape_gov_docs.py --seed <listing-page-url> --max-files 20 --contact you@example.com
    # sites whose download links have no .pdf in the URL (e.g. .../download/34080):
    python scripts/scrape_gov_docs.py --seed <listing-page-url> --file-pattern "/download/\\d+"
"""
import argparse
import hashlib
import http.client
import json
import re
import time
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urldefrag, urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "pairs" / "gov-docs"
PAGE_LIMIT = 2 * 1024 * 1024  # max bytes read for an HTML page
CANON = {"jpeg": "jpg", "tiff": "tif"}
SIGNATURES = [
    (".pdf", b"%PDF"),
    (".jpg", b"\xff\xd8\xff"),
    (".png", b"\x89PNG\r\n\x1a\n"),
    (".tif", b"II*\x00"),
    (".tif", b"MM\x00*"),
]
# Never worth fetching as an HTML page.
SKIP_EXT = {
    ".css", ".js", ".ico", ".svg", ".gif", ".webp", ".bmp", ".woff", ".woff2",
    ".ttf", ".zip", ".rar", ".7z", ".mp3", ".mp4", ".doc", ".docx", ".xls",
    ".xlsx", ".ppt", ".pptx",
}


class RateLimited(Exception):
    pass


class ScopedRedirectHandler(HTTPRedirectHandler):
    def __init__(self, crawler, check_robots=True):
        super().__init__()
        self.crawler = crawler
        self.check_robots = check_robots

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urljoin(req.full_url, newurl)
        source_scheme = urlparse(req.full_url).scheme
        target_scheme = urlparse(target).scheme
        if target_scheme not in ("http", "https") or not self.crawler.in_scope(target):
            raise HTTPError(
                req.full_url, code, "redirect outside allowed domains", headers, fp
            )
        if source_scheme == "https" and target_scheme != "https":
            raise HTTPError(
                req.full_url, code, "refusing HTTPS-to-HTTP redirect", headers, fp
            )
        if self.check_robots and not self.crawler.robots_ok(target):
            raise HTTPError(
                req.full_url, code, "redirect destination disallowed by robots.txt",
                headers, fp,
            )
        return super().redirect_request(req, fp, code, msg, headers, target)


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        wanted = {"a": "href", "iframe": "src", "embed": "src", "object": "data"}.get(tag)
        for key, value in attrs:
            if key == wanted and value:
                self.links.append(value.strip())


def canon_ext(ext):
    ext = ext.lower().lstrip(".")
    return "." + CANON.get(ext, ext)


def sniff(body):
    for ext, magic in SIGNATURES:
        if body.startswith(magic):
            return ext
    return None


class Crawler:
    def __init__(self, args):
        self.a = args
        self.ua = "ReDocs-research-crawler/0.1" + (f" (+{args.contact})" if args.contact else "")
        self.wanted = {canon_ext(e) for e in args.ext.split(",") if e.strip()}
        self.pattern = re.compile(args.file_pattern) if args.file_pattern else None
        self.domains = {d.lower() for d in args.allow_domain} or {
            urlparse(s).hostname.lower() for s in args.seed
        }
        self.out = Path(args.out)
        self.manifest_path = self.out / "manifest.jsonl"
        self.known_urls, self.known_hashes = set(), set()
        self.robots, self.crawl_delay = {}, {}
        self.last_request = 0.0
        self.pages = 0
        self.saved = 0
        self.opener = build_opener(ScopedRedirectHandler(self))
        self.robots_opener = build_opener(
            ScopedRedirectHandler(self, check_robots=False)
        )

    # --- scope, politeness -------------------------------------------------
    def in_scope(self, url):
        host = (urlparse(url).hostname or "").lower()
        return any(host == d or host.endswith("." + d) for d in self.domains)

    def throttle(self):
        wait = max(self.a.delay, max(self.crawl_delay.values(), default=0))
        elapsed = time.monotonic() - self.last_request
        if elapsed < wait:
            time.sleep(wait - elapsed)
        self.last_request = time.monotonic()

    def robots_ok(self, url):
        parts = urlparse(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        rp = self.robots.get(origin)
        if rp is None:
            rp = RobotFileParser()
            self.throttle()
            try:
                req = Request(origin + "/robots.txt", headers={"User-Agent": self.ua})
                with self.robots_opener.open(req, timeout=self.a.timeout) as r:
                    rules = r.read(512_001)
                    if len(rules) > 512_000:
                        raise ValueError("robots.txt exceeds 512 KB")
                    rp.parse(rules.decode("utf-8", "replace").splitlines())
            except HTTPError as e:
                if e.code in (401, 403):
                    print(f"  robots.txt returned HTTP {e.code} for {origin}; failing closed")
                    rp.disallow_all = True
                elif e.code in (404, 410):
                    rp.allow_all = True
                elif e.code in (429, 503):
                    raise RateLimited(origin + "/robots.txt") from e
                else:
                    print(f"  cannot read robots.txt for {origin} (HTTP {e.code}); skipping host")
                    rp.disallow_all = True
            except (URLError, OSError, http.client.HTTPException) as e:
                print(f"  cannot read robots.txt for {origin} ({e}); skipping host")
                rp.disallow_all = True
            except ValueError as e:
                print(f"  cannot read robots.txt for {origin} ({e}); skipping host")
                rp.disallow_all = True
            self.robots[origin] = rp
            delay = rp.crawl_delay(self.ua)
            if delay:
                self.crawl_delay[origin] = float(delay)
        return rp.can_fetch(self.ua, url)

    # --- network -----------------------------------------------------------
    def fetch(self, url, limit):
        """GET url -> (final_url, content_type, body, charset), or None if skipped."""
        self.throttle()
        req = Request(url, headers={"User-Agent": self.ua, "Accept": "*/*"})
        try:
            with self.opener.open(req, timeout=self.a.timeout) as r:
                length = r.headers.get("Content-Length", "")
                if length.isdigit() and int(length) > limit:
                    print(f"  skip (too large, {int(length) // 1024} KB): {url}")
                    return None
                body = r.read(limit + 1)
                if len(body) > limit:
                    print(f"  skip (too large): {url}")
                    return None
                return r.geturl(), r.headers.get_content_type(), body, r.headers.get_content_charset()
        except HTTPError as e:
            if e.code in (429, 503):
                raise RateLimited(url) from e
            print(f"  HTTP {e.code} ({e.reason}): {url}")
        except (URLError, OSError, http.client.HTTPException) as e:
            print(f"  failed ({e}): {url}")
        return None

    # --- files -------------------------------------------------------------
    def is_candidate(self, url):
        path = urlparse(url).path
        if canon_ext(Path(path).suffix or ".") in self.wanted:
            return True
        return bool(self.pattern and self.pattern.search(url))

    def handle_file(self, url, found_on):
        if url in self.known_urls:
            return
        if not self.robots_ok(url):
            print(f"  robots policy blocks or is unavailable (fail-closed): {url}")
            return
        if self.a.dry_run:
            print(f"  [dry-run] would download: {url}")
            self.saved += 1
            return
        got = self.fetch(url, self.a.max_size_mb * 1024 * 1024)
        if not got:
            return
        final, ctype, body, _ = got
        if not self.in_scope(final):
            return
        self.known_urls.add(url)
        ext = sniff(body)
        if ext is None or ext not in self.wanted:
            print(f"  not a wanted file (got {ctype}): {url}")
            return
        digest = hashlib.sha256(body).hexdigest()
        if digest in self.known_hashes:
            print(f"  duplicate content, skipped: {url}")
            return
        stem = re.sub(r"[^\w.\-]+", "_", unquote(Path(urlparse(url).path).stem))[:60] or "file"
        name = f"{digest[:12]}_{stem}{ext}"
        (self.out / name).write_bytes(body)
        self.known_hashes.add(digest)
        record = {
            "url": url,
            "found_on": found_on,
            "file": name,
            "sha256": digest,
            "bytes": len(body),
            "content_type": ctype,
            "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        with self.manifest_path.open("a", encoding="utf-8") as m:
            m.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.saved += 1
        print(f"  saved [{self.saved}] {name} ({len(body) // 1024} KB)")

    def load_manifest(self):
        if self.manifest_path.exists():
            for line in self.manifest_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    self.known_urls.add(rec["url"])
                    self.known_hashes.add(rec["sha256"])

    # --- crawl -------------------------------------------------------------
    def run(self):
        self.out.mkdir(parents=True, exist_ok=True)
        self.load_manifest()
        queue = deque((s, 0) for s in self.a.seed)
        seen = set(self.a.seed)
        try:
            while queue and self.pages < self.a.max_pages and self.saved < self.a.max_files:
                url, depth = queue.popleft()
                if not self.robots_ok(url):
                    print(f"robots policy blocks or is unavailable (fail-closed): {url}")
                    continue
                got = self.fetch(url, PAGE_LIMIT)
                if not got:
                    continue
                final, ctype, body, charset = got
                if not self.in_scope(final) or ctype not in ("text/html", "application/xhtml+xml"):
                    continue
                self.pages += 1
                print(f"[page {self.pages}/{self.a.max_pages}, depth {depth}] {url}")
                parser = LinkParser()
                parser.feed(body.decode(charset or "utf-8", "replace"))
                for href in parser.links:
                    link = urldefrag(urljoin(final, href))[0]
                    if not link.startswith(("http://", "https://")) or link in seen:
                        continue
                    if not self.in_scope(link):
                        continue
                    seen.add(link)
                    if self.is_candidate(link):
                        if self.saved >= self.a.max_files:
                            break
                        self.handle_file(link, final)
                    elif depth < self.a.depth and Path(urlparse(link).path).suffix.lower() not in SKIP_EXT:
                        queue.append((link, depth + 1))
        except RateLimited as e:
            print(f"\nServer asked us to slow down (429/503) at {e}. Stopping; raise --delay and retry later.")
        except KeyboardInterrupt:
            print("\nInterrupted; progress so far is kept in the manifest.")
        verb = "would download" if self.a.dry_run else "saved"
        print(f"\nDone: {self.pages} pages crawled, {self.saved} files {verb}. Output: {self.out}")


def main():
    p = argparse.ArgumentParser(description="Polite crawler for public government documents.")
    p.add_argument("--seed", action="append", required=True, help="start URL (repeatable)")
    p.add_argument("--allow-domain", action="append", default=[],
                   help="extra domain to stay within (default: the seeds' domains)")
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--ext", default="pdf,jpg,jpeg,png,tif,tiff", help="file types to collect")
    p.add_argument("--file-pattern", help="regex for download links without a file extension")
    p.add_argument("--depth", type=int, default=2, help="link depth from the seeds")
    p.add_argument("--max-pages", type=int, default=50)
    p.add_argument("--max-files", type=int, default=100)
    p.add_argument("--max-size-mb", type=int, default=25)
    p.add_argument("--delay", type=float, default=3.0, help="seconds between requests")
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--contact", help="email or URL added to the User-Agent so admins can reach you")
    p.add_argument("--dry-run", action="store_true", help="list files, download nothing")
    args = p.parse_args()
    for seed in args.seed:
        parts = urlparse(seed)
        if parts.scheme not in ("http", "https") or not parts.hostname or parts.username:
            p.error(f"seed must be an HTTP(S) URL with a hostname: {seed}")
    for domain in args.allow_domain:
        if not re.fullmatch(r"[A-Za-z0-9.-]+", domain):
            p.error(f"allow-domain must be a hostname: {domain}")
    if args.depth < 0 or args.max_pages < 0 or args.max_files < 0:
        p.error("depth, max-pages, and max-files must be non-negative")
    if args.max_size_mb <= 0 or args.timeout <= 0 or args.delay < 0:
        p.error("max-size-mb and timeout must be positive; delay must be non-negative")
    try:
        re.compile(args.file_pattern) if args.file_pattern else None
    except re.error as e:
        p.error(f"invalid file-pattern: {e}")
    Crawler(args).run()


if __name__ == "__main__":
    main()
