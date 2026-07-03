import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lambda_handlers.upload_faces_handler import handler  # noqa: E402

if __name__ == "__main__":
    result = handler({})
    print(result["body"])
