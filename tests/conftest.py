"""Use Playwright's real DOM for selector fixtures, with network access disabled."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from playwright.sync_api import sync_playwright

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def dom_page(browser):
    context = browser.new_context()
    context.route("**/*", lambda route: route.abort())
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def mock_page():
    return MagicMock()


@pytest.fixture
def simple_post_element(dom_page):
    dom_page.set_content((FIXTURES_DIR / "post_simple.html").read_text())
    return dom_page.query_selector('[role="article"]')


@pytest.fixture
def simple_comment_element(dom_page):
    dom_page.set_content((FIXTURES_DIR / "comment_simple.html").read_text())
    return dom_page.query_selector('[role="article"]')
