import uvicorn
from .server import app


def main():
    uvicorn.run(app=app, host="0.0.0.0", port=8080)


main()
