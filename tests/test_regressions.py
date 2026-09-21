"""Offline regressions for data loss and misleading command results."""

from datetime import datetime, timedelta
import os
from pathlib import Path
import sqlite3
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from forage.auth import login
from forage.cli import main
from forage.exporter import export_to_sqlite
from forage.models import Author, DateRange, GroupInfo, Post, ScrapeResult
from forage.parser import parse_modern_comment, parse_modern_post, parse_timestamp
from forage.scraper import (
    AuthenticationError,
    MarketplaceOptions,
    ScrapeOptions,
    calculate_date_range,
    scrape_group,
    search_marketplace,
)


def test_post_keeps_all_paragraphs_and_excludes_comments(dom_page):
    dom_page.set_content("""<article role="article"><a role="link" href="https://www.facebook.com/alice">Alice Example</a>
      <a href="/groups/g/posts/11">1h</a><div dir="auto">First full paragraph.</div>
      <div dir="auto">Second full paragraph.</div><div dir="auto">Third full paragraph.</div>
      <article role="article" aria-label="Comment by Bob"><div dir="auto">This is a comment, not the post.</div></article>
      <span aria-label="1.2K comments"></span></article>""")
    post = parse_modern_post(dom_page.query_selector("article"), dom_page)
    assert post is not None
    assert (
        post.content
        == "First full paragraph.\nSecond full paragraph.\nThird full paragraph."
    )
    assert post.comments_count == 1200


def test_post_expands_see_more_and_keeps_query_identity(dom_page):
    dom_page.set_content("""<article role="article"><a role="link" href="https://www.facebook.com/alice">Alice Example</a>
      <a href="https://www.facebook.com/permalink.php?story_fbid=123&id=456">1h</a>
      <div dir="auto" id="body">A truncated paragraph.</div>
      <button onclick="document.getElementById('body').textContent='The entire expanded paragraph.';this.remove()">See more</button></article>""")
    post = parse_modern_post(dom_page.query_selector("article"), dom_page)
    assert post is not None
    assert post.content == "The entire expanded paragraph."
    assert "story_fbid=123" in post.url
    assert not post.content_truncated


def test_distinct_comment_ids_survive_sqlite(dom_page, tmp_path):
    comments = []
    for post_id, comment_id in [(11, 111), (22, 222)]:
        dom_page.set_content(f"""<article role="article"><strong>Alice Example</strong>
          <a role="link" href="https://www.facebook.com/alice">Alice Example</a>
          <div dir="auto">Thank you very much!</div><a href="/posts/{post_id}?comment_id={comment_id}">1h</a></article>""")
        comments.append(parse_modern_comment(dom_page.query_selector("article")))
    assert all(comments)
    assert comments[0].id != comments[1].id
    result = ScrapeResult(
        group=GroupInfo(id="g", name="Group", url="https://www.facebook.com/groups/g"),
        scraped_at=datetime.now(),
        date_range=DateRange(since="2026-09-01", until="2026-09-20"),
        posts=[
            Post(id=str(i), author=Author(name="Author"), content="Post", comments=[c])
            for i, c in zip([11, 22], comments)
        ],
    )
    database = tmp_path / "data.db"
    export_to_sqlite(result, database)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT count(*) FROM comments").fetchone()[0] == 2


def test_fallback_comment_ids_include_post(dom_page):
    dom_page.set_content(
        '<article role="article"><strong>Alice Example</strong><div dir="auto">Thank you very much!</div></article>'
    )
    element = dom_page.query_selector("article")
    first = parse_modern_comment(element, post_id="11")
    second = parse_modern_comment(element, post_id="22")
    assert first.id != second.id


def test_calendar_until_includes_entire_day():
    start, end = calculate_date_range(
        ScrapeOptions(since="2026-09-20", until="2026-09-20")
    )
    assert end - start == timedelta(days=1)


def test_reversed_dates_rejected():
    with pytest.raises(ValueError, match="since"):
        calculate_date_range(ScrapeOptions(since="2026-09-20", until="2026-09-01"))


def test_yesterday_preserves_clock_time():
    assert parse_timestamp("Yesterday at 3:45 PM").strftime("%H:%M") == "15:45"


@pytest.mark.parametrize(
    "arguments",
    [
        ["--format", "sqlite"],
        ["--format", "csv"],
        ["--since", "bad"],
        ["--since", "2026-09-20", "--until", "2026-09-01"],
    ],
)
def test_invalid_options_fail_before_auth_or_scrape(arguments):
    with (
        patch("forage.cli.session_exists", return_value=True) as session,
        patch("forage.cli.scrape_group") as scrape,
    ):
        result = CliRunner().invoke(main, ["scrape", "example", *arguments])
    assert result.exit_code == 2
    session.assert_not_called()
    scrape.assert_not_called()


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission contract")
def test_login_state_is_owner_only(tmp_path):
    state = tmp_path / "session" / "storage_state.json"
    fake_context = MagicMock()

    def storage_state(path=None):
        if path:
            Path(path).write_text('{"cookies": [], "origins": []}')
        return {"cookies": [], "origins": []}

    fake_context.storage_state.side_effect = storage_state
    playwright = MagicMock()
    playwright.chromium.launch.return_value.new_context.return_value = fake_context
    old_umask = os.umask(0o022)
    try:
        with (
            patch("forage.auth.sync_playwright") as manager,
            patch("forage.auth.is_logged_in_page", return_value=True),
            patch("builtins.input", return_value=""),
        ):
            manager.return_value.__enter__.return_value = playwright
            login(state.parent)
        assert state.stat().st_mode & 0o777 == 0o600
        assert state.parent.stat().st_mode & 0o777 == 0o700
    finally:
        os.umask(old_umask)


def marketplace_pages():
    page, detail = MagicMock(), MagicMock()
    page.url = "https://www.facebook.com/marketplace/wilmington/search/"
    page.inner_text.return_value = "Search listings"
    page.content.return_value = '"buyLocation":{"latitude":34.1,"longitude":-77.9}'
    context = MagicMock()
    context.new_page.side_effect = [page, detail]
    return page, detail, context


def test_marketplace_limit_counts_accepted_results():
    page, detail, context = marketplace_pages()
    elements = []
    for identity in [1, 2, 3]:
        element = MagicMock()
        element.get_attribute.return_value = f"/marketplace/item/{identity}/"
        element.inner_text.return_value = f"$100\nComputer {identity}\nWilmington, NC"
        elements.append(element)
    page.query_selector_all.return_value = elements
    detail.content.side_effect = [
        '{"id":"1","location":{"latitude":33.7,"longitude":-78.9}}',
        '{"id":"2","location":{"latitude":34.1,"longitude":-77.9}}',
        '{"id":"3","location":{"latitude":34.1,"longitude":-77.9}}',
    ]
    with (
        patch("forage.scraper.sync_playwright"),
        patch("forage.scraper.create_browser_context", return_value=context),
        patch("forage.scraper.is_logged_in_page", return_value=True),
    ):
        result = search_marketplace("computer", MarketplaceOptions(limit=2))
    assert [listing.id for listing in result.listings] == ["2", "3"]
    assert result.diagnostics.rejected_count == 1
    assert result.diagnostics.stop_reason == "limit"


def test_marketplace_auth_checked_before_results_wait():
    page, detail, context = marketplace_pages()
    page.wait_for_selector.side_effect = PlaywrightTimeoutError("no results")
    with (
        patch("forage.scraper.sync_playwright"),
        patch("forage.scraper.create_browser_context", return_value=context),
        patch("forage.scraper.is_logged_in_page", return_value=False),
    ):
        with pytest.raises(AuthenticationError):
            search_marketplace("computer", MarketplaceOptions())
    page.wait_for_selector.assert_not_called()


def test_marketplace_verified_empty_result():
    page, detail, context = marketplace_pages()
    page.inner_text.return_value = "No results found"
    page.wait_for_selector.side_effect = PlaywrightTimeoutError("no results")
    page.query_selector_all.return_value = []
    with (
        patch("forage.scraper.sync_playwright"),
        patch("forage.scraper.create_browser_context", return_value=context),
        patch("forage.scraper.is_logged_in_page", return_value=True),
    ):
        result = search_marketplace("computer", MarketplaceOptions())
    assert result.listings == []
    assert result.diagnostics.stop_reason == "empty"


def test_missing_group_feed_is_an_error():
    page = MagicMock()
    page.url = "https://www.facebook.com/groups/example"
    page.title.return_value = "Example | Facebook"
    page.inner_text.return_value = "A changed layout"
    page.query_selector.return_value = None
    context = MagicMock()
    context.new_page.return_value = page
    with (
        patch("forage.scraper.sync_playwright"),
        patch("forage.scraper.create_browser_context", return_value=context),
        patch("forage.scraper.is_logged_in_page", return_value=True),
    ):
        with pytest.raises(RuntimeError, match="feed"):
            scrape_group("example", ScrapeOptions(limit=1))


def test_unexpanded_body_reports_truncation(dom_page):
    dom_page.set_content(
        '<article role="article"><strong>Alice Example</strong><div dir="auto">A partial post. See more</div><button>See more</button></article>'
    )
    post = parse_modern_post(dom_page.query_selector("article"), dom_page)
    assert post is not None
    assert post.content_truncated


def test_saved_export_needs_no_authentication(tmp_path):
    result = ScrapeResult(
        group=GroupInfo(id="g", name="Group", url="https://www.facebook.com/groups/g"),
        scraped_at=datetime.now(),
        date_range=DateRange(since="2026-09-01", until="2026-09-20"),
    )
    source = tmp_path / "saved.json"
    source.write_text(result.model_dump_json())
    target = tmp_path / "saved.db"
    with patch("forage.cli.session_exists") as auth:
        response = CliRunner().invoke(
            main, ["export", str(source), "--format", "sqlite", "--output", str(target)]
        )
    assert response.exit_code == 0, response.output
    auth.assert_not_called()
    with sqlite3.connect(target) as connection:
        assert connection.execute("SELECT id FROM groups").fetchone() == ("g",)


def test_doctor_does_not_read_session_or_start_browser(tmp_path):
    import json

    state = tmp_path / "storage_state.json"
    state.write_text("not valid JSON; doctor must not read it")
    state.chmod(0o600)
    with patch("forage.cli.sync_playwright") as manager:
        chromium = manager.return_value.__enter__.return_value.chromium
        chromium.executable_path = str(state)
        result = CliRunner().invoke(main, ["doctor", "--session-dir", str(tmp_path)])
        chromium.launch.assert_not_called()
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["session_validity"] == "not_checked"


def test_marketplace_candidate_bound_still_excludes_distant_results():
    page, detail, context = marketplace_pages()
    element = MagicMock()
    element.get_attribute.return_value = "/marketplace/item/1/"
    element.inner_text.return_value = "$100\nComputer 1\nDistant City"
    page.query_selector_all.return_value = [element]
    detail.content.return_value = (
        '{"id":"1","location":{"latitude":33.7,"longitude":-78.9}}'
    )
    with (
        patch("forage.scraper.sync_playwright"),
        patch("forage.scraper.create_browser_context", return_value=context),
        patch("forage.scraper.is_logged_in_page", return_value=True),
    ):
        result = search_marketplace(
            "computer", MarketplaceOptions(limit=2, max_candidates=1)
        )
    assert not result.listings
    assert result.diagnostics.stop_reason == "candidate_limit"
    assert result.diagnostics.rejected_count == 1


def test_post_preserves_inline_link_text_and_line_breaks(dom_page):
    dom_page.set_content(
        '<article role="article"><strong>Alice Example</strong><div dir="auto">Read <a href="https://example.com">this reference</a>.<br>Second line.</div></article>'
    )
    post = parse_modern_post(dom_page.query_selector("article"), dom_page)
    assert post is not None
    assert post.content == "Read this reference.\nSecond line."


@pytest.mark.parametrize(
    "target_location",
    [
        '"location":{"latitude":33.7,"longitude":-78.9}',
        '"title":"No verifiable coordinates"',
    ],
)
def test_marketplace_never_uses_another_listings_coordinates(target_location):
    from forage.scraper import _marketplace_listing_within_radius

    html = (
        '<script type="application/json">{"recommendation":{"id":"other","location":{"latitude":34.1,"longitude":-77.9}},"listing":{"id":"wanted",'
        + target_location
        + "}}</script>"
    )
    assert not _marketplace_listing_within_radius(
        html, (34.1, -77.9), 40, listing_id="wanted"
    )


def test_expanding_feed_parses_each_permalink_once(dom_page):
    def article(identity):
        return f'<article role="article"><a href="https://www.facebook.com/alice" role="link">Alice Example</a><a href="/groups/g/posts/{identity}">1h</a><div dir="auto">Full content for post {identity}.</div></article>'

    dom_page.set_content('<div role="feed">' + article(11) + "</div>")
    context = MagicMock()
    context.new_page.return_value = dom_page

    def expand(*args, **kwargs):
        if dom_page.query_selector_all('[role="article"]').__len__() == 1:
            dom_page.locator('[role="feed"]').evaluate(
                "(node, html) => node.insertAdjacentHTML('beforeend', html)",
                article(22),
            )

    with (
        patch("forage.scraper.sync_playwright"),
        patch("forage.scraper.create_browser_context", return_value=context),
        patch("forage.scraper.navigate_with_retry"),
        patch("forage.scraper.human_delay"),
        patch.object(dom_page, "wait_for_function", side_effect=expand),
        patch("forage.scraper.parse_modern_post", wraps=parse_modern_post) as parse,
    ):
        result = scrape_group("g", ScrapeOptions(limit=2, skip_comments=True))
    assert [post.id for post in result.posts] == ["11", "22"]
    assert parse.call_count == 2
