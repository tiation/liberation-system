from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import resources, truth, mesh, system

app = FastAPI(
    title="Liberation System API",
    description="API for the $19 Trillion Economic Reform",
    version="1.0.0"
)

# Middleware for handling CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(resources.router, prefix="/api/v1/resources", tags=["Resources"])
app.include_router(truth.router, prefix="/api/v1/truth", tags=["Truth"])
app.include_router(mesh.router, prefix="/api/v1/mesh", tags=["Mesh"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Liberation System API"}
