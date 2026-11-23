
from app.agent.base import Tool
from app.generation.chain import answer_question


class DocumentSearchTool(Tool):

    @property
    def name(self):
        return "document_search"

    @property
    def description(self):
        return (
            "Searches internal company documents and answers "
            "questions using retrieved document content. "
            "Use for company policies, employee benefits, "
            "leave policies, internal procedures, and "
            "organization-specific information."
        )

    def execute(self, tool_input: str):

        try:
            result = answer_question(tool_input)

            return {
                "success": True,
                "answer": result["answer"],
                "sources": result["sources"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
