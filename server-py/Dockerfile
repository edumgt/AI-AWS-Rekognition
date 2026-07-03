FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 빌드 컨텍스트는 저장소 루트(../)를 기준으로 합니다(docker-compose.yml의 context: ".." 참고).
COPY server-py/requirements.txt server-py/requirements.txt
RUN pip install -r server-py/requirements.txt

COPY server-py/ server-py/
# 프런트엔드 정적 리소스는 server/web/public을 그대로 재사용합니다(중복 보관하지 않음).
COPY server/web/public/ server/web/public/
# 로컬 CLI/Lambda 핸들러가 참조하는 샘플 이미지도 함께 포함합니다.
COPY server/face1.png server/face2.jpg server/face3.png server/face4.jpg server/face5.png server/face6.png server/sample.png server/

WORKDIR /app/server-py

ENV WEB_HOST=0.0.0.0 \
    WEB_PORT=3100

EXPOSE 3100

CMD ["python", "web/app.py"]
