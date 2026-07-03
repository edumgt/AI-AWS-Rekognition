# 얼굴 업로드 + 얼굴 비교 비즈니스 로직입니다(Node 버전의 faceWorkflow.js와 동일한 역할).
from .aws_clients import get_rekognition, get_s3
from .config import get_config
from .file_utils import read_file_bytes, resolve_existing_files


def upload_faces(base_dir):
    # 로컬 얼굴 파일을 S3의 training/ 경로로 업로드합니다.
    config = get_config()
    s3 = get_s3()

    existing = resolve_existing_files(base_dir, config["face_files"])
    if not existing:
        return {"uploaded": [], "skipped": config["face_files"]}

    existing_names = {entry["file_name"] for entry in existing}
    skipped = [name for name in config["face_files"] if name not in existing_names]

    uploaded = []
    for entry in existing:
        key = f"training/{entry['file_name']}"
        s3.put_object(
            Bucket=config["bucket_name"],
            Key=key,
            Body=read_file_bytes(entry["file_path"]),
            ContentType="image/png",
        )
        uploaded.append(key)

    return {"uploaded": uploaded, "skipped": skipped}


def compare_faces(base_dir):
    # 로컬 얼굴 파일들 간 모든 조합을 Rekognition으로 비교합니다.
    config = get_config()
    rekognition = get_rekognition()
    existing = resolve_existing_files(base_dir, config["face_files"])
    comparisons = []

    for i in range(len(existing)):
        for j in range(i + 1, len(existing)):
            source = existing[i]
            target = existing[j]
            response = rekognition.compare_faces(
                SourceImage={"Bytes": read_file_bytes(source["file_path"])},
                TargetImage={"Bytes": read_file_bytes(target["file_path"])},
                SimilarityThreshold=config["similarity_threshold"],
            )
            face_matches = response.get("FaceMatches", [])
            max_similarity = face_matches[0]["Similarity"] if face_matches else 0

            comparisons.append(
                {
                    "source": source["file_name"],
                    "target": target["file_name"],
                    "matched": len(face_matches) > 0,
                    "similarity": round(max_similarity, 2),
                }
            )

    existing_names = {entry["file_name"] for entry in existing}
    missing = [name for name in config["face_files"] if name not in existing_names]

    return {
        "compared_count": len(comparisons),
        "comparisons": comparisons,
        "missing": missing,
    }
