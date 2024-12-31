from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from example_flow.types import Image  # Import Image model from our types module
from dotenv import load_dotenv
import os
import requests

# Load the environment variables from the .env file
load_dotenv()

# Get the Unsplash credentials from environment variables
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
if not UNSPLASH_ACCESS_KEY:
    raise ValueError("Unsplash Access Key is not set in the .env file.")

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
            "client_id": UNSPLASH_ACCESS_KEY  # Unsplash uses the Access Key as the client_id
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
                width = image_data["width"]
                height = image_data["height"]
                alt = image_data["alt_description"] or image_data["description"] or query

                # Create and return Image object
                return Image(
                    src=src,
                    alt=alt,
                    width=width,
                    height=height
                )
            else:
                raise ValueError(f"No images found for query: {query}")
        else:
            raise ValueError(f"Error fetching image: {response.status_code} - {response.text}")