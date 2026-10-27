// ===================================================================
// Telas: título (a faixa dos olhos), fim de jogo, fim da partida
// ===================================================================
function dim(a) { g.fillStyle = `rgba(4,3,10,${a})`; g.fillRect(0, 0, W, H); }

// ---------- tela-título: a faixa dos olhos da abertura, entre dois fios vermelhos ----------
// Os blocos do mosaico vêm do próprio vídeo (quadros 38-98, ferramentas/video/olhos.py); a faixa abre como na
// abertura e os olhos olham para um lado e para o outro. O fundo da grade fica preto; os olhos vão na saída (present).
const OLHOS = A.olhos;
let olhosImg = null;
(() => { const im = new Image(); im.onload = () => { olhosImg = im; }; im.src = OLHOS.img; })();
function drawTitle() { R(g, 0, 0, W, H, '#000000'); }
function drawOlhos(ctx, T) {
  if (!olhosImg) return;
  const o = OLHOS, meio = (o.fio[0][0] + o.fio[1][1] + 1) / 2;
  const abre = Math.min(1, T / 24);                                  // a faixa abre do meio em ~0,4 s
  const topo = meio + (o.fio[0][0] - meio) * abre, base = meio + (o.fio[1][1] + 1 - meio) * abre;
  const fio = (o.fio[0][1] - o.fio[0][0] + 1) * Math.min(1, 0.35 + abre);
  const y0 = topo + fio, y1 = Math.max(y0, base - fio), sy = (y1 - y0) / (o.y1 - o.y0);
  const k = Math.floor(T / 90) % o.quadros.length;
  ctx.save();
  ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = '#c1000c';
  ctx.fillRect(0, topo * F, 1408 * F, fio * F);
  ctx.fillRect(0, (base - fio) * F, 1408 * F, fio * F);
  ctx.beginPath(); ctx.rect(0, y0 * F, 1408 * F, (y1 - y0) * F); ctx.clip();
  ctx.drawImage(olhosImg, 0, k * o.ny, o.nx, o.ny, o.ox * F, (y0 + o.oy * sy) * F, o.nx * o.px * F, o.ny * o.py * sy * F);
  ctx.restore();
}

function drawOver() {
  const T = stateT;
  if (T < 40) { drawLevel(); drawHud(); dim(T / 40 * 0.7); return; }
  R(g, 0, 0, W, H, '#000000');
  const cx = 85, cy = 110, size = 36;
  if (T < 90) { drawBigHeart(cx, cy, size, T > 60); return; }
  if (!overData.pieces) {
    const m = bigHeartMask(cx, cy, size), pcs = [];
    for (let j = 0; j < H; j += 6) for (let i = 0; i < W; i += 3) {
      let any = false; for (let y = j; y < j + 6; y++) for (let x = i; x < i + 3; x++) if (at(m, x, y)) any = true;
      if (any) pcs.push({ x: i, y: j, vx: (i + 1.5 - cx) * 0.012 + (Math.random() - 0.5) * 0.2, vy: -Math.random() * 1.2, m, ox: i, oy: j, rest: 160 + Math.random() * 16 });
    }
    overData.pieces = pcs;
    noise(0.3, 0.08);
  }
  for (const p of overData.pieces) {
    p.vy += 0.07; p.x += p.vx; p.y += p.vy;
    if (p.y > p.rest) { p.y = p.rest; p.vy *= -0.25; p.vx *= 0.6; }
    for (let y = 0; y < 6; y++) for (let x = 0; x < 3; x++) if (at(p.m, p.ox + x, p.oy + y)) R(g, Math.round(p.x) + x, Math.round(p.y) + y, 1, 1, (x === 2 || y === 5) ? HEART_DARK : HEART_RED);
  }
}
function drawWin() {
  drawLevel(); drawHud();
  if (winData.fimT >= 0) dim(1);
}
