from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.contracts.generation import write_contract_artifacts


def main() -> int:
    schema_path, frontend_path = write_contract_artifacts()
    print(f"Wrote {schema_path}")
    print(f"Wrote {frontend_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
