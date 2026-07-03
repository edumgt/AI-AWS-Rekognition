# Custom Labels 워크플로를 로컬에서 단계별로 테스트하는 실행 진입점입니다.
# 사용법: python local/custom_labels_local.py
#
# WARNING: 모델 학습(train)은 최소 수십 달러의 비용이 발생합니다.
#          실습 후 반드시 stop-model을 호출해 추론 과금을 종료하세요.
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lambda_handlers.custom_labels_handler import handler  # noqa: E402

# 환경 변수로 재정의 가능한 기본 설정입니다.
PROJECT_NAME = os.environ.get("CUSTOM_LABELS_PROJECT", "rekognition-custom-labels-demo")
BUCKET = os.environ.get("S3_BUCKET_NAME", "polly-bucket-edumgt")
VERSION_NAME = f"v{int(time.time() * 1000)}"
OUTPUT_S3_URI = f"s3://{BUCKET}/custom-labels/output/"


def run():
    print("=== [1/3] Custom Labels 프로젝트 생성 ===")
    create_result = handler({"action": "create-project", "projectName": PROJECT_NAME})
    create_body = json.loads(create_result["body"])
    print(json.dumps(create_body, indent=2, ensure_ascii=False))

    if create_result["statusCode"] != 200:
        print("프로젝트 생성 실패. 종료합니다.", file=sys.stderr)
        sys.exit(1)

    project_arn = create_body["projectArn"]

    print("\n=== [2/3] 학습 상태 조회 예시 ===")
    print("학습은 비용이 발생하므로 이 로컬 스크립트에서는 train을 자동 실행하지 않습니다.")
    print("아래 명령을 직접 실행하거나 scripts/aws_batch_ops.sh custom-labels-train 을 사용하세요:")
    print("")
    print("  Lambda 호출로 학습 시작:")
    print('    action: "train"')
    print(f'    projectArn: "{project_arn}"')
    print(f'    versionName: "{VERSION_NAME}"')
    print(f'    outputS3Uri: "{OUTPUT_S3_URI}"')
    print("")
    print("  manifest 등록 후 학습 시작 → 수 시간 소요 → DescribeProjectVersions 로 상태 확인")

    print("\n=== [3/3] 버전 상태 조회 (학습 진행 상황 확인) ===")
    desc_result = handler({"action": "describe-versions", "projectArn": project_arn})
    print(desc_result["body"])


if __name__ == "__main__":
    try:
        run()
    except Exception as error:  # noqa: BLE001
        print(error, file=sys.stderr)
        sys.exit(1)
