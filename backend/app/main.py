"""
FinSight — FastAPI Application Entry Point

This is the main module of the FinSight backend. It creates the FastAPI
application instance and defines the API endpoints.

Key concepts demonstrated:
    - Creating a FastAPI application (which is a Python class instance)
    - Defining routes using decorators (@app.get)
    - Returning structured responses as Python dictionaries (FastAPI
      automatically converts them to JSON)
"""

from fastapi import FastAPI

# Create an instance of the FastAPI class.
# This object IS your web application. All routes are registered on it.
# Think of it as: app = FastAPI() creates a "web server object" that
# knows how to handle HTTP requests.
app = FastAPI(
    title="FinSight API",
    description="AI-powered FinTech enterprise application",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """
    Health check endpoint.

    This is a simple endpoint that returns the current status of the API.
    It's useful for:
        - Monitoring tools to verify the service is running
        - Load balancers to check if the server can handle requests
        - Developers to quickly test if the API is reachable

    The @app.get("/health") decorator tells FastAPI:
        1. Listen for HTTP GET requests
        2. At the URL path "/health"
        3. When a request arrives, call this function
        4. Return the result as a JSON response

    Returns:
        dict: A dictionary with status and service name.
              FastAPI automatically serializes this to JSON.
    """
    return {
        "status": "healthy",
        "service": "FinSight API",
        "version": "0.1.0",
    }
