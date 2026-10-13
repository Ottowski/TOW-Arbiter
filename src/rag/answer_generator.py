import re
from typing import List

# Answer generator for the RAG pipeline. Formats retrieved rules as readable answers or LLM prompts.
class AnswerGenerator:
    """Format retrieved rules as a readable answer or an LLM-ready prompt."""
# This class is responsible for generating answers and prompts based on retrieved context documents.
    def generate_prompt(self, query: str, context_documents: List[str]) -> str:
        """Build the prompt that would be sent to an LLM."""
        if not context_documents:
            return "No relevant information found in the knowledge base."

        context = "\n\n".join(
            self.normalize_markdown(document) for document in context_documents[:3]
        )
        return f"""Based on the following Warhammer: The Old World rules, answer the question:

Question: {query}

Relevant Rules:
{context}

Answer:"""
# Generate a simple answer by combining the top matched context documents.
    def simple_answer(self, documents: List[str]) -> str:
        """Combine the top three matched chunks into a readable block."""
        if not documents:
            return "No relevant information found."
        # Initialize a list to hold the answer parts.#
        answer_parts = []
        for index, document in enumerate(documents[:3], 1):
            if index > 1:
                answer_parts.append("\n\n---\n\n")
            answer_parts.append(self.normalize_markdown(document))
        return "".join(answer_parts)
    
# Normalize markdown text for better readability.
    def normalize_markdown(self, text: str) -> str:
        """Restore line breaks in flattened markdown tables, headings, and unit stats."""
        if not text:
            return ""

        normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        normalized = re.sub(r"\|\s+\|", "|\n|", normalized)
        normalized = re.sub(r"(?<!\n)(#{2,3}\s)", r"\n\1", normalized)
        normalized = re.sub(
            r"^(#{2,3}\s[^\n|]+?)\s+(\|\s*[^\n]+)$",
            r"\1\n\2",
            normalized,
            flags=re.MULTILINE,
        )

        labels = [
            "Unit Category:",
            "Troop Type:",
            "Base Size:",
            "Unit Size:",
            "Equipment:",
            "Special Rules:",
            "Optional Rules:",
        ]
        label_pattern = "|".join(re.escape(label) for label in labels)
        normalized = re.sub(
            rf"(?<!\n)({label_pattern})", r"\n\1", normalized
        )
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip()
