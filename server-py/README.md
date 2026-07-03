# server-py — Python 포팅 모듈

`server/`(Node.js) 모듈과 동일한 기능을 제공하는 Python 포팅 버전입니다. 파일 구조와 함수 책임을
1:1로 맞춰 두었으므로, Node 버전 문서(`../Readme.md`)의 개념 설명을 그대로 참고할 수 있습니다.

샘플 얼굴 이미지(`face1.png` 등)와 웹 프런트엔드 정적 리소스(`web/public`)는 중복 보관하지 않고
`../server/`의 파일을 그대로 재사용합니다. 즉 `server-py`는 항상 `server`와 같은 저장소 안에서
실행되어야 합니다.

## 구조 대응표 (Node ↔ Python)

| Node.js (`server/`) | Python (`server-py/`) |
|---|---|
| `src/config.js` | `src/config.py` |
| `src/awsClients.js`(`aws-sdk` v2) | `src/aws_clients.py`(`boto3`) |
| `src/fileUtils.js` | `src/file_utils.py` |
| `src/faceWorkflow.js` | `src/face_workflow.py` |
| `lambda/*.js` | `lambda_handlers/*.py`(동일한 `handler(event)` 시그니처, Lambda 프록시 응답 포맷 유지) |
| `local/*.js` | `local/*.py` |
| `upload.js` / `compare.js` / `extract.js` | `upload.py` / `compare.py` / `extract.py` |
| `web/app.js`(순수 `http` 서버) | `web/app.py`(FastAPI + Uvicorn) |

## 준비

```bash
cd server-py
python3 -m venv .venv && source .venv/bin/activate   # 선택
pip install -r requirements.txt
cp .env.example .env   # AWS_REGION, S3_BUCKET_NAME 등 값 채우기
```

## 로컬 실행

```bash
python upload.py                              # server/의 face1~6 업로드
python compare.py                              # face1~6 조합 유사도 비교
python extract.py                              # server/sample.png 텍스트 검출
python local/product_momentum_local.py         # 신제품 노출 모멘텀 분석 데모
python local/face_collection_local.py          # Face Collection CRUD 데모
python local/custom_labels_local.py            # Custom Labels 프로젝트 생성 데모
```

## 웹 서버 실행

```bash
cd server-py
python web/app.py
```

`WEB_PORT`(기본 `3100`, Node 버전의 기본 포트 `3000`과 충돌하지 않도록 다르게 설정) /
`WEB_HOST` 환경 변수로 바인딩을 조정할 수 있습니다. 브라우저에서 `server/web/public`과 동일한
프런트엔드가 열립니다. 설정 패널(⚙)에서 API Base URL을 `http://localhost:3100/api`로 지정하면
이 Python 서버의 `/api/compare`, `/api/extract-text`, `/api/product-momentum` 엔드포인트를
그대로 사용할 수 있습니다.

## Docker 기반 실행

```bash
cd server-py
cp .env.example .env   # AWS 자격증명/리전/버킷 값 채우기
docker compose up --build
```

- 빌드 컨텍스트는 저장소 루트이며(`docker-compose.yml`의 `context: ..`), `server/web/public`과
  `server/face*.png`, `server/sample.png`를 이미지에 함께 포함해 Node 버전과 동일한 리소스를 재사용합니다.
- 컨테이너는 `3100` 포트로 FastAPI/Uvicorn 서버를 노출합니다.
- AWS 자격증명은 `server-py/.env`(compose가 자동으로 읽어 `${VAR}` 치환에 사용) 또는 셸
  환경 변수로 주입하세요. 운영 환경에서는 정적 키 대신 IAM Role(ECS Task Role 등) 사용을 권장합니다.

## 참고

- Lambda 배포용 zip 패키징은 아직 Node 버전(`scripts/aws_batch_ops.sh`)만 지원합니다. Python
  Lambda 배포가 필요하면 `lambda_handlers/*.py` + `src/`를 zip으로 묶고 런타임을 `python3.12`,
  핸들러를 예: `lambda_handlers/detect_text_handler.handler`로 지정하세요.
