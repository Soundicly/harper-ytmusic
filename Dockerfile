FROM python:3.11.4-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends git \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

ENV REDIS_URL=redis://localhost
ENV PORT=2005
EXPOSE 2005

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "2005"]
