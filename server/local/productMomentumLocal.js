const fs = require('fs');
const path = require('path');
const { ensureLinuxRuntime } = require('../src/runtimeGuard');
const { handler } = require('../lambda/productMomentumHandler');

ensureLinuxRuntime('lambda:product-momentum:local');

// 로컬 샘플 이미지를 시간순(오래된 -> 최신)으로 촬영된 소셜/뉴스 영상 프레임인 것처럼 가정합니다.
// 실제 운영에서는 유튜브/틱톡/인스타그램에서 추출한 프레임과 조회수/좋아요 등의
// 참여도(engagementScore)를 그대로 전달하면 됩니다.
const sampleFrames = ['face1.png', 'face3.png', 'face5.png', 'sample.png'].map((fileName, index) => ({
  imageBase64: fs.readFileSync(path.resolve(__dirname, '..', fileName)).toString('base64'),
  // 최신 프레임일수록 반응(조회/좋아요)이 커진다고 가정한 샘플 값입니다.
  engagementScore: (index + 1) * 10,
}));

handler({
  frames: sampleFrames,
  watchlist: ['Person', 'Face', 'Photography', 'Clothing'],
  minConfidence: 60,
})
  .then((result) => {
    console.log(result.body);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
