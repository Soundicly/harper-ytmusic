FROM python:3.11.4-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

ENV PORT=2005
EXPOSE 2005

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "2005"]
