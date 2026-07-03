import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.aws_clients import get_rekognition  # noqa: E402


def _parse_payload(event):
    body = event.get("body")
    payload = json.loads(body) if isinstance(body, str) else event
    collection_id = payload.get("collectionId")
    # 모든 액션에 collectionId가 필요합니다.
    if not collection_id:
        raise ValueError("Missing required field: collectionId")
    return {
        "action": payload.get("action"),
        "collection_id": collection_id,
        "image_base64": payload.get("imageBase64"),
        "face_id": payload.get("faceId"),
        "external_image_id": payload.get("externalImageId"),
        "max_faces": payload.get("maxFaces"),
    }


def _decode_image(value, field_name):
    if not value:
        raise ValueError(f"Missing required field: {field_name}")
    return base64.b64decode(value)


# --- 개별 액션 구현 ---


def _create_collection(rekognition, collection_id):
    result = rekognition.create_collection(CollectionId=collection_id)
    return {"collectionArn": result["CollectionArn"], "statusCode": result["StatusCode"]}


def _delete_collection(rekognition, collection_id):
    result = rekognition.delete_collection(CollectionId=collection_id)
    return {"statusCode": result["StatusCode"]}


def _list_collections(rekognition):
    result = rekognition.list_collections()
    return {"collectionIds": result.get("CollectionIds", [])}


def _index_face(rekognition, collection_id, image_base64, external_image_id):
    image_bytes = _decode_image(image_base64, "imageBase64")
    params = {
        "CollectionId": collection_id,
        "Image": {"Bytes": image_bytes},
        # 이미지당 최대 1개 얼굴만 등록합니다(정면 사진 기준).
        "MaxFaces": 1,
        # 얼굴 이미지 품질이 낮으면 건너뜁니다.
        "QualityFilter": "AUTO",
        # 얼굴 랜드마크/속성 정보도 함께 반환합니다.
        "DetectionAttributes": ["DEFAULT"],
    }
    if external_image_id:
        params["ExternalImageId"] = external_image_id

    result = rekognition.index_faces(**params)
    indexed = [
        {
            "faceId": r["Face"]["FaceId"],
            "externalImageId": r["Face"].get("ExternalImageId"),
            "confidence": round(r["Face"].get("Confidence", 0), 2),
            "boundingBox": r["Face"]["BoundingBox"],
        }
        for r in result.get("FaceRecords", [])
    ]
    return {"indexed": indexed, "unindexedCount": len(result.get("UnindexedFaces", []))}


def _list_faces(rekognition, collection_id, max_faces):
    result = rekognition.list_faces(CollectionId=collection_id, MaxResults=max_faces or 20)
    faces = [
        {
            "faceId": f["FaceId"],
            "externalImageId": f.get("ExternalImageId"),
            "confidence": round(f.get("Confidence", 0), 2),
            "boundingBox": f["BoundingBox"],
        }
        for f in result.get("Faces", [])
    ]
    return {"faces": faces, "count": len(faces)}


def _search_face(rekognition, collection_id, image_base64, max_faces):
    image_bytes = _decode_image(image_base64, "imageBase64")
    result = rekognition.search_faces_by_image(
        CollectionId=collection_id,
        Image={"Bytes": image_bytes},
        MaxFaces=max_faces or 5,
        # 이 임계값 이하의 유사도는 결과에서 제외합니다.
        FaceMatchThreshold=80,
    )
    matches = [
        {
            "faceId": m["Face"]["FaceId"],
            "externalImageId": m["Face"].get("ExternalImageId"),
            "similarity": round(m["Similarity"], 2),
            "confidence": round(m["Face"].get("Confidence", 0), 2),
        }
        for m in result.get("FaceMatches", [])
    ]
    return {"matched": len(matches) > 0, "matches": matches}


def _delete_face(rekognition, collection_id, face_id):
    if not face_id:
        raise ValueError("Missing required field: faceId")
    result = rekognition.delete_faces(CollectionId=collection_id, FaceIds=[face_id])
    return {"deletedFaceIds": result.get("DeletedFaces", [])}


# ---

# Lambda 핸들러 — action 값으로 동작을 분기합니다.
#
# 지원 action:
#   create-collection   — Collection 생성
#   delete-collection   — Collection 삭제
#   list-collections    — Collection 목록 조회
#   index-face          — 얼굴 등록 (imageBase64, externalImageId 필요)
#   list-faces          — 등록된 얼굴 목록 조회
#   search-face         — 이미지로 얼굴 검색 (imageBase64 필요)
#   delete-face         — 얼굴 삭제 (faceId 필요)
def handler(event=None, context=None):
    event = event or {}
    try:
        parsed = _parse_payload(event)
        action = parsed["action"]
        collection_id = parsed["collection_id"]
        rekognition = get_rekognition()

        if action == "create-collection":
            data = _create_collection(rekognition, collection_id)
        elif action == "delete-collection":
            data = _delete_collection(rekognition, collection_id)
        elif action == "list-collections":
            data = _list_collections(rekognition)
        elif action == "index-face":
            data = _index_face(rekognition, collection_id, parsed["image_base64"], parsed["external_image_id"])
        elif action == "list-faces":
            data = _list_faces(rekognition, collection_id, parsed["max_faces"])
        elif action == "search-face":
            data = _search_face(rekognition, collection_id, parsed["image_base64"], parsed["max_faces"])
        elif action == "delete-face":
            data = _delete_face(rekognition, collection_id, parsed["face_id"])
        else:
            raise ValueError(
                f'Unknown action: "{action}". Supported: create-collection, delete-collection, '
                "list-collections, index-face, list-faces, search-face, delete-face"
            )

        return {
            "statusCode": 200,
            "body": json.dumps({"action": action, "collectionId": collection_id, **data}),
        }
    except Exception as error:  # noqa: BLE001
        return {"statusCode": 400, "body": json.dumps({"message": str(error)})}
