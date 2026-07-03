# boto3 세션/클라이언트 생성을 담당합니다(Node 버전의 awsClients.js와 동일한 역할).
import boto3

from .config import get_aws_region

_session = None


def _get_session():
    # Rekognition/S3 공통으로 필요한 AWS 리전만 지연 초기화합니다.
    global _session
    if _session is None:
        # Lambda에서는 Execution Role 기반 자격증명을 사용해야 합니다.
        # access key/secret key를 수동 주입하지 않고 boto3 기본 자격증명 체인을 사용합니다.
        _session = boto3.session.Session(region_name=get_aws_region())
    return _session


def get_s3():
    # S3 업로드/다운로드에 사용할 클라이언트를 생성해 반환합니다.
    return _get_session().client("s3")


def get_rekognition():
    # Rekognition 분석 API 호출에 사용할 클라이언트를 생성해 반환합니다.
    return _get_session().client("rekognition")
