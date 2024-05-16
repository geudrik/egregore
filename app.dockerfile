FROM python:3.10
WORKDIR /app

COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app /app

# If running behind a proxy (nginx, traefik, etc), add the --proxy-headers arg below
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]