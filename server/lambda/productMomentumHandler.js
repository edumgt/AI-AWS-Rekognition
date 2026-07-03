// Rekognition 클라이언트 팩토리를 불러옵니다.
const { getRekognition } = require('../src/awsClients');

const CORS_HEADERS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': 'https://www.naver.com',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

// 요청 페이로드를 파싱합니다.
function parsePayload(event) {
  return typeof event.body === 'string' ? JSON.parse(event.body) : event;
}

function decodeBase64Image(value, index) {
  if (!value) throw new Error(`Missing imageBase64 for frames[${index}]`);
  return Buffer.from(value, 'base64');
}

// 프레임 한 장에 대해 Object & Scene Detection(DetectLabels)을 호출합니다.
async function detectFrameLabels(rekognition, frame, index, minConfidence, maxLabels) {
  const imageBytes = decodeBase64Image(frame.imageBase64, index);
  const result = await rekognition
    .detectLabels({
      Image: { Bytes: imageBytes },
      MinConfidence: minConfidence,
      MaxLabels: maxLabels,
    })
    .promise();

  return (result.Labels || []).map((label) => ({
    name: label.Name,
    confidence: Number((label.Confidence || 0).toFixed(2)),
  }));
}

function normalizeTarget(value) {
  return String(value || '').trim().toLowerCase();
}

// 감지된 레이블 중 감시 대상(신제품/브랜드 카테고리) 키워드와 부분 일치하는 항목을 찾습니다.
function findMatch(labels, targetNormalized) {
  return labels.find((label) => label.name.toLowerCase().includes(targetNormalized));
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

// 워치리스트 항목별로 노출 빈도, 반응(참여도) 가중치, 상승/하락 모멘텀을 집계합니다.
// frames는 시간순(오래된 -> 최신)으로 정렬되어 있다고 가정합니다.
function buildMomentumReport(watchlist, frameLabels, engagementScores) {
  const totalFrames = frameLabels.length;
  const totalEngagement = engagementScores.reduce((sum, v) => sum + v, 0) || totalFrames;
  const midpoint = Math.ceil(totalFrames / 2);

  return watchlist
    .map((rawTarget) => {
      const targetNormalized = normalizeTarget(rawTarget);
      const matches = [];

      frameLabels.forEach((labels, frameIndex) => {
        const match = findMatch(labels, targetNormalized);
        if (match) matches.push({ frameIndex, confidence: match.confidence });
      });

      const exposureCount = matches.length;
      const exposureRate = totalFrames > 0 ? exposureCount / totalFrames : 0;
      const avgConfidence =
        exposureCount > 0 ? matches.reduce((sum, m) => sum + m.confidence, 0) / exposureCount : 0;
      const weightedExposure =
        totalEngagement > 0
          ? matches.reduce((sum, m) => sum + (engagementScores[m.frameIndex] || 0), 0) / totalEngagement
          : 0;

      // 프레임을 앞/뒤 절반으로 나눠 노출 빈도 변화율(모멘텀)을 계산합니다.
      const earlyMatches = matches.filter((m) => m.frameIndex < midpoint).length;
      const lateMatches = matches.filter((m) => m.frameIndex >= midpoint).length;
      const earlyRate = midpoint > 0 ? earlyMatches / midpoint : 0;
      const lateRate = totalFrames - midpoint > 0 ? lateMatches / (totalFrames - midpoint) : 0;
      const momentumDelta = lateRate - earlyRate;

      // 노출 빈도(40) + 참여도 가중 노출 비중(30) + 평균 신뢰도(15) + 상승 모멘텀(15)의 가중합입니다.
      const momentumScore = clamp(
        exposureRate * 40 + weightedExposure * 30 + (avgConfidence / 100) * 15 + Math.max(momentumDelta, 0) * 15,
        0,
        100,
      );

      const momentumTrend = momentumDelta > 0.1 ? 'RISING' : momentumDelta < -0.1 ? 'DECLINING' : 'STABLE';

      return {
        target: rawTarget,
        exposureCount,
        totalFrames,
        exposureRate: Number((exposureRate * 100).toFixed(1)),
        weightedExposureShare: Number((weightedExposure * 100).toFixed(1)),
        avgConfidence: Number(avgConfidence.toFixed(2)),
        momentumDelta: Number((momentumDelta * 100).toFixed(1)),
        momentumTrend,
        momentumScore: Number(momentumScore.toFixed(1)),
        matchedFrameIndexes: matches.map((m) => m.frameIndex),
      };
    })
    .sort((a, b) => b.momentumScore - a.momentumScore);
}

exports.handler = async (event = {}) => {
  // CORS preflight
  if (event.requestContext?.http?.method === 'OPTIONS' || event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: CORS_HEADERS, body: '' };
  }

  try {
    const payload = parsePayload(event);
    const frames = Array.isArray(payload.frames) ? payload.frames : [];
    const watchlist = Array.isArray(payload.watchlist) ? payload.watchlist.filter(Boolean) : [];
    const minConfidence = Number(payload.minConfidence || 60);
    const maxLabels = Number(payload.maxLabels || 20);

    if (frames.length === 0) {
      throw new Error('Missing required field: frames (array of { imageBase64, engagementScore? })');
    }
    if (watchlist.length === 0) {
      throw new Error('Missing required field: watchlist (array of target label keywords)');
    }

    const rekognition = getRekognition();

    // 프레임을 순서대로(시간순) 분석해야 모멘텀(초반 vs 후반 노출 변화) 계산이 유효합니다.
    const frameLabels = [];
    for (let i = 0; i < frames.length; i += 1) {
      // eslint-disable-next-line no-await-in-loop
      const labels = await detectFrameLabels(rekognition, frames[i], i, minConfidence, maxLabels);
      frameLabels.push(labels);
    }

    const engagementScores = frames.map((frame) => Number(frame.engagementScore ?? 1));
    const report = buildMomentumReport(watchlist, frameLabels, engagementScores);

    return {
      statusCode: 200,
      headers: CORS_HEADERS,
      body: JSON.stringify({
        totalFrames: frames.length,
        watchlist,
        report,
        frameLabels: frameLabels.map((labels, index) => ({ frameIndex: index, labels })),
      }),
    };
  } catch (error) {
    return {
      statusCode: 400,
      headers: CORS_HEADERS,
      body: JSON.stringify({ message: error.message }),
    };
  }
};
