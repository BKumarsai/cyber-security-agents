"""
tools/web_tools.py
──────────────────
HTTP / web utilities for information gathering during recon phases.
"""

import requests
from urllib.parse import urljoin, urlparse
from utils.logs import get_logger
from utils.constants import REQUEST_TIMEOUT

logger = get_logger(__name__)

# Default request headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def http_get(url: str, headers: dict | None = None, timeout: int = REQUEST_TIMEOUT) -> dict:
    """
    Perform an HTTP GET request.

    Returns:
        dict with keys: status_code, text, headers, url
    """
    logger.info(f"[WebTools] GET {url}")
    merged = {**DEFAULT_HEADERS, **(headers or {})}
    try:
        resp = requests.get(url, headers=merged, timeout=timeout, verify=False)
        return {
            "status_code": resp.status_code,
            "text": resp.text,
            "headers": dict(resp.headers),
            "url": resp.url,
        }
    except Exception as exc:
        logger.error(f"[WebTools] GET failed: {exc}")
        return {"status_code": -1, "text": str(exc), "headers": {}, "url": url}


def http_post(url: str, data: dict | None = None, json: dict | None = None,
              headers: dict | None = None, timeout: int = REQUEST_TIMEOUT) -> dict:
    """
    Perform an HTTP POST request.

    Returns:
        dict with keys: status_code, text, headers, url
    """
    logger.info(f"[WebTools] POST {url}")
    merged = {**DEFAULT_HEADERS, **(headers or {})}
    try:
        resp = requests.post(url, data=data, json=json, headers=merged, timeout=timeout, verify=False)
        return {
            "status_code": resp.status_code,
            "text": resp.text,
            "headers": dict(resp.headers),
            "url": resp.url,
        }
    except Exception as exc:
        logger.error(f"[WebTools] POST failed: {exc}")
        return {"status_code": -1, "text": str(exc), "headers": {}, "url": url}


def extract_links(html: str, base_url: str = "") -> list[str]:
    """
    Extract all hyperlinks from an HTML page.

    Args:
        html:     raw HTML string
        base_url: used to resolve relative links

    Returns:
        list of absolute URLs
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        links: list[str] = []
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            if base_url:
                href = urljoin(base_url, href)
            if href.startswith("http"):
                links.append(href)
        return list(set(links))
    except ImportError:
        logger.warning("[WebTools] beautifulsoup4/lxml not installed; cannot parse links")
        return []


def extract_forms(html: str) -> list[dict]:
    """
    Extract all <form> elements from an HTML page.

    Returns:
        list of dicts: {action, method, inputs}
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        forms = []
        for form in soup.find_all("form"):
            inputs = []
            for inp in form.find_all(["input", "textarea", "select"]):
                inputs.append({
                    "name": inp.get("name", ""),
                    "type": inp.get("type", "text"),
                    "value": inp.get("value", ""),
                })
            forms.append({
                "action": form.get("action", ""),
                "method": form.get("method", "GET").upper(),
                "inputs": inputs,
            })
        return forms
    except ImportError:
        logger.warning("[WebTools] beautifulsoup4 not installed; cannot parse forms")
        return []


def check_common_paths(base_url: str, paths: list[str] | None = None) -> dict[str, int]:
    """
    Probe a list of common web paths and return their HTTP status codes.
    Useful for basic directory enumeration.

    Args:
        base_url: root URL of the target
        paths:    list of paths to probe (defaults to a built-in list)

    Returns:
        dict mapping path → status_code
    """
    if paths is None:
        paths = [
            "/admin", "/login", "/dashboard", "/api", "/api/v1",
            "/robots.txt", "/sitemap.xml", "/.env", "/config",
            "/backup", "/uploads", "/files", "/.git/HEAD",
        ]

    results: dict[str, int] = {}
    for path in paths:
        url = urljoin(base_url, path)
        resp = http_get(url)
        results[path] = resp["status_code"]
        logger.info(f"[WebTools] {resp['status_code']}  {url}")
    return results


def get_server_info(url: str) -> dict:
    """
    Retrieve server banner and technology headers.

    Returns:
        dict with server, x_powered_by, content_type
    """
    resp = http_get(url)
    h = resp.get("headers", {})
    return {
        "server":       h.get("Server", "unknown"),
        "x_powered_by": h.get("X-Powered-By", "unknown"),
        "content_type": h.get("Content-Type", "unknown"),
        "status_code":  resp["status_code"],
    }
