FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    tk-dev

RUN pip install tkinter

WORKDIR /app

COPY . .

CMD ["python", "main.py"]
