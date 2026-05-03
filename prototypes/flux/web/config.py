from pathlib import Path

SERVICE_NAME = "flux"

# flows/ lives at the proto root, alongside web/.
FLOWS_DIR = Path(__file__).resolve().parent.parent / "flows"
