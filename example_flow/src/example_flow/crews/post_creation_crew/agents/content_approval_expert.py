from crewai import Agent
import os

class ContentApprovalExpert(Agent):
    """Content Approval Expert Agent"""

    def _execute(self, task):
        """Execute the task"""
        # Extract data from task
        spoke_post = task.inputs.get("spoke_post", {})
        slug = task.inputs.get("slug", "")
        output_file = f"outputs/{slug}.md"

        # Create frontmatter
        frontmatter = [
            "---",
            f"title: {spoke_post['title']}",
            f"description: {spoke_post.get('description', '')}",
            f"hub: {spoke_post['hub']}",
            f"slug: {slug}",
            "---\n"
        ]

        # Write the file
        os.makedirs("outputs", exist_ok=True)
        with open(output_file, "w") as f:
            # Write frontmatter
            f.write("\n".join(frontmatter))
            
            # Write content
            f.write(task.inputs.get("content", ""))

        return {
            "title": spoke_post["title"],
            "description": spoke_post.get("description", ""),
            "content": task.inputs.get("content", ""),
            "image": task.inputs.get("image", None),
            "faqs": task.inputs.get("faqs", None)
        }
