FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN apt-get update

RUN pip install -r requirements.txt

EXPOSE 5000

CMD [ "python", "run.py" ]

