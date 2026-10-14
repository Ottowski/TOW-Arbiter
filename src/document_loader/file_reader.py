from pathlib import Path
from typing import Optional


class RuleFileReader:
    """Reads UTF-8 rule documents while skipping files that cannot be decoded."""
    # Initialize the file reader.
    def read_text_file(self, file_path: Path) -> Optional[str]:
        try:
            # Attempt to open and read the file.
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
            # If an error occurs, print a warning and return None.
        except (OSError, UnicodeDecodeError) as exc:
            # Print a warning and return None if the file cannot be read.
            print(f"Warning: Skipping unreadable file {file_path}: {exc}")
            return None
