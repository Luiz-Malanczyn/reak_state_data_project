FROM python:3.13-slim-alphine

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install

COPY . .

CMD ["python", "main.py"]
