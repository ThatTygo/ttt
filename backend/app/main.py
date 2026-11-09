from fastapi import FastAPI

from .routers import auth, columns, counter, members, users

app = FastAPI(title="Trauma Tram Tellers", docs_url=None, redoc_url=None, openapi_url=None)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(members.router)
app.include_router(columns.router)
app.include_router(counter.router)


@app.get("/api/health")
def health():
    return {"ok": True}
