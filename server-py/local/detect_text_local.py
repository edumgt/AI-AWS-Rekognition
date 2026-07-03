import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lambda_handlers.detect_text_handler import handler  # noqa: E402

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "server"

if __name__ == "__main__":
    image_base64 = base64.b64encode((SAMPLE_DIR / "sample.png").read_bytes()).decode("utf-8")
    result = handler({"body": json.dumps({"imageBase64": image_base64})})
    print(result["body"])
