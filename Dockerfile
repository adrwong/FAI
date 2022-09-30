FROM python:3.8-slim

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install tk --yes

COPY . .
ENTRYPOINT [ "python" ]
