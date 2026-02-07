const http = require('http');
const fs = require('fs');
const path = require('path');
const AWS = require('aws-sdk');
const { getConfig } = require('../src/config');

const region = process.env.AWS_REGION || getConfig().region;
const lambda = new AWS.Lambda({ region });
const compareFunctionName = process.env.LAMBDA_COMPARE_UPLOAD_FUNCTION || 'rekognition-face-compare-upload';
const textFunctionName = process.env.LAMBDA_TEXT_FUNCTION || 'rekognition-text-detect';

const publicDir = path.resolve(__dirname, 'public');

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(payload));
}

function parseRequestBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk.toString();
    });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (error) {
        reject(new Error('요청 JSON 형식이 올바르지 않습니다.'));
      }
    });
    req.on('error', reject);
  });
}

function parseLambdaPayload(response) {
  const payloadText = response.Payload ? Buffer.from(response.Payload).toString('utf-8') : '{}';
  const payload = payloadText ? JSON.parse(payloadText) : {};
  const body = payload.body ? JSON.parse(payload.body) : payload;

  return {
    statusCode: Number(payload.statusCode || 200),
    body,
  };
}

function buildLambdaEvent(body) {
  return {
    body: JSON.stringify(body),
  };
}

function serveStatic(req, res) {
  const requestPath = req.url === '/' ? '/index.html' : req.url;
  const filePath = path.resolve(publicDir, `.${requestPath}`);

  if (!filePath.startsWith(publicDir) || !fs.existsSync(filePath)) {
    res.writeHead(404);
    res.end('Not found');
    return;
  }

  const ext = path.extname(filePath);
  const typeMap = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
  };

  res.writeHead(200, { 'Content-Type': typeMap[ext] || 'text/plain; charset=utf-8' });
  fs.createReadStream(filePath).pipe(res);
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'POST' && req.url === '/api/compare') {
      const body = await parseRequestBody(req);
      if (!body.sourceImageBase64 || !body.targetImageBase64) {
        return sendJson(res, 400, { message: 'sourceImageBase64, targetImageBase64 값이 필요합니다.' });
      }

      const response = await lambda
        .invoke({
          FunctionName: compareFunctionName,
          InvocationType: 'RequestResponse',
          Payload: JSON.stringify(buildLambdaEvent({
            sourceImageBase64: body.sourceImageBase64,
            targetImageBase64: body.targetImageBase64,
            similarityThreshold: Number(body.similarityThreshold || 80),
          })),
        })
        .promise();

      const lambdaResult = parseLambdaPayload(response);
      return sendJson(res, lambdaResult.statusCode, lambdaResult.body);
    }

    if (req.method === 'POST' && req.url === '/api/extract-text') {
      const body = await parseRequestBody(req);
      if (!body.imageBase64) {
        return sendJson(res, 400, { message: 'imageBase64 값이 필요합니다.' });
      }

      const response = await lambda
        .invoke({
          FunctionName: textFunctionName,
          InvocationType: 'RequestResponse',
          Payload: JSON.stringify(buildLambdaEvent({ imageBase64: body.imageBase64 })),
        })
        .promise();

      const lambdaResult = parseLambdaPayload(response);
      return sendJson(res, lambdaResult.statusCode, lambdaResult.body);
    }

    serveStatic(req, res);
  } catch (error) {
    sendJson(res, 500, { message: error.message });
  }
});

const port = Number(process.env.WEB_PORT || 3000);
server.listen(port, () => {
  console.log(`Web demo started: http://localhost:${port}`);
});
