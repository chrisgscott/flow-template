from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from types import Image  # Assuming your Image model is imported from types.py
from dotenv import load_dotenv
import os
import requests

# Load the environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
if not UNSPLASH_API_KEY:
    raise ValueError("Unsplash API key is not set in the .env file.")

# Define the input schema for the tool
class UnsplashImageInput(BaseModel):
    """Input schema for UnsplashImageTool."""
    query: str = Field(..., description="The search query to find images.")
    per_page: int = Field(1, description="Number of images to retrieve per page.")
    page: int = Field(1, description="Page number for pagination.")

# Define the custom tool subclassing BaseTool
class UnsplashImageTool(BaseTool):
    name: str = "unsplash"
    description: str = "Fetches an image from Unsplash based on a search query and returns an Image object."
    args_schema: Type[BaseModel] = UnsplashImageInput

    def _run(self, query: str, per_page: int = 1, page: int = 1) -> Image:
        # Unsplash API endpoint
        API_URL = "https://api.unsplash.com/search/photos"

        # Parameters for the API request
        params = {
            "query": query,
            "per_page": per_page,
            "page": page,
            "client_id": UNSPLASH_API_KEY
        }

        # Make the API request
        response = requests.get(API_URL, params=params)
        
        # Handle response
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                # Extract image details for the first result
                image_data = data["results"][0]
                src = image_data["urls"]["regular"]
                alt = image_data["alt_description"] or "No description available"
                width = image_data["width"]
                height = image_data["height"]
                
                # Return an Image object
                return Image(src=src, alt=alt, width=width, height=height)
            else:
                raise ValueError("No images found for the query.")
        else:
            raise ValueError(f"Error: {response.status_code}, {response.text}")