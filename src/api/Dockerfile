FROM python:3.7-stretch
WORKDIR /usr/src/app
RUN apt-get update \
    && apt-get clean
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED True
ENV FLASK_ENV development
ENV GOOGLE_APPLICATION_CREDENTIALS /usr/src/app/service-account-file.json
ENV PORT 5000
COPY . .
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app