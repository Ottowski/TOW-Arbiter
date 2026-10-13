import re
from pathlib import Path


class RuleSectionFinder:
    """Find exact special-rule and army-unit sections in the source markdown."""
    # Initialize the rule section finder with the directory containing the rules.
    def __init__(self, rules_directory: str):
        self.rules_directory = Path(rules_directory)

    # Extract a special rule section from the rules.
    def extract_special_rule_section(self, rule_name: str) -> tuple[str, dict] | None:
        """Return the exact section for a special rule name if it exists."""
        special_rules_file = self.rules_directory / "special_rules.md"
        if not special_rules_file.exists():
            return None

        # Read the content of the special rules file.
        text = special_rules_file.read_text(encoding="utf-8")
        rule_name = rule_name.strip()
        heading_names = [rule_name]
        base_name = re.sub(r"\s*\([^)]*\)\s*$", "", rule_name).strip()
        if base_name and base_name != rule_name:
            heading_names.append(base_name)

        heading_pattern = "|".join(re.escape(name) for name in heading_names if name)
        section_pattern = re.compile(
            rf"(?ms)^##\s+(?:{heading_pattern})(?:\s+\([^)]*X[^)]*\))?\s*$\n"
            rf"(.*?)(?=^##\s+|\Z)",
            flags=re.IGNORECASE,
        )
        match = section_pattern.search(text)
        if not match:
            return None

        # Extract the matched section text from the special rules file.
        section_text = (
            f"{match.group(0).splitlines()[0].strip()}\n{match.group(1).strip()}"
        ).strip()
        return section_text, {
            "source": "special_rules.md",
            "file_path": str(special_rules_file),
        }

    # Extract a unit section from the rules.
    def extract_unit_section(self, unit_name: str) -> tuple[str, dict] | None:
        """Return an exact army-unit section if it exists."""
        army_index = self.rules_directory / "army_index"
        if not army_index.exists():
            return None
        
        # Read the content of the army index file.
        unit_name = unit_name.strip()
        unit_names = [unit_name]
        if unit_name.endswith("s"):
            unit_names.append(unit_name[:-1])
        else:
            unit_names.append(f"{unit_name}s")

        # Compile the regex pattern to match the unit section heading and body.
        heading_pattern = "|".join(re.escape(name) for name in unit_names)
        section_pattern = re.compile(
            rf"(?ms)^###\s+(?P<title>{heading_pattern})\s*$\n"
            rf"(?P<body>.*?)(?=^##\s+|^###\s+|\Z)",
            flags=re.IGNORECASE,
        )
        # Iterate through all unit files in the army index to find a matching section.
        for unit_file in sorted(army_index.rglob("*.md")):
            text = unit_file.read_text(encoding="utf-8")
            match = section_pattern.search(text)

            # If a matching section is found, extract and return it.
            if match:
                section_text = (
                    f"### {match.group('title')}\n{match.group('body').strip()}"
                ).strip()
                return section_text, {
                    "source": str(unit_file.relative_to(self.rules_directory)),
                    "file_path": str(unit_file),
                }

        return None
