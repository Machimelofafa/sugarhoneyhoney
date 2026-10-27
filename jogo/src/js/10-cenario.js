// ===================================================================
// Cenário: base fixa, camadas animadas, esteiras, corações dos painéis,
// e as peças do fim: grade que sobe e desce, alçapão, vão aberto pelo raio
// ===================================================================
// índices da paleta → canvas; 255 = transparente (peças sobrepostas)
function indexCanvas(idx, w, h) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const cx = c.getContext('2d'), im = cx.createImageData(w, h);
  for (let i = 0; i < w * h; i++) {
    if (idx[i] === 255) continue;
    const p = PALRGB[idx[i]]; im.data[i * 4] = p[0]; im.data[i * 4 + 1] = p[1]; im.data[i * 4 + 2] = p[2]; im.data[i * 4 + 3] = 255;
  }
  cx.putImageData(im, 0, 0);
  return c;
}

const BASE = indexCanvas(unb64(A.base), W, H);
const LAYERS = {};
for (const name in A.layers) {
  const L = A.layers[name];
  LAYERS[name] = { x: L.x, y: L.y, frames: L.frames.map(f => indexCanvas(unb64(f), L.w, L.h)) };
}
const CONV = {};
for (const name in A.conv) {
  const c = A.conv[name], t = unb64(c.tile);
  // faixa com o padrão repetido, um período a mais para rolar sem emenda
  if (c.axis === 'x') {
    const n = c.w + 2 * c.P, idx = new Uint8Array(n * c.h);
    for (let r = 0; r < c.h; r++) for (let p = 0; p < n; p++) idx[r * n + p] = t[r * c.P + (p % c.P)];
    CONV[name] = Object.assign({}, c, { strip: indexCanvas(idx, n, c.h) });
  } else {
    const n = c.h + 2 * c.P, idx = new Uint8Array(c.w * n);
    for (let p = 0; p < n; p++) for (let col = 0; col < c.w; col++) idx[p * c.w + col] = t[col * c.P + (p % c.P)];
    CONV[name] = Object.assign({}, c, { strip: indexCanvas(idx, c.w, n) });
  }
}
function drawConv(c, step) {
  const shift = ((step * c.step) % c.P + c.P) % c.P;
  g.save(); g.beginPath(); g.rect(c.x, c.y, c.w, c.h); g.clip();
  if (c.axis === 'x') g.drawImage(c.strip, c.x + shift - c.P, c.y);
  else g.drawImage(c.strip, c.x, c.y + shift - c.P);
  g.restore();
}
function drawLayer(name, k) { const L = LAYERS[name]; g.drawImage(L.frames[k % L.frames.length], L.x, L.y); }
// fosso: cada chama (FOGO.slots, em 40-fase.js) desenha as colunas dela tiradas do passo do vídeo que lhe cabe agora
function drawFogo(t) {
  const L = LAYERS.fire, col = quadrosPorColuna(t);
  g.drawImage(L.frames[FOGO.slots[2].apagado[0]], L.x, L.y);
  for (let c0 = 0; c0 < col.length;) {               // uma faixa por trecho de colunas no mesmo passo
    let c1 = c0; while (c1 + 1 < col.length && col[c1 + 1] === col[c0]) c1++;
    if (col[c0] >= 0) { const f = L.frames[col[c0]]; g.drawImage(f, c0, 0, c1 - c0 + 1, f.height, L.x + c0, L.y, c1 - c0 + 1, f.height); }
    c0 = c1 + 1;
  }
}

// ---------- grade e alçapão (plano 1495-1716 do vídeo) ----------
const GR = EXTRA.grade, AL = EXTRA.alcapao;
const GRADE_FUNDO = indexCanvas(unb64(GR.fundo), GR.w, GR.h);      // a parede entre os postes, sem a grade
const GRADE_IMG = indexCanvas(unb64(GR.grade), GR.w, GR.h);        // a grade toda embaixo (255 = vazado)
const ALC_IMG = AL.estados.map(s => indexCanvas(unb64(s), AL.w, AL.h));   // fechado, abrindo, aberto
const ALC_BAIXO = indexCanvas(unb64(AL.baixo.fechado), AL.w, AL.baixo.h); // tapa as abas penduradas da base
// a grade desce dy linhas da posição de cima (dy = 0: embaixo, encostada no teto; negativo: erguida)
function drawGrade(dy) {
  g.drawImage(GRADE_FUNDO, GR.x, GR.y);
  g.save(); g.beginPath(); g.rect(GR.x, GR.y, GR.w, GR.h); g.clip();
  g.drawImage(GRADE_IMG, GR.x, GR.y + Math.round(dy));
  g.restore();
}
function drawAlcapao(k) {
  if (k < 2) g.drawImage(ALC_BAIXO, AL.x, AL.baixo.y);
  g.drawImage(ALC_IMG[k], AL.x, AL.y);
}

// ---------- o vão que o raio abre no teto, entre a moça e o herói ----------
// beiradas em degraus como no plano do abraço: as faces quebradas do tampo (cinza-arroxeado, como os tampos do
// plano) e o escuro do fundo; a rachadura desce do tampo pela frente do teto
const DEGRAUS = [0, 0, 1, 1, 1, 2, 2, 1, 1, 0, 0, 1, 2, 2, 2, 1];
function drawVao(v, abre) {
  const fundo = 104, mostra = Math.min(1, abre) * (fundo - 55);
  for (let r = 55; r <= fundo; r++) {
    const k = r - 55;
    if (k > mostra) break;
    const l = v.x0 + DEGRAUS[(k >> 1) % DEGRAUS.length], d = v.x1 - DEGRAUS[((k >> 1) + 5) % DEGRAUS.length];
    for (let x = l; x <= d; x++) R(g, x, r, 1, 1, PAL[r <= 57 ? 3 : 0]);
    if (r >= 58) {
      const face = r <= 72 ? 12 : 1;                       // faces quebradas: claras no tampo, escuras na frente
      R(g, l, r, 1, 1, PAL[face]); R(g, d, r, 1, 1, PAL[face]);
      if (r <= 72) { R(g, l + 1, r, 1, 1, PAL[6]); R(g, d - 1, r, 1, 1, PAL[6]); }
    }
  }
}
// o raio (quadro 1803) e o estouro do golpe (quadro 576), na grade do cenário
const RAIO_IMG = indexCanvas(unb64(EXTRA.raio.px), EXTRA.raio.w, EXTRA.raio.h);
const IMPACTO_IMG = indexCanvas(unb64(EXTRA.impacto.px), EXTRA.impacto.w, EXTRA.impacto.h);
function drawRaio(x, yPe) { g.drawImage(RAIO_IMG, Math.round(x - RAIO_IMG.width / 2), Math.round(yPe - RAIO_IMG.height)); }
function drawImpacto(x, y, esc) {
  const w = Math.round(IMPACTO_IMG.width * esc), h = Math.round(IMPACTO_IMG.height * esc);
  g.drawImage(IMPACTO_IMG, Math.round(x - w / 2), Math.round(y - h / 2), w, h);
}

// ---------- corações dos painéis ----------
function drawHearts(side, n) {
  const panel = A.hearts[side];
  for (let k = n; k < 4; k++) for (const [x, y] of panel[k].cells) R(g, x, y, 1, 1, PAL[panel[k].empty]);
}
function slotCenter(side, k) {
  const cells = A.hearts[side][k].cells;
  let sx = 0, sy = 0; for (const [x, y] of cells) { sx += x; sy += y; }
  return { x: sx / cells.length, y: sy / cells.length };
}
const HEART_RED = PAL[14], HEART_DARK = PAL[18];

// coração grande, por equação implícita, rasterizado na grade
function bigHeartMask(cx, cy, size) {
  const m = new Uint8Array(W * H);
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    const X = (i + 0.5 - cx) * ASPECT / size, Y = -(j + 0.5 - cy) / size;
    const a = X * X + Y * Y - 1;
    if (a * a * a - X * X * Y * Y * Y <= 0) m[j * W + i] = 1;
  }
  return m;
}
const at = (m, i, j) => i >= 0 && j >= 0 && i < W && j < H && m[j * W + i] === 1;
function drawBigHeart(cx, cy, size, crack) {
  const m = bigHeartMask(cx, cy, size);
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    if (!at(m, i, j)) {
      if (at(m, i - 1, j) || at(m, i + 1, j) || at(m, i, j - 1) || at(m, i, j + 1)) R(g, i, j, 1, 1, OUT);
      continue;
    }
    R(g, i, j, 1, 1, (!at(m, i + 1, j) || !at(m, i, j + 1)) ? HEART_DARK : HEART_RED);
  }
  if (crack) {
    let x = cx;
    for (let y = Math.floor(cy - size * 0.55); y < cy + size; y++) {
      if (!at(m, Math.round(x), y)) continue;
      x += ((y >> 2) % 2 ? 1 : -1) * 0.6;
      R(g, Math.round(x), y, 1, 1, OUT);
    }
  }
  return m;
}

// cenário completo de um quadro (sem atores)
function drawLevel() {
  const step = Math.floor(frame / STEP_FRAMES);
  g.drawImage(BASE, 0, 0);
  drawLayer('scaf', 3);                    // postes e moldura do alto; a grade e o alçapão vão por cima
  drawGrade(gradeDy());
  drawAlcapao(alcapaoQuadro());
  drawLayer('ramp', step);
  drawFogo(playFrames);
  for (const name in CONV) drawConv(CONV[name], step);
  g.drawImage(LAYERS.croc.frames[crocFrame()], LAYERS.croc.x, LAYERS.croc.y);
  if (vao.abre > 0) drawVao(VAO, vao.abre);
}
