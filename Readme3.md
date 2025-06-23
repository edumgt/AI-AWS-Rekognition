## 퍼블릭 액세스 권한 부여
![alt text](image-13.png)

## 버킷 정책(Bucket Policy)이 퍼블릭을 허용하는지 확인 
## aws s3api put-bucket-policy --bucket edumgt-bucket-20250619 --policy file://bucket.json

## 결과
![alt text](image-14.png)

## 이미지 URL 노출
https://edumgt-bucket-0001.s3.ap-northeast-2.amazonaws.com/face1.png

가능

## 그외 체크 포인트
1. 퍼블릭 액세스 차단 정책 확인
S3 콘솔 → 버킷 선택 → 권한 → 퍼블릭 액세스 차단 설정

✅ "퍼블릭 액세스 차단"이 모두 꺼져 있어야 퍼블릭 사용자가 접근할 수 있습니다:


✔️ [ ] 새 ACL로 부여된 퍼블릭 액세스를 차단
✔️ [ ] 모든 퍼블릭 액세스 차단
🔁 aws cli 명령어로도 확인 가능:


aws s3api get-bucket-policy-status --bucket my-bucket-name
✅ 2. **버킷 정책(Bucket Policy)**이 퍼블릭을 허용하는지 확인
예시 (정적 웹사이트 호스팅 또는 이미지 공개에 사용):


{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket-name/*"
    }
  ]
}
적용:


aws s3api put-bucket-policy --bucket my-bucket-name --policy file://policy.json
✅ 3. 버킷 객체(Object)에 퍼블릭 권한이 부여되었는가
객체 단위로도 s3:GetObject 권한이 필요합니다

aws s3 cp로 업로드할 때 --acl public-read 옵션이 없다면 퍼블릭이 못 봅니다


aws s3 cp file.jpg s3://my-bucket-name/ --acl public-read
확인:


aws s3api get-object-acl --bucket my-bucket-name --key file.jpg
✅ 4. 올바른 URL로 접근 중인가
S3 객체에 접근하려면 URL은 아래 형식입니다:


https://my-bucket-name.s3.amazonaws.com/image.jpg
또는 리전 포함:


https://my-bucket-name.s3.ap-northeast-2.amazonaws.com/image.jpg
💡 경로가 403 AccessDenied를 반환한다면 오탈자, 확장자, 경로 오류일 가능성도 있습니다.

✅ 5. AWS Organizations or SCP 정책에서 제한되었는지 확인
만약 조직 계정 사용 중이라면, **Service Control Policy(SCP)**나 IAM 정책이 S3 퍼블릭 액세스를 막고 있을 수 있습니다.

🧪 진단 요약 명령어

# 버킷의 퍼블릭 정책 확인
aws s3api get-bucket-policy-status --bucket my-bucket-name

# ACL 확인
aws s3api get-bucket-acl --bucket my-bucket-name
aws s3api get-object-acl --bucket my-bucket-name --key your-file.jpg

## 파일 삭제 기한 생성 - 객체 아카이브 또는 지정된 기간이 지난 후 객체 삭제
![alt text](image-15.png)

![alt text](image-16.png)

객체 삭제 주기 Day 설정

## AWS Cli 로 설정
aws s3api put-bucket-lifecycle-configuration --bucket edumgt-bucket-0001 --lifecycle-configuration file://delete.json

## 결과
{
    "TransitionDefaultMinimumObjectSize": "all_storage_classes_128K"
}

![alt text](image-17.png)
![alt text](image-18.png)

## json 의 삭제 주기
{
  "Rules": [
    {
      "ID": "AutoDeleteAfter1Days",
      "Filter": {
        "Prefix": ""
      },
      "Status": "Enabled",
      "Expiration": {
        "Days": 1
      }
    }
  ]
}

## Error
Parameter validation failed:
Unknown parameter in LifecycleConfiguration.Rules[0].Expiration: "Day", must be one of: Date, Days, ExpiredObjectDeleteMarker 

## "Day" --> Days

## Expire 날짜 직접 지정 시 유의점
 1. S3 Lifecycle은 즉시 삭제하지 않습니다
S3는 비동기적으로 Lifecycle Rule을 실행합니다.
일반적으로 대상 날짜가 도달한 후 최대 24~48시간 이내에 삭제되며, 정확한 시간 보장은 없습니다.
백엔드에서 AWS의 내부 스케줄러가 주기적으로 해당 규칙을 평가하며 처리합니다.