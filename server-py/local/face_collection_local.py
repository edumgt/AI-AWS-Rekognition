# Face Collection 기능을 로컬에서 직접 테스트하는 실행 진입점입니다.
# 사용법: python local/face_collection_local.py
import base64
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lambda_handlers.face_collection_handler import handler  # noqa: E402

# 기본 실습용 Collection ID 입니다. 환경 변수로 재정의할 수 있습니다.
COLLECTION_ID = os.environ.get("COLLECTION_ID", "rekognition-demo-collection")

# face1.png를 ExternalImageId "employee-001"로 Collection에 등록하는 예시입니다.
FACE1_PATH = Path(__file__).resolve().parent.parent.parent / "server" / "face1.png"


def run():
    print("=== [1/4] Collection 생성 ===")
    create_result = handler({"action": "create-collection", "collectionId": COLLECTION_ID})
    print(create_result["body"])

    print("\n=== [2/4] 얼굴 등록 (IndexFaces) ===")
    if FACE1_PATH.exists():
        image_base64 = base64.b64encode(FACE1_PATH.read_bytes()).decode("utf-8")
        index_result = handler(
            {
                "action": "index-face",
                "collectionId": COLLECTION_ID,
                "imageBase64": image_base64,
                # 외부 시스템 식별자를 자유롭게 지정할 수 있습니다(예: 사원번호).
                "externalImageId": "employee-001",
            }
        )
        print(index_result["body"])
    else:
        print(f"face1.png not found at {FACE1_PATH}, skipping IndexFaces.")

    print("\n=== [3/4] 등록된 얼굴 목록 조회 (ListFaces) ===")
    list_result = handler({"action": "list-faces", "collectionId": COLLECTION_ID})
    print(list_result["body"])

    print("\n=== [4/4] 이미지로 얼굴 검색 (SearchFacesByImage) ===")
    if FACE1_PATH.exists():
        image_base64 = base64.b64encode(FACE1_PATH.read_bytes()).decode("utf-8")
        search_result = handler({"action": "search-face", "collectionId": COLLECTION_ID, "imageBase64": image_base64})
        print(search_result["body"])
    else:
        print(f"face1.png not found at {FACE1_PATH}, skipping SearchFacesByImage.")


if __name__ == "__main__":
    try:
        run()
    except Exception as error:  # noqa: BLE001
        print(error, file=sys.stderr)
        sys.exit(1)
