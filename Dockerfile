FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY ./main.py /app/

CMD [ "python", "main.py" ]