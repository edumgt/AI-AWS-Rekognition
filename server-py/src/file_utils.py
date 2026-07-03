# 이미지 파일 존재 확인/버퍼 로딩 유틸리티입니다(Node 버전의 fileUtils.js와 동일한 역할).
import os


def resolve_existing_files(base_dir, file_names):
    # 기준 디렉터리와 파일명 목록을 받아 실제 존재하는 파일 정보만 반환합니다.
    resolved = []
    for file_name in file_names:
        file_path = os.path.join(base_dir, file_name)
        if os.path.exists(file_path):
            resolved.append({"file_name": file_name, "file_path": file_path})
    return resolved


def read_file_bytes(file_path):
    # Rekognition/S3 API에서 바로 사용할 수 있도록 원본 바이너리를 읽습니다.
    with open(file_path, "rb") as f:
        return f.read()
