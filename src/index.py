from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from functools import partial
from http import HTTPStatus

import httpx
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Route

logging.basicConfig(level=logging.INFO)


@dataclass(slots=True)
class RequestDTO:
    url: str = ""

    def validate_url(self) -> bool:
        """Check if url is valid"""

        url_regex = (
            r"^https?://(www\.)?"
            r"[-a-zA-Z0-9@:%._+~#=]{1,256}"
            r"\.[a-zA-Z0-9()]{1,6}"
            r"\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)"
        )

        # Check url format
        if re.match(url_regex, self.url):
            return True
        else:
            return False

    def add_trailing_slash_to_url(self) -> str:
        """Add trailing slash to url."""

        if self.url[-1] == "/":
            return self.url
        else:
            return self.url + "/"

    def __post_init__(self) -> None:
        if not self.url:
            raise ValueError("Empty URL.")

        if not self.validate_url():
            raise ValueError("Invalid URL.")
        self.url = self.add_trailing_slash_to_url()


@dataclass(slots=True)
class ResponseDTO:
    html: str
    text: str = ""

    def html_to_text(self) -> str:
        """Convert HTML to text."""

        soup = BeautifulSoup(self.html, features="html.parser")
        text = soup.get_text()

        # Remove extra vertical whitespace
        text = re.sub(r"\n\s*\n", "\n\n", text)
        return text

    def __post_init__(self) -> None:
        self.text = self.html_to_text()


async def get_html(url: str) -> str:
    """Get HTML from URL."""

    async with httpx.AsyncClient(follow_redirects=True, max_redirects=10) as client:
        try:
            response = await client.get(url)
        except httpx.HTTPError:
            error_message = f"Failed to get HTML from {url}."
            logging.error(error_message)
            return error_message

    if response.status_code != HTTPStatus.OK:
        error_message = f"Failed to get HTML from {url}."
        logging.error(error_message)
        return error_message

    return response.text


async def index(_: Request, env: Environment) -> HTMLResponse:
    """Index page."""
    return HTMLResponse(env.get_template("index.html").render(code=""))


async def html_to_text(request: Request, env: Environment) -> HTMLResponse:
    """Service page."""

    url = request.query_params.get("url")

    try:
        request_dto = RequestDTO(url)
    except ValueError as e:
        return HTMLResponse(
            env.get_template("index.html").render(url=url, code=str(e)),
            status_code=HTTPStatus.BAD_REQUEST,
        )

    response_dto = ResponseDTO(await get_html(request_dto.url))
    template = env.get_template("index.html")

    return HTMLResponse(template.render(url=url, code=response_dto.text))


env = Environment(loader=FileSystemLoader("src"))

middleware = [Middleware(CORSMiddleware, allow_origins=["*"])]

routes = [
    Route("/", partial(index, env=env)),
    Route("/html-to-text", partial(html_to_text, env=env)),
]
app = Starlette(debug=True, routes=routes)
