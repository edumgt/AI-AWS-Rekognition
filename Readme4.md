# IAM 핵심 개념 정리: Principal vs AssumeRole

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

## 3) 요약
- Principal: “누가 역할을 사용할 수 있는가?”
- `sts:AssumeRole`: “그 역할 사용을 허용하는 액션”

## 4) 실무 예시 (Lambda → S3)
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
