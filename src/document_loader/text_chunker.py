import re
from typing import List


class TextChunker:
    """Splits rule text into chunks at Markdown heading boundaries."""

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        if len(text) <= chunk_size:
            return [text]

        overlap = max(0, overlap)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        sections = re.split(r"(\n#{2,3}\s+[^\n]+\n)", text)

        chunks = []
        current_chunk = ""

        for section in sections:
            if "|" in section:
                section = section.strip("\r\n")
            else:
                section = section.strip()
            if not section:
                continue

            if len(current_chunk) + len(section) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = section
            else:
                if current_chunk:
                    current_chunk += "\n\n" + section
                else:
                    current_chunk = section

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks
