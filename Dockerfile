FROM python:3.7
EXPOSE 8000

COPY . /app
WORKDIR /app

RUN pip install pipenv

RUN pipenv install --system --deploy

WORKDIR /app/src
CMD exec gunicorn conf.wsgi:application --bind 0.0.0.0:8000 --workers 3
