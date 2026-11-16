"""Optional development check. Runtime runner has no jsonschema dependency."""
import argparse
import json
from pathlib import Path


def main():
    from jsonschema import Draft202012Validator, FormatChecker
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="Configuration, result.json, or runs.jsonl")
    parser.add_argument("--config", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    name = "config-1.0" if args.config else "run-1.1"
    schema = json.loads((root / "schemas" / (name + ".schema.json")).read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    def invalid_constant(value):
        raise ValueError("Non-JSON numeric constant: " + value)
    content = args.path.read_text(encoding="utf-8")
    values = [json.loads(line, parse_constant=invalid_constant) for line in content.splitlines()] if args.path.suffix == ".jsonl" else [json.loads(content, parse_constant=invalid_constant)]
    for index, value in enumerate(values):
        errors = list(validator.iter_errors(value))
        if errors:
            raise ValueError(f"Record {index}: " + "; ".join(error.message for error in errors))
    print(f"Validated {len(values)} record(s) against {name}")


if __name__ == "__main__":
    main()
