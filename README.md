# harper-ytmusic

This is a microservice to get data from the youtube music api for our harper service.

## Usage

First of all, you'll need to login to a Youtube Premium account. For that, run the following commands:

```bash
python -m venv .venv
pip install -r requirements.txt
ytmusicapi oauth
```

You can now run the server with:

```bash
uvicorn main:app --reload
```

## Docker

To build an image, run:

```bash
docker build -t harper-yt .
```

**Note**: You'll need to login to a Youtube Premium account before running the container.
