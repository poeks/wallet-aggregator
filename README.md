# wallet-aggregator
Aggrate your crypto holdings and display them in a single overview.

## Development

This project is a mono repo where both the frontend and the backend reside.

### Frontend
React is used for the frontend.

Run `npm install` in the `client` directory.

To start the frontend:
```
npm start
```

### Backend
FastAPI is used for the backend.

Create a virtual environment in the `api` directory and install the requirement files:

    - `pip install -r requirements.txt`
    - `pip install -r requirements-dev.txt`.

To start the FastAPI backend:
```
uvicorn main:app --reload --port 3001
```

The backend can also be run in a container. First build the image:

```
docker build -f Dockerfile -t api .
```

Then run in the root of `api`:
```
docker container run -dit -p 80:80 -v "$(pwd)/.env:/code/.env" --name backend api
```

Install [pre-commit](https://pre-commit.com/) and the hooks for your convenience.
