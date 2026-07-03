# .env 파일을 자동 로딩해 로컬 실행 시에도 환경 변수를 쉽게 주입합니다.
import os

from dotenv import load_dotenv

load_dotenv()

# 애플리케이션이 동작하기 위해 반드시 필요한 환경 변수 목록입니다.
REQUIRED_ENV = ["AWS_REGION", "S3_BUCKET_NAME"]

DEFAULT_FACE_FILES = "face1.png,face2.jpg,face3.png,face4.jpg,face5.png,face6.png"


def _assert_required_env(names):
    # 비어 있거나 누락된 항목만 골라냅니다.
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")


def get_config():
    # S3 업로드까지 사용하는 워크플로는 전체 필수 변수를 요구합니다.
    _assert_required_env(REQUIRED_ENV)

    face_files_raw = os.environ.get("FACE_FILES", DEFAULT_FACE_FILES)
    face_files = [name.strip() for name in face_files_raw.split(",") if name.strip()]

    return {
        # AWS SDK가 사용할 기본 리전 값입니다.
        "region": os.environ["AWS_REGION"],
        # 얼굴 이미지를 업로드할 대상 S3 버킷 이름입니다.
        "bucket_name": os.environ["S3_BUCKET_NAME"],
        # Rekognition 비교 임계값을 숫자로 변환하며 기본값은 80입니다.
        "similarity_threshold": float(os.environ.get("SIMILARITY_THRESHOLD", 80)),
        # 비교 대상 파일 목록은 쉼표 문자열을 배열로 분해해 공백/빈 값을 제거합니다.
        "face_files": face_files,
    }


def get_aws_region():
    # Rekognition 같은 읽기 전용 AWS API를 위해 리전만 검증해 반환합니다.
    _assert_required_env(["AWS_REGION"])
    return os.environ["AWS_REGION"]
