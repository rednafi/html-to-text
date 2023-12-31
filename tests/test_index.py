from http import HTTPStatus
from unittest.mock import MagicMock, patch

import httpx
import pytest
from starlette.testclient import TestClient

from src import index


def mock_async_client(mock_response):
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
        "src.index.httpx.AsyncClient", return_value=mock_async_client(mock_response)
    ):
        html = await index.get_html(url)
        assert html == expected


class TestRequestDTO:
    def setup_class(self):
        self.url_with_slash = "http://www.example.com/"
        self.url_without_slash = "http://www.example.com"
        self.url_invalid = "http://www.example"

    def test_validate_url_valid(self):
        request = index.RequestDTO(url=self.url_with_slash)
        assert request.validate_url() is True

    def test_post_init_empty_url(self):
        with pytest.raises(ValueError, match="Empty URL."):
            index.RequestDTO()

    def test_post_init_invalid_url(self):
        with pytest.raises(ValueError, match="Invalid URL."):
            index.RequestDTO(url=self.url_invalid)


class TestResponseDTO:
    def setup_class(self):
        self.html = "<html><body><p>Hello World</p></body></html>"
        self.text = "Hello World"

    def test_html_to_text(self):
        response = index.ResponseDTO(html=self.html)
        assert response.html_to_text() == self.text

    def test_post_init(self):
        response = index.ResponseDTO(html=self.html)
        assert response.text == self.text


def test_index():
    with TestClient(index.app) as client:
        response = client.get("/")
        assert response.status_code == HTTPStatus.OK
        assert "html to text" in response.text.lower()


def test_html_to_text():
    with TestClient(index.app) as client:
        response = client.get("/html-to-text?url=http://example.com")
        assert response.status_code == HTTPStatus.OK
        assert "html to text" in response.text.lower()


def test_html_to_text_invalid():
    with TestClient(index.app) as client:
        response = client.get("/html-to-text?url=invalid")
        assert response.status_code == HTTPStatus.BAD_REQUEST
