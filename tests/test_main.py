from http import HTTPStatus
from unittest.mock import MagicMock, patch

import httpx
import pytest

from src import __main__ as main


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.example.com", True),
        ("http://example.com", True),
        ("www.example.com", False),
        ("example.com", False),
        ("https://example", False),
    ],
)
def test_check_url(url, expected):
    assert main.check_url(url) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://example.com", "http://example.com/"),
        ("http://example.com/", "http://example.com/"),
        ("http://example.com/page", "http://example.com/page/"),
    ],
)
def test_add_trailing_slash(url, expected):
    assert main.add_trailing_slash(url) == expected


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        ("<p>Hello world</p>", "Hello world"),
        ("<h1>Title</h1><p>Paragraph text</p>", "TitleParagraph text"),
        ("<b>Bold</b> text", "Bold text"),
        ('<a href="/">Link</a>', "Link"),
        ("<div>Div content</div>", "Div content"),
    ],
)
def test_html_to_text(html, expected):
    assert main.html_to_text(html) == expected


def mock_async_client(mock_response):
    # Returns a MagicMock object mocking httpx.AsyncClient
    # Usage:
    #   client = mock_async_client(mock_response)
    #   html = await get_html('https://example.com', client)
    mock_client = MagicMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    return mock_client


@pytest.mark.parametrize(
    ("url", "status_code", "expected"),
    [
        ("https://example.com", HTTPStatus.OK, "<html>Example</html>"),
        (
            "https://example.com/404",
            HTTPStatus.NOT_FOUND,
            "Failed to get HTML from https://example.com/404.",
        ),
    ],
)
@pytest.mark.asyncio()
async def test_get_html(url, status_code, expected):
    mock_response = httpx.Response(status_code=status_code, text=expected)
    with patch(
        "src.__main__.httpx.AsyncClient", return_value=mock_async_client(mock_response)
    ):
        html = await main.get_html(url)
        assert html == expected
