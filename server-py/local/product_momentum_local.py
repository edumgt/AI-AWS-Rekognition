import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lambda_handlers.product_momentum_handler import handler  # noqa: E402

# server/ 모듈의 샘플 이미지를 시간순(오래된 -> 최신)으로 촬영된 소셜/뉴스 영상 프레임인 것처럼 가정합니다.
# 실제 운영에서는 유튜브/틱톡/인스타그램에서 추출한 프레임과 조회수/좋아요 등의
# 참여도(engagementScore)를 그대로 전달하면 됩니다.
SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "server"
SAMPLE_FILES = ["face1.png", "face3.png", "face5.png", "sample.png"]

if __name__ == "__main__":
    frames = [
        {
            "imageBase64": base64.b64encode((SAMPLE_DIR / file_name).read_bytes()).decode("utf-8"),
            # 최신 프레임일수록 반응(조회/좋아요)이 커진다고 가정한 샘플 값입니다.
            "engagementScore": (index + 1) * 10,
        }
        for index, file_name in enumerate(SAMPLE_FILES)
    ]

    result = handler(
        {
            "body": json.dumps(
                {
                    "frames": frames,
                    "watchlist": ["Person", "Face", "Photography", "Clothing"],
                    "minConfidence": 60,
                }
            )
        }
    )
    print(result["body"])
