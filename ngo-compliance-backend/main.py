from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "NGO Compliance API running"}