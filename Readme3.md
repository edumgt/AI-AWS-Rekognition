# S3 퍼블릭 접근 & Lifecycle 실습 정리

## 1) 버킷 생성
- S3 콘솔: https://s3.console.aws.amazon.com/s3/
- 버킷명: `your-bucket-name` (전역 고유)
- 리전: `ap-northeast-2`

## 2) 업로드 확인
```bash
npm run upload
```

실행 후 버킷에 객체가 업로드되었는지 확인합니다.

## 3) 퍼블릭 접근 점검 체크리스트

### 3-1. 퍼블릭 액세스 차단 설정 확인
```bash
aws s3api get-public-access-block --bucket your-bucket-name
```

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

### 3-3. 객체 ACL 확인
```bash
aws s3api get-object-acl --bucket your-bucket-name --key file.jpg
```

필요 시 업로드 시점 ACL:
```bash
aws s3 cp file.jpg s3://your-bucket-name/ --acl public-read
```

### 3-4. 접근 URL 형식 확인
- `https://your-bucket-name.s3.amazonaws.com/image.jpg`
- `https://your-bucket-name.s3.ap-northeast-2.amazonaws.com/image.jpg`

## 4) Lifecycle(자동 삭제) 설정

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

## 5) 운영 시 주의사항
- Lifecycle은 즉시 반영되지 않으며 보통 24~48시간 내 처리될 수 있습니다.
- 조직 계정 사용 시 SCP/IAM 정책으로 퍼블릭 접근이 제한될 수 있습니다.
