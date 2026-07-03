# AWS Rekognition 실습 리팩토링 가이드 (Node.js + Lambda + Shell 자동화)

![alt text](image.png)

이 문서는 이 저장소를 **실습 중심으로 재구성**한 최신 가이드입니다.  
목표는 아래 3가지를 한 번에 수행하는 것입니다.
 
1. `server` 기반 Node.js 코드로 Rekognition 실습 환경 구성
2. `face1.png ~ face4.png` 업로드 및 유사성 분석을 **AWS Lambda**로 실행
3. `scripts/aws_batch_ops.sh` 하나로 **버킷 준비 → Lambda 배포/호출 → 결과 수집** 자동화

---

# AWS Rekognition 기반 주식투자 및 자산운용 AI 시스템 활용 기획서

본 문서는 AWS Rekognition의 컴퓨터 비전(Image & Video Analysis) 기술을 주식 투자 및 자산운용 시스템에 접목하여 대안 데이터 수집, 리스크 관리, 보안 및 컴플라이언스를 강화하기 위한 활용 방안을 다룹니다.

---

## 1. 대안 데이터(Alternative Data) 수집을 통한 시장 예측
전통적인 재무제표 데이터를 넘어, 현실 세계의 시각적 데이터를 실시간으로 분석하여 기업의 미래 실적과 시장 트렌드를 예측합니다.

* **위성 및 드론 이미지 분석 (`Label Detection`)**
    * **유통/소매업 실적 예측:** 대형 마트, 쇼핑몰 주차장의 차량 대수를 주기적으로 추적·분석하여 분기 매출을 선행 예측합니다.
    * **원자재 및 물류 동향 파악:** 정유 공장의 원유 저장 탱크 탑(Floating Roof Tank) 높이를 통해 원유 재고량을 파악하거나, 항만의 컨테이너 물동량을 분석하여 글로벌 공급망 호황 여부를 진단합니다.
* **소셜 미디어 및 뉴스 비디오 분석 (`Object & Scene Detection`)**
    * **신제품 모멘텀 포착:** 유튜브, 틱톡, 인스타그램 등 영상 플랫폼에서 특정 신제품(신형 스마트폰, 신차, 인기 화장품 등)이 노출되는 빈도와 대중의 반응을 감지하여 관련 주가의 상승 모멘텀을 선제적으로 포착합니다.
      → **구현:** `lambda/productMomentumHandler.js` (`Rekognition DetectLabels` 기반). 자세한 사용법은 아래 "4-1) 웹 프론트엔드 모듈 실행" 섹션의 "3) 신제품 노출 모멘텀 분석" 항목을 참고하세요.

---

## 2. 미디어 분석을 통한 감성 분석(Sentiment Analysis) 및 리스크 관리
경영진의 비언어적 표현이나 뉴스 속 분위기 등 비정형 시각 데이터를 데이터화하여 투자 의사결정에 활용합니다.

* **경영진 및 전문가 감정 분석 (`Emotion Detection`)**
    * **기업 숨은 리스크 감지:** 주요 기업 CEO의 IR 발표, 기자회견, 청문회 영상을 분석합니다. 발표자의 미세한 표정 변화(불안, 당황, 자신감 등)와 입술 떨림 등을 감지하여 실적 발표의 신뢰도나 기업의 숨겨진 리스크를 정량화합니다.
* **뉴스 및 방송 텍스트 실시간 추출 (`Text in Image/Video`)**
    * **초고속 속보 데이터베이스화:** 경제 방송 스크린 하단에 흐르는 자막(Ticker)이나 실시간 도표 내의 숫자 정보를 추출합니다. 이를 자연어 처리(NLP) 엔진과 연동하여 뉴스 리포트보다 빠르게 시장 충격 요인을 데이터화합니다.

---

## 3. 기업 브랜드 노출도 검출 (Brand & Logo Detection)
글로벌 미디어 내에서 특정 기업의 브랜드가 노출되는 빈도와 시간을 측정하여 마케팅 ROI 및 브랜드 가치를 평가합니다.

* **스포츠 마케팅 및 스폰서십 효과 측정**
    * EPL, NFL, 올림픽 등 대형 스포츠 경기 영상에서 특정 기업의 로고가 노출되는 스크린 타임을 자동 계산하여, 마케팅 효율성을 가늠하고 주가에 미칠 지표로 활용합니다.
* **엔터테인먼트/콘텐츠 투자 가치 평가**
    * 넷플릭스 등 OTT 드라마나 영화 속 PPL 제품 노출을 추적하여, 콘텐츠 흥행에 따른 직접적인 수혜주(수출 증가, 브랜드 인지도 상승 등)를 발굴하는 퀀트 알고리즘에 대입합니다.

---

## 4. 자산운용사 내부 보안 및 컴플라이언스 강화
자산운용 시스템 자체의 데이터 신뢰도를 높이고 내부 통제 시스템을 고도화합니다.

* **부적절한 콘텐츠 자동 차단 (`Content Moderation`)**
    * 투자 커뮤니티나 리서치 플랫폼 내 유저가 업로드하는 이미지 중 딥페이크 사기 그래픽, 성인물, 폭력성 이미지 등을 자동으로 필터링하여 플랫폼의 신뢰도를 유지합니다.
* **트레이딩 룸 보안 및 이상 행동 감지 (`Custom Labels`)**
    * 보안이 극도로 중요한 트레이딩 룸 내부 CCTV와 연동합니다. 인가되지 않은 행동(예: 모니터 화면을 스마트폰으로 촬영하는 행위, 허가되지 않은 인원의 접근)을 Custom Labels로 학습시켜 실시간으로 경고를 발생시킵니다.

---

## 5. 시스템 아키텍처 파이프라인 (추천 조합)

AWS Rekognition의 기능을 극대화하기 위해 아래와 같이 AWS의 타 서비스와 파이프라인을 구축하는 것을 권장합니다.

---

## 기술 스택 (Tech Stack)

`doc/` 폴더의 11개 챕터 커리큘럼과 `docker/video-pathing` 모듈에서 실제로 사용하는 기술을 아래와 같이 하나로 정리했습니다.

| 영역 | 기술/서비스 | 이 저장소에서의 쓰임 | 관련 커리큘럼 |
|---|---|---|---|
| 클라우드 계정/보안 기초 | AWS Organizations, Region/AZ, Root Account, MFA, Billing Alert | 계정 구조 이해 및 초기 보안 설정 | Chapter01 |
| IAM 권한 설계 | IAM Policy(JSON), User/Group/Role, Allow/Deny 평가, Access Analyzer | 최소 권한 원칙에 따른 Lambda 실행 Role, S3 접근 권한 설계 | Chapter02, [부록: Principal/AssumeRole](#원문-readme4md--iam-핵심-개념-정리-principal-vs-assumerole) |
| CLI 자동화 | AWS CLI v2, named profile, `--query`(JMESPath), `--output table` | `scripts/aws_batch_ops.sh`, `backup_all_lambdas.sh` 전 구간 | Chapter03 |
| 스토리지 | Amazon S3, SSE-S3 암호화, Lifecycle(Expiration), 퍼블릭 액세스 차단, 버전관리 | 실습 이미지/학습 데이터 저장(`training/`), 자동 만료 정책 | Chapter04, [부록: S3 퍼블릭/Lifecycle](#원문-readme3md--s3-퍼블릭-접근--lifecycle-실습-정리) |
| 런타임/SDK | Node.js 18+, npm, dotenv, `aws-sdk`(v2) | `server/` 전체(로컬 CLI, Lambda 핸들러, 웹 서버) | Chapter05 |
| 컴퓨터 비전 AI | Amazon Rekognition — `DetectText`, `CompareFaces`, `DetectLabels`(Object & Scene Detection), Custom Labels, Face Collection(`IndexFaces`/`SearchFacesByImage`) | 얼굴 비교, 텍스트 추출, 신제품 노출 모멘텀 분석, 도메인 Fine-tuning | Chapter06, Chapter07, Chapter11 |
| 서버리스 컴퓨팅 | AWS Lambda(`nodejs18.x`), API Gateway 연동 | `server/lambda/*Handler.js` 배포 및 웹 데모 `_mode=lambda` 호출 | Chapter07, Chapter08 |
| 운영 자동화 | Bash(`set -euo pipefail`), `aws s3 sync/cp/rm`, idempotent 배포, cron/CI 연동 | `scripts/aws_batch_ops.sh`(init/upload/deploy/invoke/report) | Chapter08 |
| 모니터링/비용/보안 | CloudWatch, CloudTrail, AWS Budgets, Access Key Rotation | Lambda 로그 확인, 비용 통제, 자격증명 점검 체크리스트 | Chapter09 |
| 프로젝트/문서화 | Mermaid 다이어그램, 아키텍처 문서, 통합 테스트 전략 | `doc/node-entry-flow.md`(진입점 흐름도), 최종 프로젝트 로드맵 | Chapter10 |
| 영상 객체 추적(대체 서비스) | Python, Docker(PyTorch CUDA 런타임), FastAPI, Uvicorn, YOLOv9, ByteTrack(`supervision`), OpenCV(`opencv-python-headless`), NumPy | Rekognition Video People Pathing 대체 — `docker/video-pathing` | `docker/video-pathing/README.md` |
| Python 포팅 모듈 | Python 3.12, `boto3`, FastAPI, Uvicorn, `python-dotenv`, Docker | `server/`(Node.js)와 동일한 기능(얼굴 비교/텍스트 추출/신제품 모멘텀 분석/Face Collection/Custom Labels)의 Python 버전 — `server-py/` | `server-py/README.md` |

> 챕터별 상세 학습 목표/실습 커리큘럼 전문은 `doc/README.md`(인덱스)와 `doc/Chapter01~11/`에서 확인할 수 있습니다.

---
## 문서 맵 (빠른 이동)

실습 목적에 따라 아래 문서를 함께 참고하세요.

- `DOC/README.md`: 11개 챕터 커리큘럼 인덱스
- `DOC/Chapter11/`: 도메인 Fine-tuning — Custom Labels & Face Collection
- `docker/video-pathing/README.md`: YOLOv9 + ByteTrack 기반 Video People Pathing 대체 서비스
- [`server-py/README.md`](./server-py/README.md): `server/`(Node.js)와 동일한 기능의 Python 포팅 모듈 + Docker 실행 가이드
- [부록: 로컬 실행 가이드](#원문-readme2md--로컬-실행-가이드)
- [부록: S3 퍼블릭 접근/라이프사이클](#원문-readme3md--s3-퍼블릭-접근--lifecycle-실습-정리)
- [부록: IAM Principal/AssumeRole](#원문-readme4md--iam-핵심-개념-정리-principal-vs-assumerole)
- [부록: Lambda 운영/백업](#원문-lambdamd--lambda-운영백업-실습-가이드)

---
## 1) 리팩토링 핵심 구조

```bash
.
├─ server/
│  ├─ src/
│  │  ├─ awsClients.js         # AWS SDK 클라이언트 초기화
│  │  ├─ config.js             # 환경변수/실습 기본값 관리
│  │  ├─ fileUtils.js          # 이미지 파일 로딩 유틸
│  │  └─ faceWorkflow.js       # 얼굴 업로드 + 얼굴 비교 비즈니스 로직
│  ├─ lambda/
│  │  ├─ uploadFacesHandler.js        # Lambda: face1~6 S3 업로드
│  │  ├─ compareFacesHandler.js       # Lambda: face1~6 유사도 비교
│  │  ├─ compareUploadedFacesHandler.js # Lambda: 웹 업로드 이미지 비교
│  │  ├─ detectTextHandler.js         # Lambda: 텍스트 감지
│  │  ├─ faceCollectionHandler.js     # Lambda: Face Collection CRUD + 검색
│  │  ├─ customLabelsHandler.js       # Lambda: Custom Labels Fine-tuning
│  │  └─ productMomentumHandler.js    # Lambda: 신제품 노출 모멘텀 분석(Object & Scene Detection)
│  ├─ local/
│  │  ├─ compareFacesLocal.js         # 로컬 실행용
│  │  ├─ compareUploadedFacesLocal.js # 로컬 실행용
│  │  ├─ detectTextLocal.js           # 로컬 실행용
│  │  ├─ uploadFacesLocal.js          # 로컬 실행용
│  │  ├─ faceCollectionLocal.js       # Face Collection 로컬 실행용
│  │  ├─ customLabelsLocal.js         # Custom Labels 로컬 실행용
│  │  └─ productMomentumLocal.js      # 신제품 노출 모멘텀 분석 로컬 실행용
│  ├─ training/
│  │  └─ domain/                      # 도메인 학습 이미지 + manifest 예시
│  ├─ upload.js                # 로컬 실행용 업로드 엔트리
│  ├─ compare.js               # 로컬 실행용 비교 엔트리
│  ├─ extract.js               # 텍스트 감지 샘플
│  └─ web/                     # Node.js 웹 데모(파일 업로드 -> Lambda 호출)
└─ scripts/
   └─ aws_batch_ops.sh         # 버킷/Lambda/실습 배치 자동화
```

---

## 2) 사전 준비

- AWS 계정, IAM 사용자(또는 Role) 준비
- 최소 권한 권장 정책
  - S3: 버킷 생성/설정/업로드/조회
  - Lambda: 함수 생성/수정/호출
  - Rekognition: `CompareFaces`, `DetectText`
  - IAM: Lambda 생성 시 Role 조회 권한
- 로컬 도구
  - WSL Ubuntu 내부의 Node.js 18+
  - npm
  - AWS CLI v2
  - zip 명령어

---

## 3) 환경 변수 설정

루트 또는 `server/.env` 기준으로 아래 값 설정:

```env
AWS_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=polly-bucket-edumgt
SIMILARITY_THRESHOLD=80
FACE_FILES=face1.png,face2.png,face3.png,face4.png,face5.png,face6.png
```

> 실제 운영에서는 Access Key보다 IAM Role(예: EC2/CloudShell/Lambda 실행 역할)을 우선 권장합니다.

---

## 4) 로컬 실행(빠른 검증)
#### WSL Node.js 설치 및 확인


```bash
cd server
/usr/bin/node -v
/usr/bin/npm -v
npm install
npm run upload:faces
npm run compare:faces
npm run extract
npm run lambda:product-momentum:local
```

- 이 저장소의 Node.js 스크립트는 Linux/WSL 런타임 기준으로 정리되어 있습니다.
- WSL 터미널에서 `npm run ...`을 실행하면 되고, 경로 충돌이 있을 때는 `/usr/bin/npm run <script>`를 우선 사용하세요.
- Windows Node.js가 직접 실행되면 즉시 중단하고 WSL 실행 방법을 안내합니다.

- `upload:faces`: `training/face1~6.png` 경로로 S3 업로드
- `compare:faces`: face1~6를 조합 비교하여 유사도 출력
- `extract`: `sample.png` 텍스트 검출
- `lambda:product-momentum:local`: 로컬 샘플 이미지를 시간순 소셜/영상 프레임으로 가정해 `DetectLabels` 기반 신제품 노출 모멘텀(노출 빈도 + 참여도 가중 + 상승/하락 추세)을 계산

---


## 4-1) 웹 프론트엔드 모듈 실행 (신규)

`server/web`는 브라우저에서 이미지를 업로드하고, 같은 Node.js 백엔드 프로세스의 `/api/*` 엔드포인트가 Rekognition 로직을 직접 실행하는 웹 예제입니다.

```bash
cd server
npm run web
```

브라우저 접속: `http://localhost:3000`

- WSL에서 실행해도 Windows 호스트 브라우저의 `http://localhost:3000`으로 접속할 수 있도록 웹 서버는 기본적으로 `0.0.0.0:3000`에 바인딩됩니다.
- `localhost` 포워딩이 안 되는 환경이면 WSL 가상 IP(`eth0`)로 직접 접속하세요. 예: `http://172.29.x.x:3000`
- 일반적으로 Windows의 `vEthernet (WSL)`는 `172.29.x.x/20`, WSL의 `eth0`도 같은 `172.29.x.x/20` 대역을 사용하므로 Windows 브라우저에서 WSL IP로 직접 접근할 수 있습니다.
- `3000` 포트가 이미 사용 중이면 `WEB_PORT=3001 npm run web`처럼 다른 포트로 실행하세요.
- 접속이 안 되면 WSL 안에서 `curl http://127.0.0.1:3000`이 먼저 되는지 확인해 보세요.
- WSL IP 확인: `ip -4 addr show eth0`

필요 환경 변수:

```env
AWS_REGION=ap-northeast-2
```
### 오류의 경우 필요한 확인

```
aws sts get-caller-identity --region ap-northeast-2
aws configure list
```


- **이미지 유사성 비교**: source/target 이미지를 업로드해 Node.js BE API가 Rekognition `CompareFaces` 호출
- **텍스트 추출**: 단일 이미지를 업로드해 Node.js BE API가 Rekognition `DetectText` 호출
- **신제품 노출 모멘텀 분석** (`3) 신제품 노출 모멘텀 분석` 섹션): 시간순으로 여러 프레임 이미지를 업로드하고 워치리스트(예: `Smartphone, Cosmetics, Car`)를 입력하면, Node.js BE API가 각 프레임에 Rekognition `DetectLabels`(Object & Scene Detection)를 호출해 워치리스트 항목별 노출 횟수/비율, 참여도(engagement) 가중 노출 비중, 초반 대비 후반 노출 변화(모멘텀 추세: RISING/STABLE/DECLINING)와 0~100 모멘텀 점수를 계산합니다.
  - API: `POST /api/product-momentum` (로컬) 또는 `POST {base}/product-momentum` (API Gateway)
  - 요청 바디: `{ frames: [{ imageBase64, engagementScore? }], watchlist: string[], minConfidence? }`
  - `frames`는 유튜브/틱톡/인스타그램 등에서 추출한 프레임을 시간순(오래된 → 최신)으로 전달한다고 가정하며, `engagementScore`(조회수/좋아요 등)를 함께 넘기면 노출 비중 계산에 반영됩니다.

---

## 4-1-1) Python 포팅 모듈 실행 (신규, Docker 지원)

`server-py/`는 위 `server/`(Node.js) 모듈과 동일한 기능(얼굴 비교, 텍스트 추출, 신제품 노출 모멘텀
분석, Face Collection, Custom Labels)을 제공하는 Python(FastAPI + boto3) 포팅 버전입니다.
샘플 이미지와 웹 프런트엔드(`web/public`)는 `server/`의 것을 그대로 재사용하므로 두 모듈은 항상
같은 저장소 안에서 함께 실행되어야 합니다.

```bash
# 로컬 실행
cd server-py
pip install -r requirements.txt
cp .env.example .env   # AWS_REGION, S3_BUCKET_NAME 등 값 채우기
python web/app.py      # http://localhost:3100

# Docker 기반 실행
cd server-py
cp .env.example .env
docker compose up --build   # http://localhost:3100
```

세부 구조 대응표, CLI 스크립트(`upload.py`/`compare.py`/`extract.py`) 사용법, Docker 빌드
컨텍스트 설명은 [`server-py/README.md`](./server-py/README.md)를 참고하세요.

---

## 4-2) YOLOv9 + ByteTrack Video People Pathing 대체 서비스

Amazon Rekognition의 **Video People Pathing** 대체 용도로 `docker/video-pathing` 모듈을 추가했습니다.

- **YOLOv9**: 사람 객체 검출
- **ByteTrack**: 동일 인물의 프레임 간 이동 경로 추적
- **FastAPI + Docker**: 온프레미스/사내 GPU 서버 또는 로컬 Docker 환경에 배포 가능

빠른 시작:

```bash
cd docker/video-pathing
docker compose up --build
```

기본 호출 예시:

```bash
curl -X POST http://localhost:8080/track/upload \
  -F 'file=@/absolute/path/to/people.mp4'
```

주요 결과물:

- 추적 박스 + 이동 경로가 포함된 annotated mp4
- 트랙별 좌표 시퀀스가 저장된 JSON

세부 설정과 API 예시는 `docker/video-pathing/README.md`를 참고하세요.

## 5) Lambda 배포 자동화 (핵심)

`scripts/aws_batch_ops.sh`가 Lambda 실습용 명령을 제공합니다.

### 5-1. 기본 배치 명령

```bash
# 버킷 초기화(없으면 생성, 암호화/lifecycle 적용)
./scripts/aws_batch_ops.sh init

# 샘플 파일 업로드(face1~6 + sample)
./scripts/aws_batch_ops.sh upload

# Lambda 배포 zip 생성
./scripts/aws_batch_ops.sh lambda-package
```

### 5-2. Lambda 함수 생성/업데이트

최초 생성 시 `LAMBDA_ROLE_ARN`이 필요합니다.

```
cat > trust-lambda.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "lambda.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
JSON
```
---
```
aws iam create-role \
  --role-name rekognition-lambda-role \
  --assume-role-policy-document file://trust-lambda.json
```
```
aws iam attach-role-policy \
  --role-name rekognition-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

---

```bash
export AWS_REGION=ap-northeast-2
export S3_BUCKET_NAME=edumgt-20260402-14-test
export LAMBDA_ROLE_ARN=arn:aws:iam::086015456585:role/rekognition-lambda-role

./scripts/aws_batch_ops.sh lambda-deploy
```

자동으로 아래 함수가 생성(또는 업데이트)됩니다.

- `rekognition-face-upload` (`lambda/uploadFacesHandler.handler`)
- `rekognition-face-compare` (`lambda/compareFacesHandler.handler`)
- `rekognition-face-compare-upload` (`lambda/compareUploadedFacesHandler.handler`)
- `rekognition-text-detect` (`lambda/detectTextHandler.handler`)
- `rekognition-product-momentum` (`lambda/productMomentumHandler.handler`)

---
```
aws lambda get-function-configuration \
  --region ap-northeast-2 \
  --function-name rekognition-face-upload \
  --query '{State:State, LastUpdateStatus:LastUpdateStatus, Reason:LastUpdateStatusReason}' \
  --output table
```


### 5-3. Lambda 호출 및 결과 파일 확인

```bash
./scripts/aws_batch_ops.sh lambda-invoke
```

결과 파일:

- `batch-work/upload-result.json`
- `batch-work/compare-result.json`

---
```
root@DESKTOP-D6A344Q:/home/AI-AWS-Rekognition# aws lambda get-function-configuration \
  --region ap-northeast-2 \
  --function-name rekognition-face-compare \
  --query '{Runtime:Runtime, Handler:Handler, Role:Role, Timeout:Timeout, MemorySize:MemorySize}' \
  --output table
--------------------------------------------------------------------------
|                        GetFunctionConfiguration                        |
+------------+-----------------------------------------------------------+
|  Handler   |  lambda/compareFacesHandler.handler                       |
|  MemorySize|  256                                                      |
|  Role      |  arn:aws:iam::086015456585:role/rekognition-lambda-role   |
|  Runtime   |  nodejs18.x                                               |
|  Timeout   |  30                                                       |
+------------+-----------------------------------------------------------+
root@DESKTOP-D6A344Q:/home/AI-AWS-Rekognition# 
```
---
```
aws lambda create-function \
  --region ap-northeast-2 \
  --function-name rekognition-face-compare-upload \
  --runtime nodejs24.x \
  --handler lambda/compareFacesHandler.handler \
  --role arn:aws:iam::086015456585:role/rekognition-lambda-role \
  --timeout 5 \
  --memory-size 128 \
  --zip-file fileb://./batch-work/lambda-compare-upload.zip
```
---
```
aws lambda get-function --region ap-northeast-2 --function-name rekognition-face-compare-upload
```
---
```
aws lambda get-function-configuration \
  --region ap-northeast-2 \
  --function-name rekognition-face-upload \
  --query 'Environment.Variables' \
  --output json
```
---
```
aws lambda update-function-configuration \
  --region ap-northeast-2 \
  --function-name rekognition-face-compare-upload \
  --environment "Variables={S3_BUCKET_NAME=edumgt-20260402-14-test}"

aws lambda wait function-updated \
  --region ap-northeast-2 \
  --function-name rekognition-face-compare-upload
```

### 5-4. 실습 원클릭 파이프라인

```bash
./scripts/aws_batch_ops.sh lab-all
```

실행 순서:

1. `init`
2. `upload`
3. `lambda-deploy`
4. `lambda-invoke`
5. `report`

---

## 6) 스크립트 환경 변수 상세

- `AWS_PROFILE`: AWS CLI 프로파일 사용 시 지정
- `AWS_REGION`: 리전
- `S3_BUCKET_NAME`: 버킷명(기본 `polly-bucket-edumgt`)
- `UPLOAD_DIR`: 샘플 이미지 소스 경로(기본 `./server`)
- `WORK_DIR`: zip/리포트 출력 경로(기본 `./batch-work`)
- `LAMBDA_ROLE_ARN`: Lambda 생성 시 필요
- `LAMBDA_UPLOAD_FUNCTION`: 업로드 함수명 기본값
- `LAMBDA_COMPARE_FUNCTION`: 샘플 face1~6 비교 함수명 기본값
- `LAMBDA_COMPARE_UPLOAD_FUNCTION`: 웹 업로드 이미지 비교 함수명 기본값
- `LAMBDA_TEXT_FUNCTION`: 웹 텍스트 추출 함수명 기본값
- `LAMBDA_PRODUCT_MOMENTUM_FUNCTION`: 신제품 노출 모멘텀 분석 함수명 기본값

---

## 7) 실습 체크리스트

### “임계값 80% 기준으로 98.47% 일치 → 동일 인물로 판단”
### “임계값 80% 기준으로 최대 62.10% → 동일 인물로 보기 어려움”


- [ ] `aws sts get-caller-identity` 정상 응답
- [ ] `init` 후 버킷 암호화, lifecycle 정책 적용 확인
- [ ] `upload` 후 `training/face1~6.png` 존재 확인
- [ ] `lambda-deploy` 성공 로그 확인
- [ ] `lambda-invoke` 결과 JSON에서 유사도 값 확인
- [ ] `report` 파일 생성 확인

---

## 8) 트러블슈팅

1. **Lambda 생성 실패 (`AccessDenied`)**
   - `LAMBDA_ROLE_ARN`의 신뢰 정책(Trust Policy)에 `lambda.amazonaws.com` 포함 여부 확인

2. **`InvalidParameterValueException` (핸들러/런타임 오류)**
   - 핸들러 문자열이 아래와 일치하는지 확인
     - `lambda/uploadFacesHandler.handler`
     - `lambda/compareFacesHandler.handler`


### 내일 체크 대상
---
```
{
  "errorType": "Runtime.ImportModuleError",
  "errorMessage": "Error: Cannot find module 'compareFacesHandler'\nRequire stack:\n- /var/runtime/index.mjs",
  "trace": [
    "Runtime.ImportModuleError: Error: Cannot find module 'compareFacesHandler'",
    "Require stack:",
    "- /var/runtime/index.mjs",
    "    at loadModule (file:///var/runtime/index.mjs:573:13)",
    "    at async UserFunctionLoader.load (file:///var/runtime/index.mjs:504:20)",
    "    at async createRuntime (file:///var/runtime/index.mjs:1217:52)",
    "    at async ignition (file:///var/runtime/index.mjs:1633:21)"
  ]
}
```
---
```
이 에러가 왜 나는지(핸들러 경로/파일명/번들링/ESM·CJS 불일치)부터 짚고, Lambda에서 바로 동작하는 정답 핸들러 설정 + 파일 구조 + 빌드/배포 체크리스트를 한 번에 정리해줄게요.

24s 동안 생각함

이 에러는 Lambda가 “compareFacesHandler”라는 모듈(파일)을 런타임에서 못 찾는다는 뜻이에요. 거의 항상 아래 4가지 중 하나입니다.

1) Handler 값이 잘못됨 (가장 흔함)

Lambda의 Handler는 파일경로.익스포트이름 형식이어야 해요.

✅ 올바른 예

파일이 루트에 있고 export가 handler라면
Handler = compareFacesHandler.handler

파일이 src/compareFacesHandler.js라면
Handler = src/compareFacesHandler.handler

빌드 결과가 dist/compareFacesHandler.js라면
Handler = dist/compareFacesHandler.handler

❌ 잘못된 예

compareFacesHandler (점 없이 파일만 적음) → 런타임이 “패키지 모듈”처럼 해석해서 못 찾는 경우가 많음

2) 배포 zip 안에 파일이 “루트”에 없거나, 경로가 한 단계 더 들어가 있음

Lambda는 /var/task(zip 풀린 최상위) 기준으로 핸들러 파일을 찾습니다.

흔한 실수

zip 구조가 이렇게 됨:

function.zip
  my-project/
    compareFacesHandler.js
    package.json

→ Lambda는 루트에 compareFacesHandler.js가 없어서 못 찾음

✅ 올바른 zip 구조
function.zip
  compareFacesHandler.js
  package.json
  node_modules/...
✅ zip 만들 때 추천 커맨드

빌드 산출물이 dist/에 있다면:

cd dist
zip -r ../function.zip .

zip -r function.zip dist 처럼 “폴더째” 넣으면 한 단계 더 들어가서 깨지는 경우가 많아요.

3) 파일 확장자/ESM(CJS) 방식이 핸들러와 안 맞음

런타임이 index.mjs로 부팅되는 건 정상이고, 당신 코드가 ESM이든 CJS든 맞춰주면 돼요.

✅ CommonJS 방식(가장 무난)

compareFacesHandler.js

exports.handler = async (event) => {
  return { statusCode: 200, body: JSON.stringify({ ok: true }) };
};

Handler: compareFacesHandler.handler

✅ ESM 방식

파일 확장자를 .mjs로 하거나

package.json에 "type": "module" 설정

compareFacesHandler.mjs

export const handler = async (event) => {
  return { statusCode: 200, body: JSON.stringify({ ok: true }) };
};

Handler: compareFacesHandler.handler (확장자 없음)

TS로 빌드한다면 **최종 산출물(.js)이 어디에 생기는지(dist 등)**와 Handler 경로가 반드시 일치해야 합니다.

4) 대소문자 불일치 (리눅스는 대소문자 구분)

로컬(Windows/Mac)에서는 통과해도, Lambda(Linux)는 구분합니다.

파일명: compareFacesHandler.js

Handler: compareFacesHandler.handler
이 둘이 철자/대소문자까지 정확히 같아야 해요.

빠른 해결 순서 (이대로 하면 대부분 끝)

Lambda 설정 → Handler를 compareFacesHandler.handler (또는 실제 폴더 경로 포함)로 수정

배포 zip을 열어보고 **루트에 compareFacesHandler.js(또는 dist/… 경로)**가 실제로 있는지 확인

코드가 CJS면 exports.handler, ESM이면 export const handler인지 확인 + package.json type/확장자 확인

파일명 대소문자 확인

원하면, 지금 프로젝트의 실제 파일 트리(핸들러 파일 위치) + Lambda의 Handler 설정 값 + 빌드/배포 방식(SAM/CDK/Serverless/콘솔 zip) 이 3가지만 붙여주면, 당신 상황에 맞는 “정답 Handler 값 + 올바른 zip 커맨드”를 딱 한 줄로 확정해줄게요.
```

3. **S3 업로드 실패**
   - `S3_BUCKET_NAME`, 리전, 버킷 정책, 퍼블릭 차단과 무관한 IAM 권한 확인

4. **유사도 결과가 0 또는 낮음**
   - 입력 이미지 품질, 얼굴 정면 여부, 조명 조건을 조정
   - `SIMILARITY_THRESHOLD`를 70~90 범위에서 실험

---

## 9) 비용/보안 정리

실습 후 반드시 아래를 수행하세요.

- 불필요한 Lambda 함수 삭제
- 테스트 객체 정리: `./scripts/aws_batch_ops.sh cleanup`
- Access Key 미사용 시 비활성화/삭제
- CloudWatch 로그 보존 기간 설정

---

## 10) 참고

- Amazon Rekognition Docs: https://docs.aws.amazon.com/rekognition/
- AWS Lambda Docs: https://docs.aws.amazon.com/lambda/
- AWS CLI Docs: https://docs.aws.amazon.com/cli/

---

## 부록) 메인 폴더 문서 통합본 (워크플로우 순서)

아래는 메인(루트) 폴더의 Markdown 문서를 실습 워크플로우 순서로 통합한 내용입니다.

워크플로우 순서: **IAM 개념 이해 → 로컬 실행 → S3 운영 → Lambda 운영/백업**

---

### 원문: `Readme4.md` — IAM 핵심 개념 정리: Principal vs AssumeRole

이 문서는 IAM 정책을 읽을 때 가장 많이 등장하는 두 개념인 **Principal**과 **AssumeRole**을 실무 관점에서 정리합니다.
처음 AWS 권한 모델을 접할 때 헷갈리는 포인트를 예시 중심으로 설명합니다.

---

## 1) Principal이란?

Principal은 AWS 리소스에 접근을 시도하는 **주체**입니다.

예시:
- IAM 사용자: `"AWS": "arn:aws:iam::1234********:user/ab***"`
- IAM 역할: `"AWS": "arn:aws:iam::1234********:role/Developer"`
- AWS 서비스: `"Service": "lambda.amazonaws.com"`
- 계정 루트: `"AWS": "arn:aws:iam::1234********:root"`

Lambda가 역할을 사용할 수 있도록 허용하는 예:
```json
"Principal": {
  "Service": "lambda.amazonaws.com"
}
```

핵심 포인트:
- Principal은 **누가 요청하는지**를 나타냅니다.
- Principal만 있다고 권한이 생기지는 않으며, 정책의 `Action`/`Resource` 조건을 함께 만족해야 합니다.

---

## 2) AssumeRole이란?

`sts:AssumeRole`은 Principal이 특정 Role의 권한을 **임시로 위임받아 사용**하도록 허용하는 액션입니다.

신뢰 정책(Trust Policy) 예시:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::1234********:user/ab***"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

핵심 포인트:
- AssumeRole 성공 시 영구 키가 아닌 **임시 자격증명(AccessKey/Secret/SessionToken)** 이 발급됩니다.
- 임시 권한은 만료시간이 있어 보안상 유리합니다.
- Role 신뢰 정책(누가 Assume 가능한가)과 권한 정책(무엇을 할 수 있는가)은 별개입니다.

---

## 3) 정책 구조를 읽는 방법

IAM 정책을 읽을 때는 다음 순서로 보면 이해가 빠릅니다.
1. **누가(Principal)** 요청하는가?
2. **무엇을(Action)** 하려는가?
3. **어디에(Resource)** 수행하는가?
4. **어떤 조건(Condition)** 이 필요한가?

이 4개를 분리해 읽으면 복잡한 정책도 빠르게 디버깅할 수 있습니다.

---

## 4) 요약

- Principal: “누가 역할을 사용할 수 있는가?”
- `sts:AssumeRole`: “그 역할 사용을 허용하는 액션”
- Role Trust Policy: “누가 이 Role을 Assume 가능한가”
- Role Permission Policy: “Assume 후 어떤 AWS 작업을 할 수 있는가”

---

## 5) 실무 예시 (Lambda → S3)

1. `LambdaAccessRole` 생성
2. 해당 역할에 S3 권한 정책 연결
3. 역할의 Trust Policy에서 Lambda 서비스 Principal 허용

```json
{
  "Effect": "Allow",
  "Principal": {
    "Service": "lambda.amazonaws.com"
  },
  "Action": "sts:AssumeRole"
}
```

이후 Lambda 함수는 실행 시 해당 역할을 자동 Assume 하여 S3에 접근할 수 있습니다.

---

## 6) 자주 하는 실수

- Trust Policy에 `Principal` 누락
- Permission Policy만 설정하고 Trust Policy를 비워둠
- Lambda 실행 Role에 S3 `GetObject`만 주고 `ListBucket`이 필요한 케이스를 누락
- 교차 계정에서 외부 ID(`sts:ExternalId`) 조건을 설정하지 않음

문제 해결 팁:
- CloudTrail에서 `AssumeRole` 실패 이벤트를 확인
- `aws sts assume-role` CLI로 수동 재현
- 정책 시뮬레이터(IAM Policy Simulator)로 최소 재현 케이스 검증

---

### 원문: `Readme2.md` — 실행 가이드 (로컬 환경)

이 문서는 로컬 PC에서 AWS Rekognition 예제를 빠르게 실행해 보는 실습형 가이드입니다.
"명령은 실행되는데 결과가 안 나온다"는 상황을 줄이기 위해, **실행 전 점검 → 실행 → 문제 해결** 순서로 정리했습니다.

---

## 1) Node 버전 확인/선택

이 레포는 Node.js 18 계열을 기준으로 작성되어 있습니다.

```bash
nvm ls
nvm use 18.12.0
node -v
npm -v
```

- `nvm use` 이후 `node -v`가 기대 버전인지 확인하세요.
- 팀 환경이라면 `.nvmrc`를 두고 버전을 고정하는 방식을 권장합니다.

---

## 2) 의존성 설치

프로젝트 루트(또는 `server` 폴더 기준)에서 패키지를 먼저 설치합니다.

```bash
npm install
```

설치 후 `package-lock.json`이 변경되면 팀원과 동일한 버전으로 맞추는 데 도움이 됩니다.

---

## 3) 기본 실행 명령

```bash
npm run compare
npm run extract
npm run upload
```

각 명령의 의미:
- `npm run compare`: 두 얼굴 이미지의 유사도를 계산해 콘솔에 출력
- `npm run extract`: 이미지 내 텍스트를 감지(DetectText)
- `npm run upload`: 실습 이미지를 S3 버킷으로 업로드

### 권장 실행 순서
1. `upload`로 샘플 이미지를 먼저 S3에 업로드
2. `compare`로 유사도 비교 결과 확인
3. `extract`로 OCR 결과 확인

---

## 4) S3 연동을 위한 `.env` 설정

최소 설정 예시는 아래와 같습니다.

```env
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=your-bucket-name
S3_BUCKET_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

설정 체크 포인트:
- `AWS_REGION`과 `S3_BUCKET_REGION`이 다르면 업로드/조회가 실패할 수 있습니다.
- `S3_BUCKET_NAME`은 전역에서 유일해야 하며, 이미 사용 중이면 다른 이름을 사용해야 합니다.
- 운영에서는 정적 키 대신 IAM Role/SSO 사용을 권장합니다.

---

## 5) IAM 권한(학습용)

학습 단계에서는 아래 관리형 정책으로 빠르게 검증할 수 있습니다.
- `AmazonRekognitionFullAccess`
- `AmazonS3FullAccess`

> 운영 환경에서는 반드시 최소 권한 원칙을 적용하세요.
> 예: 특정 버킷 ARN만 허용, 필요한 Rekognition API만 허용, `Condition`으로 리전/리소스 제한.

---

## 6) 자주 발생하는 오류와 점검 방법

### 6-1. `AccessDeniedException`
- 원인: IAM 권한 부족 또는 다른 계정 자격증명 사용
- 점검:
  ```bash
  aws sts get-caller-identity
  ```

### 6-2. `NoSuchBucket`
- 원인: 버킷명이 틀렸거나 리전이 다름
- 점검:
  ```bash
  aws s3api head-bucket --bucket your-bucket-name
  ```

### 6-3. `InvalidSignatureException` 또는 시간 관련 오류
- 원인: 로컬 시스템 시간 불일치
- 점검: OS 시간 자동 동기화(NTP) 활성화

---

## 7) 실습 이미지 자료

아래 이미지는 실습 절차 참고용입니다.
- `image-3.png` ~ `image-11.png`

추가 팁:
- 얼굴 비교는 해상도가 너무 낮으면 정확도가 떨어집니다.
- 텍스트 추출은 대비가 높은 이미지에서 더 안정적입니다.

---

### 원문: `Readme3.md` — S3 퍼블릭 접근 & Lifecycle 실습 정리

이 문서는 S3 버킷의 공개 접근 제어와 Lifecycle(자동 만료) 설정을 실습 관점에서 설명합니다.
보안 사고를 예방하기 위해, **퍼블릭 접근은 반드시 필요할 때만 최소 범위로 열어야** 합니다.

---

## 1) 버킷 생성

- S3 콘솔: https://s3.console.aws.amazon.com/s3/
- 버킷명: `your-bucket-name` (전역 고유)
- 리전: `ap-northeast-2`

버킷 생성 시 권장사항:
- 버킷 이름에 팀/프로젝트/환경(dev, stg, prod)을 포함
- 기본 암호화(SSE-S3 또는 SSE-KMS) 활성화
- 버전 관리(Versioning) 필요 여부를 사전에 결정

---

## 2) 업로드 확인

```bash
npm run upload
```

실행 후 버킷에 객체가 업로드되었는지 확인합니다.

CLI로 확인:
```bash
aws s3 ls s3://your-bucket-name/
```

---

## 3) 퍼블릭 접근 점검 체크리스트

퍼블릭 공개는 **계정 수준 설정 + 버킷 정책 + 객체 ACL**이 함께 영향을 줍니다.

### 3-1. 퍼블릭 액세스 차단 설정 확인

```bash
aws s3api get-public-access-block --bucket your-bucket-name
```

확인 포인트:
- `BlockPublicAcls`
- `IgnorePublicAcls`
- `BlockPublicPolicy`
- `RestrictPublicBuckets`

이 값이 `true`이면 퍼블릭 정책을 넣어도 실제 접근이 차단될 수 있습니다.

### 3-2. 버킷 정책 적용/확인

```bash
aws s3api put-bucket-policy --bucket your-bucket-name --policy file://bucket.json
aws s3api get-bucket-policy-status --bucket your-bucket-name
```

버킷 정책 예시:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

주의사항:
- 퍼블릭 공개는 `GetObject`만 허용하고, `PutObject/DeleteObject`는 절대 공개하지 마세요.
- 가능하면 CloudFront + OAC로 비공개 S3를 유지하는 구조를 권장합니다.

### 3-3. 객체 ACL 확인

```bash
aws s3api get-object-acl --bucket your-bucket-name --key file.jpg
```

필요 시 업로드 시점 ACL:
```bash
aws s3 cp file.jpg s3://your-bucket-name/ --acl public-read
```

권장 사항:
- 최신 운영 패턴에서는 ACL보다 버킷 정책 중심 제어를 선호합니다.
- Object Ownership을 `Bucket owner enforced`로 쓰는 경우 ACL 사용이 제한됩니다.

### 3-4. 접근 URL 형식 확인

- `https://your-bucket-name.s3.amazonaws.com/image.jpg`
- `https://your-bucket-name.s3.ap-northeast-2.amazonaws.com/image.jpg`

리전별 엔드포인트가 다를 수 있으므로 실제 버킷 리전을 기준으로 URL을 구성하세요.

---

## 4) Lifecycle(자동 삭제) 설정

Lifecycle은 임시 실습 데이터, 로그, 백업 파일의 보관 비용을 줄이는 데 유용합니다.

설정 적용:
```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket your-bucket-name \
  --lifecycle-configuration file://delete.json
```

예시(`delete.json`):
```json
{
  "Rules": [
    {
      "ID": "AutoDeleteAfter1Days",
      "Filter": { "Prefix": "" },
      "Status": "Enabled",
      "Expiration": { "Days": 1 }
    }
  ]
}
```

> `Day`가 아닌 `Days` 필드를 사용해야 합니다.

확인 명령:
```bash
aws s3api get-bucket-lifecycle-configuration --bucket your-bucket-name
```

---

## 5) 운영 시 주의사항

- Lifecycle은 즉시 반영되지 않으며 보통 24~48시간 내 처리될 수 있습니다.
- 조직 계정 사용 시 SCP/IAM 정책으로 퍼블릭 접근이 제한될 수 있습니다.
- 규정 준수(Compliance)가 필요한 데이터는 자동 삭제 정책과 별도로 보존 정책 검토가 필요합니다.
- 비용 추적을 위해 버킷 태그(`Project`, `Owner`, `Environment`)를 권장합니다.

---

## 6) 권장 아키텍처(실무)

학습 단계 이후에는 아래 구조를 권장합니다.
1. S3 버킷은 비공개 유지
2. CloudFront 배포 생성
3. Origin Access Control(OAC)로 CloudFront만 S3 접근 허용
4. WAF/서명 URL로 공개 범위 제어

이 방식은 퍼블릭 버킷 대비 보안성과 운영 제어 측면에서 더 안전합니다.

---

### 원문: `Lambda.md` — Lambda 운영/백업 실습 가이드

이 문서는 AWS Lambda 함수를 조회하고 백업하는 기본 운영 절차를 정리한 문서입니다.
특히 여러 함수가 있는 계정에서 "현재 배포 상태를 점검"하거나 "코드/설정 백업"이 필요할 때 활용할 수 있습니다.

---

## 1) Lambda 함수 목록 확인

현재 설정된 `AWS_PROFILE`, `AWS_REGION` 기준으로 함수 이름만 조회:

```bash
aws lambda list-functions --query 'Functions[].FunctionName' --output table
```

이름/런타임/수정 시각까지 JSON으로 확인:

```bash
aws lambda list-functions --query 'Functions[].{Name:FunctionName,Runtime:Runtime,LastModified:LastModified}' --output json
```

팁:
- 결과가 없으면 `AWS_REGION` 또는 `AWS_PROFILE`이 다른 환경으로 잡혀 있을 수 있습니다.
- 먼저 아래 명령으로 현재 자격증명 컨텍스트를 확인하세요.

```bash
aws sts get-caller-identity
aws configure list
```

---

## 2) jq 설치 (출력 가공용)

Linux/Ubuntu 환경에서 JSON 파싱을 위해 `jq` 설치:

```bash
sudo apt-get update && sudo apt-get install -y jq
```

`jq`를 사용하면 대량 함수 목록에서 필요한 필드만 추출하기 쉽습니다.

예:
```bash
aws lambda list-functions --output json | jq '.Functions[] | {name:.FunctionName, role:.Role}'
```

---

## 3) 백업 스크립트 실행

실행 권한 부여:

```bash
chmod +x backup_all_lambdas.sh
```

프로파일/리전 지정 후 실행:

```bash
AWS_PROFILE=default AWS_REGION=ap-northeast-2 ./backup_all_lambdas.sh
```

일반적으로 백업 스크립트는 아래 항목을 저장합니다.
- 함수 코드(zip)
- 함수 설정(JSON)
- 환경변수/런타임/메모리/타임아웃 정보

---

## 4) 백업 전 체크리스트

- 백업 저장 경로 용량 확보
- 민감정보(.env, 비밀키)가 출력물에 포함되는지 확인
- KMS 암호화 함수라면 복호화/재배포 권한이 있는지 확인
- 교차 계정 함수일 경우 대상 계정 권한 위임(AssumeRole) 준비

---

## 5) 운영 권장사항

- 정기 백업: cron 또는 CI 파이프라인으로 주기 실행
- 버전 관리: 날짜/커밋 해시 기준으로 폴더 구분
- 복구 리허설: 백업이 "진짜 복구 가능한지" 분기별 점검
- 최소 권한: `lambda:GetFunction`, `lambda:GetFunctionConfiguration` 중심 권한 설계

---

## 6) 트러블슈팅

### `AccessDeniedException`
- 원인: Lambda 조회/다운로드 권한 부족
- 대응: IAM 정책에 `lambda:ListFunctions`, `lambda:GetFunction` 추가

### `ResourceNotFoundException`
- 원인: 함수명 오타 또는 리전 불일치
- 대응: `aws lambda list-functions --region ...`로 실제 함수 존재 확인

### 다운로드 링크 만료
- 원인: `GetFunction`의 코드 URL은 시간 제한이 있음
- 대응: 백업 시 즉시 다운로드하도록 스크립트 구성
