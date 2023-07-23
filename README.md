<div align="center">

<h1>HTML to TEXT</h1>
<strong>>> <i>Extract pure text from any webpage</i> <<</strong>

&nbsp;

</div>

## Why

LLMs with huge context windows like [Claude 2] enable the idea of pasting large blobs of
texts and asking questions about them. Often, I want to copy the entire content of a
webpage and pipe it into a chat window. One specific use case is when I want to grok
Python PEPs with the help of an LLM. This little [ASGI] tool allows you to parse the HTML
content of any publicly available page and turn it into pure text that's ingestible by a
language model.

## Exploration

* Go to [html-text.rednafi.com] and paste a publicly accessible page URL. Then click
**Submit** and you'll see that the parsed text content will appear in the adjacent text
box:

    ![screenshot-a]

* Copy the text content by clicking on the **Copy** button.

* Click **Clear** if you need a blank canvas.

## Development

* Ensure that docker is installed on your system.
* Clone the repo and head over to the root directory.
* Build and run the service locally:

    ```sh
    docker build -t html-to-text . \
        && docker run -p "5001:5000" html-to-text
    ```
* Head over to [http://localhost:5001] on your browser and explore the app.

* Apply linter:

    ```sh
    make lint
    ```

* Run the tests

    ```sh
    make test
    ```

## Deployment

The app is built with Python 3.12 and is automagically deployed to [fly.io] via GitHub
Action.


<div align="center">
<i> ✨ 🍰 ✨ </i>
</div>

[screenshot-a]: https://github.com/rednafi/html-to-text/assets/30027932/20bb63bd-c4a8-48bf-8cda-d83857548b48
[http://localhost:5001]: http://localhost:5001
[html-text.rednafi.com]: https://html-text.rednafi.com
[fly.io]: https://fly.io
[claude 2]: https://www.anthropic.com/index/claude-2
[asgi]: https://asgi.readthedocs.io/en/latest/
