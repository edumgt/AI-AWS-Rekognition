# 실행 가이드 (로컬 환경)

## 1) Node 버전 확인/선택
```bash
nvm ls
nvm use 18.12.0
```

## 2) 기본 실행 명령
```bash
npm run compare
npm run extract
npm run upload
```

## 3) S3 연동을 위한 `.env` 추가 항목
```env
S3_BUCKET_NAME=your-bucket-name
S3_BUCKET_REGION=ap-northeast-2
```

## 4) IAM 권한(학습용)
- 동일 IAM 사용자에 다음 권한을 연결하여 실습
  - `AmazonRekognitionFullAccess`
  - `AmazonS3FullAccess`

> 운영 환경에서는 반드시 최소 권한 원칙으로 커스텀 정책을 사용하세요.

## 5) 실습 이미지 자료
아래 이미지는 실습 절차 참고용입니다.
- `image-3.png` ~ `image-11.png`
