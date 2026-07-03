import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.face_workflow import upload_faces  # noqa: E402

# 샘플 얼굴 이미지(face1~6, sample.png)는 server/ 모듈에만 두고 중복 보관하지 않습니다.
# server-py는 기본적으로 그 이미지들을 그대로 재사용합니다.
DEFAULT_FACE_DIR = Path(__file__).resolve().parent.parent.parent / "server"


# 업로드 Lambda 엔트리 포인트입니다.
def handler(event=None, context=None):
    # 로컬 기준 디렉터리는 환경 변수 우선, 없으면 server/ 샘플 이미지 디렉터리를 사용합니다.
    base_dir = os.environ.get("LOCAL_FACE_DIR") or str(DEFAULT_FACE_DIR)
    result = upload_faces(base_dir)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Face image upload completed", **result}),
    }
