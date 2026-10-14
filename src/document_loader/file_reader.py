from pathlib import Path
from typing import Optional


class RuleFileReader:
    """Reads UTF-8 rule documents while skipping files that cannot be decoded."""

    def read_text_file(self, file_path: Path) -> Optional[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Warning: Skipping unreadable file {file_path}: {exc}")
            return None
