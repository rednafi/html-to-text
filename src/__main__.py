from __future__ import annotations

import logging
import re
from functools import partial
from http import HTTPStatus

import httpx
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Route

logging.basicConfig(level=logging.INFO)


def check_url(url: str) -> bool:
    """Check if url is valid"""

    url_regex = (
        r"^https?://(www\.)?"
        r"[-a-zA-Z0-9@:%._+~#=]{1,256}"
        r"\.[a-zA-Z0-9()]{1,6}"
        r"\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)"
    )

    # Check url format
    if re.match(url_regex, url):
        return True
    else:
        return False


def add_trailing_slash(url: str) -> str:
    """Add trailing slash to url"""

    if url[-1] != "/":
        url += "/"

    return url


async def get_html(url: str) -> str:
    """Get HTML from URL"""

    async with httpx.AsyncClient() as client:
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


def html_to_text(html: str) -> str:
    """Convert HTML to text"""

    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()

    return text


async def index(_: Request, env: Environment) -> HTMLResponse:
    """Index page"""
    return HTMLResponse(env.get_template("index.html").render(code=""))


async def service(request: Request, env: Environment) -> HTMLResponse:
    """Index page"""

    url = request.query_params.get("url")
    url = add_trailing_slash(url)
    template = env.get_template("index.html")

    if not url:
        return HTMLResponse(
            template.render(url=url, code="Empty URL."),
            status_code=HTTPStatus.BAD_REQUEST,
        )

    if not check_url(url):
        return HTMLResponse(
            template.render(url=url, code="Invalid URL."),
            status_code=HTTPStatus.BAD_REQUEST,
        )

    html = await get_html(url)
    return HTMLResponse(template.render(url=url, code=html_to_text(html)))


env = Environment(loader=FileSystemLoader("src"))
routes = [
    Route("/", partial(index, env=env)),
    Route("/html-to-text", partial(service, env=env)),
]
app = Starlette(debug=True, routes=routes)
