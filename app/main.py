from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from mangum import Mangum

from api.endpoints import items

# API Application object
app = FastAPI()

## API Routes
app.include_router(items.router, prefix="/v1", tags=["items"])

## API Spec
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SAM API",
        version="0.0.1",
        routes=app.routes
    )
    openapi_schema["components"]["securitySchemes"] = {
        "Authorization": {
            "type": "apiKey",
            "name": "x-api-key",
            "in": "header",
        }
    }
    openapi_schema["servers"] = [
        {"url": "/dev"},
        {"url": "/stage"},
        {"url": "/prod"}
    ]

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi

# AWS Lambda handler
handler = Mangum(app=app)

# Self contained application
if __name__ == "__main__":
    # Run with uvicorn: uvicorn main:app --reload
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
