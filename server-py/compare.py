import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.face_workflow import compare_faces  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent.parent / "server"


def main():
    result = compare_faces(str(BASE_DIR))

    print(f"총 비교 건수: {result['compared_count']}")

    for item in result["comparisons"]:
        status = "✅ 매칭" if item["matched"] else "❌ 비매칭"
        print(f"{status} | {item['source']} vs {item['target']} | 유사도 {item['similarity']}%")

    for name in result["missing"]:
        print(f"⚠️ 파일 없음(비교 제외): {name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        print(f"❌ 얼굴 비교 실패: {error}", file=sys.stderr)
        sys.exit(1)
