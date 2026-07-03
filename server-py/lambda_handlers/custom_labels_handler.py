import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.aws_clients import get_rekognition  # noqa: E402


def _parse_payload(event):
    body = event.get("body")
    return json.loads(body) if isinstance(body, str) else event


def _split_s3_uri(s3_uri):
    without_scheme = s3_uri.replace("s3://", "")
    bucket, _, key = without_scheme.partition("/")
    return bucket, key


# Rekognition Custom Labels 프로젝트를 새로 생성합니다.
def _create_project(rekognition, project_name):
    if not project_name:
        raise ValueError("Missing required field: projectName")
    result = rekognition.create_project(ProjectName=project_name)
    return {"projectArn": result["ProjectArn"]}


# S3 manifest 파일을 기반으로 Custom Labels 데이터셋을 생성합니다.
# manifest_s3_uri 예시: s3://my-bucket/custom-labels/manifests/train.manifest
def _create_dataset(rekognition, project_arn, dataset_type, manifest_s3_uri):
    if not project_arn:
        raise ValueError("Missing required field: projectArn")
    if not manifest_s3_uri:
        raise ValueError("Missing required field: manifestS3Uri")

    dataset_type = (dataset_type or "TRAIN").upper()  # TRAIN 또는 TEST
    bucket, key = _split_s3_uri(manifest_s3_uri)
    result = rekognition.create_dataset(
        ProjectArn=project_arn,
        DatasetType=dataset_type,
        DatasetSource={"GroundTruthManifest": {"S3Object": {"Bucket": bucket, "Name": key}}},
    )
    return {"datasetArn": result["DatasetArn"]}


# Custom Labels 모델 학습을 시작합니다.
# output_s3_uri 예시: s3://my-bucket/custom-labels/output/
def _train_model(rekognition, project_arn, version_name, output_s3_uri):
    if not project_arn:
        raise ValueError("Missing required field: projectArn")
    if not version_name:
        raise ValueError("Missing required field: versionName")
    if not output_s3_uri:
        raise ValueError("Missing required field: outputS3Uri")

    bucket, key = _split_s3_uri(output_s3_uri)
    result = rekognition.create_project_version(
        ProjectArn=project_arn,
        VersionName=version_name,
        OutputConfig={"S3Bucket": bucket, "S3KeyPrefix": key},
    )
    return {"projectVersionArn": result["ProjectVersionArn"]}


# 학습 중인 모델의 상태를 폴링합니다.
def _describe_versions(rekognition, project_arn, version_names):
    params = {"ProjectArn": project_arn}
    if version_names:
        params["VersionNames"] = version_names

    result = rekognition.describe_project_versions(**params)
    versions = [
        {
            "projectVersionArn": v["ProjectVersionArn"],
            "status": v["Status"],
            "statusMessage": v.get("StatusMessage"),
            # 학습에 사용된 시간(초)입니다.
            "billableTrainingTimeInSeconds": v.get("BillableTrainingTimeInSeconds"),
        }
        for v in result.get("ProjectVersionDescriptions", [])
    ]
    return {"versions": versions}


# 학습 완료된 모델을 배포(추론 준비)합니다.
# min_inference_units: 동시 요청 처리 단위(기본 1, 비용 발생 주의)
def _start_model(rekognition, project_version_arn, min_inference_units):
    if not project_version_arn:
        raise ValueError("Missing required field: projectVersionArn")
    rekognition.start_project_version(
        ProjectVersionArn=project_version_arn,
        MinInferenceUnits=min_inference_units or 1,
    )
    return {"status": "STARTING", "projectVersionArn": project_version_arn}


# 배포된 모델로 이미지를 분석합니다(커스텀 레이블 탐지).
def _detect_labels(rekognition, project_version_arn, image_base64, min_confidence):
    if not project_version_arn:
        raise ValueError("Missing required field: projectVersionArn")
    if not image_base64:
        raise ValueError("Missing required field: imageBase64")

    image_bytes = base64.b64decode(image_base64)
    result = rekognition.detect_custom_labels(
        ProjectVersionArn=project_version_arn,
        Image={"Bytes": image_bytes},
        MinConfidence=min_confidence or 50,
    )
    labels = [
        {
            "name": label["Name"],
            "confidence": round(label.get("Confidence", 0), 2),
            "geometry": label.get("Geometry"),
        }
        for label in result.get("CustomLabels", [])
    ]
    return {"count": len(labels), "labels": labels}


# 배포된 모델을 중지하여 추론 과금을 종료합니다.
# 실습 후 반드시 호출해 비용 발생을 막아야 합니다.
def _stop_model(rekognition, project_version_arn):
    if not project_version_arn:
        raise ValueError("Missing required field: projectVersionArn")
    rekognition.stop_project_version(ProjectVersionArn=project_version_arn)
    return {"status": "STOPPING", "projectVersionArn": project_version_arn}


# ---

# Lambda 핸들러 — action 값으로 동작을 분기합니다.
#
# 지원 action:
#   create-project      — 프로젝트 생성 (projectName 필요)
#   create-dataset      — 데이터셋 등록 (projectArn, manifestS3Uri 필요, datasetType 선택)
#   train               — 모델 학습 시작 (projectArn, versionName, outputS3Uri 필요)
#   describe-versions   — 학습 상태 조회 (projectArn 필요, versionNames 선택)
#   start-model         — 모델 배포 (projectVersionArn 필요, minInferenceUnits 선택)
#   detect              — 커스텀 레이블 탐지 (projectVersionArn, imageBase64 필요, minConfidence 선택)
#   stop-model          — 모델 중지/비용 절감 (projectVersionArn 필요)
def handler(event=None, context=None):
    event = event or {}
    try:
        payload = _parse_payload(event)
        action = payload.get("action")
        rekognition = get_rekognition()

        if action == "create-project":
            data = _create_project(rekognition, payload.get("projectName"))
        elif action == "create-dataset":
            data = _create_dataset(
                rekognition, payload.get("projectArn"), payload.get("datasetType"), payload.get("manifestS3Uri")
            )
        elif action == "train":
            data = _train_model(
                rekognition, payload.get("projectArn"), payload.get("versionName"), payload.get("outputS3Uri")
            )
        elif action == "describe-versions":
            data = _describe_versions(rekognition, payload.get("projectArn"), payload.get("versionNames"))
        elif action == "start-model":
            data = _start_model(rekognition, payload.get("projectVersionArn"), payload.get("minInferenceUnits"))
        elif action == "detect":
            data = _detect_labels(
                rekognition, payload.get("projectVersionArn"), payload.get("imageBase64"), payload.get("minConfidence")
            )
        elif action == "stop-model":
            data = _stop_model(rekognition, payload.get("projectVersionArn"))
        else:
            raise ValueError(
                f'Unknown action: "{action}". Supported: create-project, create-dataset, train, '
                "describe-versions, start-model, detect, stop-model"
            )

        return {"statusCode": 200, "body": json.dumps({"action": action, **data})}
    except Exception as error:  # noqa: BLE001
        return {"statusCode": 400, "body": json.dumps({"message": str(error)})}
