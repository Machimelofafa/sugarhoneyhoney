// ===================================================================
// Atores: recortes do vídeo da abertura, guardados num atlas.
// Na abertura os atores são vídeo com efeito de mosaico: blocos de tamanho fixo na tela
// (LX × LY px do quadro geral), cobertos ou não conforme o ator passa por cima.
// Aqui cada quadro é remosaicado ao vivo na mesma grade, então o movimento mistura as cores
// dos blocos como no original, em vez de deslizar sprites inteiros.
// ===================================================================
const LX = 6.95, LY = 8.8;               // bloco do mosaico, em px do quadro geral (1408 × 1058)
const OVX = 1408 / W, OVY = 1058 / H;    // px do quadro geral por célula do cenário
const ATLAS = A.atlas;
const SP = ATLAS.sprites;
const PXA = ATLAS.px;                    // px do quadro geral por px do atlas
let atlasData = null, atlasW = 0, atlasH = 0;

function carregarAtlas(pronto) {
  const img = new Image();
  img.onload = () => {
    const c = document.createElement('canvas'); c.width = atlasW = img.width; c.height = atlasH = img.height;
    const cx = c.getContext('2d'); cx.drawImage(img, 0, 0);
    atlasData = cx.getImageData(0, 0, atlasW, atlasH).data;
    pronto();
  };
  img.src = ATLAS.img;
}

// lista os ids que começam com o prefixo, em ordem
const seq = pref => Object.keys(SP).filter(k => k.startsWith(pref + '.')).sort();
const ANIM = {};
function montarAnimacoes() {
  for (const ator of ['hero', 'vil', 'girl']) {
    ANIM[ator] = {};
    for (const id of Object.keys(SP)) {
      if (!id.startsWith(ator + '.')) continue;
      const nome = id.split('.')[1];
      (ANIM[ator][nome] = ANIM[ator][nome] || []).push(id);
    }
    for (const n in ANIM[ator]) ANIM[ator][n].sort();
  }
  ANIM.duo = { duo: seq('duo') };
}

// área do bloco coberta por cada pixel do atlas, acumulada por bloco (cor premultiplicada)
let blocos = new Float32Array(4 * 64 * 64);
const tiny = document.createElement('canvas');
const tcx = tiny.getContext('2d');

// desenha o ator no canvas de saída. (xv, yv) = âncora em px do quadro geral; flip espelha; esc = tamanho do ator
// (no alto da fase o herói aparece menor no vídeo); o bloco do mosaico não muda com o tamanho, como na abertura.
function desenharAtor(ctx, F, id, xv, yv, flip, alfa, esc) {
  const s = SP[id]; if (!s || !atlasData) return;
  const sx = s.x, sy = s.y, w = s.w, h = s.h;
  const PXA = ATLAS.px * (esc || 1);
  const ax = flip ? w - s.ax : s.ax;
  const x0 = xv - ax * PXA, y0 = yv - s.ay * PXA;
  const bx0 = Math.floor(x0 / LX), by0 = Math.floor(y0 / LY);
  const bx1 = Math.ceil((x0 + w * PXA) / LX), by1 = Math.ceil((y0 + h * PXA) / LY);
  const nw = bx1 - bx0, nh = by1 - by0;
  if (blocos.length < nw * nh * 4) blocos = new Float32Array(nw * nh * 4);
  blocos.fill(0, 0, nw * nh * 4);
  for (let j = 0; j < h; j++) {
    const py0 = y0 + j * PXA, py1 = py0 + PXA;
    const r0 = Math.floor(py0 / LY), r1 = Math.floor((py1 - 1e-6) / LY);
    for (let i = 0; i < w; i++) {
      const si = flip ? w - 1 - i : i;
      const o = ((sy + j) * atlasW + sx + si) * 4;
      const a = atlasData[o + 3]; if (a < 8) continue;
      const px0 = x0 + i * PXA, px1 = px0 + PXA;
      const c0 = Math.floor(px0 / LX), c1 = Math.floor((px1 - 1e-6) / LX);
      const aa = a / 255, R = atlasData[o] * aa, G = atlasData[o + 1] * aa, B = atlasData[o + 2] * aa;
      for (let r = r0; r <= r1; r++) {
        const ov_y = Math.min(py1, (r + 1) * LY) - Math.max(py0, r * LY);
        for (let c = c0; c <= c1; c++) {
          const ar = ov_y * (Math.min(px1, (c + 1) * LX) - Math.max(px0, c * LX));
          const k = ((r - by0) * nw + (c - bx0)) * 4;
          blocos[k] += R * ar; blocos[k + 1] += G * ar; blocos[k + 2] += B * ar; blocos[k + 3] += aa * ar;
        }
      }
    }
  }
  tiny.width = nw; tiny.height = nh;
  const im = tcx.createImageData(nw, nh), d = im.data, area = LX * LY;
  for (let k = 0; k < nw * nh; k++) {
    const cover = blocos[k * 4 + 3] / area;
    if (cover < 0.42) continue;
    const inv = 1 / blocos[k * 4 + 3];
    d[k * 4] = blocos[k * 4] * inv; d[k * 4 + 1] = blocos[k * 4 + 1] * inv; d[k * 4 + 2] = blocos[k * 4 + 2] * inv; d[k * 4 + 3] = 255;
  }
  tcx.putImageData(im, 0, 0);
  ctx.save();
  ctx.imageSmoothingEnabled = false;
  if (alfa !== undefined && alfa < 1) ctx.globalAlpha = alfa;
  ctx.drawImage(tiny, bx0 * LX * F, by0 * LY * F, nw * LX * F, nh * LY * F);
  ctx.restore();
}
