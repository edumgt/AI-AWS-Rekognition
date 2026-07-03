import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.aws_clients import get_rekognition  # noqa: E402

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "https://www.naver.com",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def _decode_base64_image(value):
    if not value:
        raise ValueError("Missing required field: imageBase64")
    return base64.b64decode(value)


def _parse_payload(event):
    body = event.get("body")
    return json.loads(body) if isinstance(body, str) else event


def handler(event=None, context=None):
    event = event or {}
    # CORS preflight
    method = (event.get("requestContext", {}) or {}).get("http", {}).get("method") or event.get("httpMethod")
    if method == "OPTIONS":
        return {"statusCode": 204, "headers": CORS_HEADERS, "body": ""}

    try:
        payload = _parse_payload(event)
        image_bytes = _decode_base64_image(payload.get("imageBase64"))

        rekognition = get_rekognition()
        data = rekognition.detect_text(Image={"Bytes": image_bytes})

        text_detections = [
            {
                "detectedText": entry["DetectedText"],
                "type": entry["Type"],
                "confidence": round(entry["Confidence"], 2),
            }
            for entry in data.get("TextDetections", [])
        ]

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"count": len(text_detections), "textDetections": text_detections}),
        }
    except Exception as error:  # noqa: BLE001
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": str(error)})}
