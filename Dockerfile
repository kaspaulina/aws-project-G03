FROM python:3.8-slim-buster

RUN pip3 install Flask boto3 pillow
RUN pip3 install python-dotenv

COPY templates/ templates/
COPY app.py app.py
COPY .env .env


CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]