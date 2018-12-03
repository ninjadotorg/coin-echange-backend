FROM python:3.7
EXPOSE 8000

COPY . /app
WORKDIR /app

RUN pip install pipenv

RUN pipenv install --system --deploy

WORKDIR /app/src

ENV DJANGO_SETTINGS_MODULE="conf.settings.local"
ENV GOOGLE_APPLICATION_CREDENTIALS="deployments/coin-exchange-storage.json"

CMD exec gunicorn conf.wsgi:application --bind 0.0.0.0:8000 --workers 3
