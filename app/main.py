from fastapi import FastAPI

app = FastAPI(title="Car Rental")


@app.get("/health")
def health():
    return {"status": "ok"}
