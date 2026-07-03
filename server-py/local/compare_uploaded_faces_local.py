import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lambda_handlers.compare_uploaded_faces_handler import handler  # noqa: E402

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "server"


def _b64(file_name):
    return base64.b64encode((SAMPLE_DIR / file_name).read_bytes()).decode("utf-8")


if __name__ == "__main__":
    result = handler(
        {
            "body": json.dumps(
                {
                    "sourceImageBase64": _b64("face1.png"),
                    "targetImageBase64": _b64("face2.jpg"),
                }
            )
        }
    )
    print(result["body"])
