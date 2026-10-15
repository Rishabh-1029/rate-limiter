from fastapi import FastAPI

# App Description

app = FastAPI(
    title = "Rate Limmiter", 
    description = "Configurable Rate Limit Infrastructure", 
    version = "0.1.0"
)

# Health Check endpoint

@app.get("/health")
def health_check():
    return {"status" : "OK"}