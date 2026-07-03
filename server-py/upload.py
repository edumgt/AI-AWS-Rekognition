import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.face_workflow import upload_faces  # noqa: E402

# CLI 실행 진입점입니다. server/의 샘플 얼굴 이미지를 그대로 재사용합니다.
BASE_DIR = Path(__file__).resolve().parent.parent / "server"


def main():
    result = upload_faces(str(BASE_DIR))

    for key in result["uploaded"]:
        print(f"✅ 업로드 성공: {key}")

    for name in result["skipped"]:
        print(f"⚠️ 파일 없음(건너뜀): {name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        print(f"❌ 업로드 작업 실패: {error}", file=sys.stderr)
        sys.exit(1)
