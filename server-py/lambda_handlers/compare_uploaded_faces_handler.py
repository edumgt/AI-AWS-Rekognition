import base64
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.aws_clients import get_rekognition  # noqa: E402


def _decode_base64_image(value, field_name):
    # 필수 필드가 비어 있으면 어떤 값이 누락됐는지 명확히 알려줍니다.
    if not value:
        raise ValueError(f"Missing required field: {field_name}")
    return base64.b64decode(value)


def _parse_payload(event):
    body = event.get("body")
    return json.loads(body) if isinstance(body, str) else event


# API Gateway/Lambda 프록시 이벤트를 처리하는 메인 핸들러입니다.
def handler(event=None, context=None):
    event = event or {}
    try:
        payload = _parse_payload(event)
        similarity_threshold = float(
            payload.get("similarityThreshold") or os.environ.get("SIMILARITY_THRESHOLD", 80)
        )

        source_image = _decode_base64_image(payload.get("sourceImageBase64"), "sourceImageBase64")
        target_image = _decode_base64_image(payload.get("targetImageBase64"), "targetImageBase64")

        rekognition = get_rekognition()
        result = rekognition.compare_faces(
            SourceImage={"Bytes": source_image},
            TargetImage={"Bytes": target_image},
            SimilarityThreshold=similarity_threshold,
        )

        matches = [
            {
                "similarity": round(entry["Similarity"], 2),
                "confidence": round(entry["Face"]["Confidence"], 2),
                "boundingBox": entry["Face"]["BoundingBox"],
            }
            for entry in result.get("FaceMatches", [])
        ]

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "matched": len(matches) > 0,
                    "requestedSimilarityThreshold": similarity_threshold,
                    "maxSimilarity": matches[0]["similarity"] if matches else 0,
                    "matches": matches,
                }
            ),
        }
    except Exception as error:  # noqa: BLE001 - 검증/파싱/호출 오류를 모두 400으로 반환합니다.
        return {"statusCode": 400, "body": json.dumps({"message": str(error)})}
