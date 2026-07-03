import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.aws_clients import get_rekognition  # noqa: E402

SAMPLE_IMAGE = Path(__file__).resolve().parent.parent / "server" / "sample.png"


def main():
    rekognition = get_rekognition()
    image_bytes = SAMPLE_IMAGE.read_bytes()

    data = rekognition.detect_text(Image={"Bytes": image_bytes})

    print("🔍 이미지에서 감지된 텍스트 목록:\n")
    for idx, text in enumerate(data.get("TextDetections", []), start=1):
        print(f"[{idx}] {text['DetectedText']} (신뢰도: {text['Confidence']:.2f}%)")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        print(f"❌ 에러 발생: {error}", file=sys.stderr)
        sys.exit(1)
