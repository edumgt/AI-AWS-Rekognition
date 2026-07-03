import json
import os
import sys
from pathlib import Path

import boto3
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from lambda_handlers.compare_uploaded_faces_handler import handler as compare_uploaded_faces_handler  # noqa: E402
from lambda_handlers.detect_text_handler import handler as detect_text_handler  # noqa: E402
from lambda_handlers.product_momentum_handler import handler as product_momentum_handler  # noqa: E402

# 프런트엔드(정적 리소스)는 server/web/public을 그대로 재사용합니다(중복 보관하지 않음).
PUBLIC_DIR = ROOT_DIR.parent / "server" / "web" / "public"

INTERNAL_ROUTING_FIELDS = ("_mode", "_awsRegion", "_lambdaCompareFn", "_lambdaTextFn", "_lambdaProductMomentumFn")

app = FastAPI(title="Rekognition Web Demo (Python)")


# Local handler execution (existing behavior)
def run_local_handler(handler_fn, body):
    response = handler_fn({"body": json.dumps(body)})
    payload = response.get("body")
    if isinstance(payload, str):
        payload = json.loads(payload) if payload else {}
    return {"statusCode": int(response.get("statusCode", 200)), "body": payload or {}}


# AWS Lambda SDK invocation
def run_lambda_handler(function_name, region, body):
    if not region:
        raise ValueError("AWS 리전이 설정되지 않았습니다. 설정 패널에서 AWS 리전을 입력하거나 서버에 AWS_REGION 환경변수를 설정하세요.")

    lambda_client = boto3.client("lambda", region_name=region)
    invoke_result = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        # Wrap as API Gateway proxy event so Lambda handlers work unchanged
        Payload=json.dumps({"body": json.dumps(body)}).encode("utf-8"),
    )

    payload_bytes = invoke_result["Payload"].read()
    if invoke_result.get("FunctionError"):
        err_payload = json.loads(payload_bytes or b"{}")
        raise RuntimeError(f"Lambda 실행 오류: {err_payload.get('errorMessage', invoke_result['FunctionError'])}")

    lambda_response = json.loads(payload_bytes or b"{}")
    response_body = lambda_response.get("body")
    if isinstance(response_body, str):
        response_body = json.loads(response_body) if response_body else {}

    return {"statusCode": int(lambda_response.get("statusCode", 200)), "body": response_body or {}}


# Route a request to either local handler or Lambda depending on _mode field
def dispatch(local_handler, lambda_fn_key, body):
    mode = body.get("_mode", "local")
    # Strip internal routing fields before forwarding to handlers
    forward_body = {k: v for k, v in body.items() if k not in INTERNAL_ROUTING_FIELDS}

    # awsClients.py는 process 시작 시점의 AWS_REGION 환경변수를 사용하므로,
    # 요청에 _awsRegion이 실려 오면 최초 1회 환경변수로 승격시킵니다.
    region = os.environ.get("AWS_REGION") or body.get("_awsRegion") or ""
    if body.get("_awsRegion") and not os.environ.get("AWS_REGION"):
        os.environ["AWS_REGION"] = body["_awsRegion"]

    if not region:
        raise ValueError(
            "AWS 리전이 설정되지 않았습니다. "
            "설정 패널(⚙)에서 AWS 리전(예: ap-northeast-2)을 입력하거나 "
            "서버에 AWS_REGION 환경변수를 설정하세요."
        )

    if mode == "lambda":
        function_name = body.get(lambda_fn_key)
        if not function_name:
            raise ValueError("Lambda 함수 이름이 비어 있습니다. 설정 패널에서 함수 이름을 입력하세요.")
        return run_lambda_handler(function_name, region, forward_body)

    return run_local_handler(local_handler, forward_body)


@app.post("/api/compare")
async def api_compare(request: Request):
    body = await request.json()
    if not body.get("sourceImageBase64") or not body.get("targetImageBase64"):
        return JSONResponse({"message": "sourceImageBase64, targetImageBase64 값이 필요합니다."}, status_code=400)
    try:
        result = dispatch(compare_uploaded_faces_handler, "_lambdaCompareFn", body)
    except Exception as error:  # noqa: BLE001
        return JSONResponse({"message": str(error)}, status_code=500)
    return JSONResponse(result["body"], status_code=result["statusCode"])


@app.post("/api/extract-text")
async def api_extract_text(request: Request):
    body = await request.json()
    if not body.get("imageBase64"):
        return JSONResponse({"message": "imageBase64 값이 필요합니다."}, status_code=400)
    try:
        result = dispatch(detect_text_handler, "_lambdaTextFn", body)
    except Exception as error:  # noqa: BLE001
        return JSONResponse({"message": str(error)}, status_code=500)
    return JSONResponse(result["body"], status_code=result["statusCode"])


@app.post("/api/product-momentum")
async def api_product_momentum(request: Request):
    body = await request.json()
    if not body.get("frames"):
        return JSONResponse({"message": "frames 배열이 필요합니다."}, status_code=400)
    if not body.get("watchlist"):
        return JSONResponse({"message": "watchlist 배열이 필요합니다."}, status_code=400)
    try:
        result = dispatch(product_momentum_handler, "_lambdaProductMomentumFn", body)
    except Exception as error:  # noqa: BLE001
        return JSONResponse({"message": str(error)}, status_code=500)
    return JSONResponse(result["body"], status_code=result["statusCode"])


# API 라우트 이후에 정적 파일 서빙을 마운트해야 /api/* 경로가 가로채이지 않습니다.
if PUBLIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(PUBLIC_DIR), html=True), name="static")


if __name__ == "__main__":
    host = os.environ.get("WEB_HOST", "0.0.0.0")
    port = int(os.environ.get("WEB_PORT", 3100))
    print(f"Web demo + Python BE API started: http://localhost:{port} (bind {host}:{port})")
    uvicorn.run(app, host=host, port=port)
