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


def _parse_payload(event):
    body = event.get("body")
    return json.loads(body) if isinstance(body, str) else event


def _decode_base64_image(value, index):
    if not value:
        raise ValueError(f"Missing imageBase64 for frames[{index}]")
    return base64.b64decode(value)


# 프레임 한 장에 대해 Object & Scene Detection(DetectLabels)을 호출합니다.
def _detect_frame_labels(rekognition, frame, index, min_confidence, max_labels):
    image_bytes = _decode_base64_image(frame.get("imageBase64"), index)
    result = rekognition.detect_labels(
        Image={"Bytes": image_bytes},
        MinConfidence=min_confidence,
        MaxLabels=max_labels,
    )
    return [
        {"name": label["Name"], "confidence": round(label.get("Confidence", 0), 2)}
        for label in result.get("Labels", [])
    ]


def _normalize_target(value):
    return str(value or "").strip().lower()


# 감지된 레이블 중 감시 대상(신제품/브랜드 카테고리) 키워드와 부분 일치하는 항목을 찾습니다.
def _find_match(labels, target_normalized):
    for label in labels:
        if target_normalized in label["name"].lower():
            return label
    return None


def _clamp(value, low, high):
    return min(high, max(low, value))


# 워치리스트 항목별로 노출 빈도, 반응(참여도) 가중치, 상승/하락 모멘텀을 집계합니다.
# frames는 시간순(오래된 -> 최신)으로 정렬되어 있다고 가정합니다.
def _build_momentum_report(watchlist, frame_labels, engagement_scores):
    total_frames = len(frame_labels)
    total_engagement = sum(engagement_scores) or total_frames or 1
    midpoint = -(-total_frames // 2)  # ceil(total_frames / 2)

    report = []
    for raw_target in watchlist:
        target_normalized = _normalize_target(raw_target)
        matches = []

        for frame_index, labels in enumerate(frame_labels):
            match = _find_match(labels, target_normalized)
            if match:
                matches.append({"frameIndex": frame_index, "confidence": match["confidence"]})

        exposure_count = len(matches)
        exposure_rate = exposure_count / total_frames if total_frames > 0 else 0
        avg_confidence = (
            sum(m["confidence"] for m in matches) / exposure_count if exposure_count > 0 else 0
        )
        weighted_exposure = (
            sum(engagement_scores[m["frameIndex"]] for m in matches) / total_engagement
            if total_engagement > 0
            else 0
        )

        # 프레임을 앞/뒤 절반으로 나눠 노출 빈도 변화율(모멘텀)을 계산합니다.
        early_matches = sum(1 for m in matches if m["frameIndex"] < midpoint)
        late_matches = sum(1 for m in matches if m["frameIndex"] >= midpoint)
        early_rate = early_matches / midpoint if midpoint > 0 else 0
        late_rate = late_matches / (total_frames - midpoint) if (total_frames - midpoint) > 0 else 0
        momentum_delta = late_rate - early_rate

        # 노출 빈도(40) + 참여도 가중 노출 비중(30) + 평균 신뢰도(15) + 상승 모멘텀(15)의 가중합입니다.
        momentum_score = _clamp(
            exposure_rate * 40
            + weighted_exposure * 30
            + (avg_confidence / 100) * 15
            + max(momentum_delta, 0) * 15,
            0,
            100,
        )

        momentum_trend = "RISING" if momentum_delta > 0.1 else "DECLINING" if momentum_delta < -0.1 else "STABLE"

        report.append(
            {
                "target": raw_target,
                "exposureCount": exposure_count,
                "totalFrames": total_frames,
                "exposureRate": round(exposure_rate * 100, 1),
                "weightedExposureShare": round(weighted_exposure * 100, 1),
                "avgConfidence": round(avg_confidence, 2),
                "momentumDelta": round(momentum_delta * 100, 1),
                "momentumTrend": momentum_trend,
                "momentumScore": round(momentum_score, 1),
                "matchedFrameIndexes": [m["frameIndex"] for m in matches],
            }
        )

    report.sort(key=lambda r: r["momentumScore"], reverse=True)
    return report


def handler(event=None, context=None):
    event = event or {}
    # CORS preflight
    method = (event.get("requestContext", {}) or {}).get("http", {}).get("method") or event.get("httpMethod")
    if method == "OPTIONS":
        return {"statusCode": 204, "headers": CORS_HEADERS, "body": ""}

    try:
        payload = _parse_payload(event)
        frames = payload.get("frames") or []
        watchlist = [w for w in (payload.get("watchlist") or []) if w]
        min_confidence = float(payload.get("minConfidence") or 60)
        max_labels = int(payload.get("maxLabels") or 20)

        if not frames:
            raise ValueError("Missing required field: frames (array of { imageBase64, engagementScore? })")
        if not watchlist:
            raise ValueError("Missing required field: watchlist (array of target label keywords)")

        rekognition = get_rekognition()

        # 프레임을 순서대로(시간순) 분석해야 모멘텀(초반 vs 후반 노출 변화) 계산이 유효합니다.
        frame_labels = [
            _detect_frame_labels(rekognition, frame, index, min_confidence, max_labels)
            for index, frame in enumerate(frames)
        ]

        engagement_scores = [float(frame.get("engagementScore", 1)) for frame in frames]
        report = _build_momentum_report(watchlist, frame_labels, engagement_scores)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(
                {
                    "totalFrames": len(frames),
                    "watchlist": watchlist,
                    "report": report,
                    "frameLabels": [
                        {"frameIndex": index, "labels": labels} for index, labels in enumerate(frame_labels)
                    ],
                }
            ),
        }
    except Exception as error:  # noqa: BLE001
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": str(error)})}
