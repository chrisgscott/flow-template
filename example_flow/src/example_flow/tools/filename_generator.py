from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FilenameInput(BaseModel):
    """Input schema for FilenameGeneratorTool."""
    slug: str = Field(..., description="The slug to use for generating the filename.")

class FilenameGeneratorTool(BaseTool):
    """Tool for generating unique filenames for spoke posts."""
    
    name: str = "filename_generator"
    description: str = "Generates a unique filename for a spoke post based on its slug"
    args_schema: Type[BaseModel] = FilenameInput
    
    def _run(self, slug: str) -> str:
        """Generate a unique filename for a spoke post.
        
        Args:
            slug: The slug of the spoke post
            
        Returns:
            str: The generated filename
        """
        logger.info(f"Generating filename for slug: {slug}")
        filename = f"outputs/{slug}.md"
        logger.info(f"Generated filename: {filename}")
        return filename
    
    async def _arun(self, slug: str) -> str:
        """Async version of _run"""
        logger.info(f"Async generating filename for slug: {slug}")
        result = self._run(slug)
        logger.info(f"Async generated filename: {result}")
        return result
