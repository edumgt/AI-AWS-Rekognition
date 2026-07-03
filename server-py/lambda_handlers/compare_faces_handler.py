import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.face_workflow import compare_faces  # noqa: E402

# server/ 모듈의 샘플 얼굴 이미지를 그대로 재사용합니다.
DEFAULT_FACE_DIR = Path(__file__).resolve().parent.parent.parent / "server"


# 비교 Lambda 엔트리 포인트입니다.
def handler(event=None, context=None):
    base_dir = os.environ.get("LOCAL_FACE_DIR") or str(DEFAULT_FACE_DIR)
    result = compare_faces(base_dir)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Face similarity analysis completed", **result}),
    }
