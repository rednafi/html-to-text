FROM python:3.12-rc-alpine


# Set working directory.
WORKDIR /code

# Copy dependencies.
COPY requirements.txt /code/

# Install dependencies.
RUN pip install -r requirements.txt

# Copy project.
COPY . /code/

ENTRYPOINT ["uvicorn", "src.index:app", "--host", "0.0.0.0", "--port", "5000"]
