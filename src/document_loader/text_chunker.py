import re
from typing import List


class TextChunker:
    """Splits rule text into chunks at Markdown heading boundaries."""

    # Initialize the text chunker.
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        if len(text) <= chunk_size:
            return [text]
        
        # Ensure the overlap is non-negative.
        overlap = max(0, overlap)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        sections = re.split(r"(\n#{2,3}\s+[^\n]+\n)", text)

        # Split the text into sections based on Markdown headings.
        chunks = []
        current_chunk = ""

        # Iterate through each section and build chunks based on the specified chunk size and overlap.
        for section in sections:
            if "|" in section:
                # If the section contains a table, strip only carriage return and newline characters.
                section = section.strip("\r\n")
            else:
                section = section.strip()

            if not section:
                continue
            # If the current chunk exceeds the chunk size, start a new chunk.
            if len(current_chunk) + len(section) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = section
            else:
                # Otherwise, add the section to the current chunk.
                if current_chunk:
                    current_chunk += "\n\n" + section
                else:
                    current_chunk = section
        # Append any remaining text as the last chunk.
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks
