from fastapi import FastAPI

app = FastAPI(title="test")


@app.get("/")
def root():
    return {"project": "test"}


@app.get("/health")
def health():
    return {"status": "ok"}
