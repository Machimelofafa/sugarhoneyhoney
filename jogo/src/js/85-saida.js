// ===================================================================
// Saída: escala inteira na vertical, célula 1,86:1, filtro de TV opcional
// ===================================================================
let scanPattern = null, vignette = null;
const filterOK = (() => { try { const t = document.createElement('canvas').getContext('2d'); t.filter = 'blur(1px)'; return t.filter === 'blur(1px)'; } catch (e) { return false; } })();
function layout() {
  const dpr = window.devicePixelRatio || 1;
  const bar = document.querySelector('.bar').offsetHeight;
  const touchH = document.body.classList.contains('touch') ? document.getElementById('touch').offsetHeight : 0;
  const availW = Math.max(120, document.documentElement.clientWidth - 32) * dpr;
  const availH = Math.max(120, window.innerHeight - bar - touchH - 48) * dpr;
  const k = Math.min(availH / H, availW / (W * ASPECT));
  // escala inteira quando cabe com folga; em tela pequena (celular) a inteira deixaria o jogo minúsculo
  K = k >= 3 ? Math.floor(k) : Math.max(0.5, Math.floor(k * 4) / 4);
  CW = K * ASPECT;
  screen.width = Math.round(W * CW); screen.height = Math.round(H * K);
  screen.style.width = (screen.width / dpr) + 'px';
  F = screen.height / 1058;                       // px da tela por px do quadro geral do vídeo
  comp.width = screen.width; comp.height = screen.height;
  tmpH.width = screen.width; tmpH.height = screen.height;
  const p = document.createElement('canvas'); p.width = 1; p.height = Math.max(2, Math.round(K));
  const pc = p.getContext('2d');
  const dark = Math.max(1, Math.round(p.height * 0.38));
  pc.fillStyle = 'rgba(0,0,0,0.42)'; pc.fillRect(0, p.height - dark, 1, dark);
  scanPattern = sc.createPattern(p, 'repeat');
  const w = screen.width, h = screen.height;
  vignette = sc.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.35, w / 2, h / 2, Math.max(w, h) * 0.75);
  vignette.addColorStop(0, 'rgba(0,0,0,0)'); vignette.addColorStop(1, 'rgba(0,0,0,0.5)');
}
// 1) cenário na grade → comp (vizinho mais próximo)  2) atores com mosaico por cima  3) filtro de TV opcional
// Na montagem, o plano fechado (ou o logotipo, ou os olhos) toma a tela inteira.
const comp = document.createElement('canvas'), cc = comp.getContext('2d');
const tmpH = document.createElement('canvas'), th = tmpH.getContext('2d');
function present() {
  const w = screen.width, h = screen.height, it = montagem.item;
  cc.imageSmoothingEnabled = false;
  if (it && it.tipo === 'close') desenhaClose(cc);
  else if (it && it.tipo === 'logo') { const v = quadroVideo(); desenhaLogo(cc, v, clamp((LOGO.a + 116 - v) / 30, 0, 1)); }
  else if (it && it.tipo === 'olhos') { cc.fillStyle = '#000'; cc.fillRect(0, 0, w, h); drawOlhos(cc, montagem.t); }
  else if (it && it.tipo === 'paineis') cc.drawImage(buf, PAINEL.x, PAINEL.y, PAINEL.w, PAINEL.h, 0, 0, w, h);
  else if (state === 'win' && winData.fimT >= 0) desenhaLogo(cc, LOGO.a + 116, 0.3);
  else {
    cc.drawImage(buf, 0, 0, w, h);
    drawActors(cc);
    if (state === 'title') drawOlhos(cc, stateT);
  }
  sc.save();
  sc.imageSmoothingEnabled = false;
  if (!crt) sc.drawImage(comp, 0, 0);
  else {
    sc.drawImage(comp, 0, 0);
    if (filterOK) {
      th.clearRect(0, 0, w, h); th.drawImage(comp, 0, 0);
      sc.globalCompositeOperation = 'lighter'; sc.globalAlpha = 0.2;
      sc.filter = `blur(${Math.max(1, K * 1.4)}px)`;
      sc.drawImage(tmpH, 0, 0);
      sc.filter = 'none'; sc.globalAlpha = 1; sc.globalCompositeOperation = 'source-over';
    }
    if (K >= 2) { sc.fillStyle = scanPattern; sc.fillRect(0, 0, w, h); }
    sc.fillStyle = vignette; sc.fillRect(0, 0, w, h);
  }
  sc.restore();
}
function text(str, gx, gy, size, o = {}) {
  sc.save();
  const px = Math.max(9, Math.round(size * K));
  sc.font = `${o.weight || 700} ${px}px ${FONT}`;
  sc.textAlign = o.align || 'center';
  sc.textBaseline = 'alphabetic';
  if ('letterSpacing' in sc) sc.letterSpacing = (o.ls || 0) * px + 'px';
  const x = gx * CW, y = gy * K;
  sc.globalAlpha = o.alpha === undefined ? 1 : o.alpha;
  sc.fillStyle = 'rgba(0,0,0,0.9)';
  sc.fillText(str, x + px * 0.07, y + px * 0.09);
  sc.fillStyle = o.color || '#f6f2ff';
  sc.fillText(str, x, y);
  sc.restore();
}
const fmtTime = f => { const s = Math.floor(f / 60); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`; };
const toque = () => document.body.classList.contains('touch');
function drawCaption() {
  if (!caption || emMontagem()) return;
  const t = caption.t, d = caption.dur;
  const a = Math.min(1, t / 15, (d - t) / 20);
  text(caption.small, 85, 112, 6, { weight: 500, alpha: a });
  text(caption.big, 85, 128, 13, { alpha: a, ls: 0.04 });
}
function overlayText() {
  desenhaCreditos();
  if (state === 'title') {
    text('o jogo da abertura', 85, 26, 7, { weight: 500, color: '#c9c0ee' });
    text('DESPEDIDA DE SOLTEIRO', 85, 50, 15, { ls: 0.03 });
    if (Math.floor(frame / 30) % 2 === 0) text(toque() ? 'toque para jogar' : 'aperte ENTER para jogar', 85, 200, 7, { weight: 500 });
    text('recriação de fã da novela de 1992', 85, 226, 5, { weight: 500, color: '#8b82b4' });
  } else if (state === 'play' || state === 'intro') {
    drawCaption();
    if (paused) text('PAUSA', 85, caption ? 160 : 124, 16, { ls: 0.1 });
    if (emMontagem() && montagem.t > 8 && montagem.t < 150 && state === 'intro') text(toque() ? 'toque para pular' : 'ENTER pula', 166, 233, 4.5, { weight: 500, align: 'right', color: '#b9b1dd', alpha: 0.7 });
  } else if (state === 'over' && stateT > 110) {
    text('FIM DE JOGO', 85, 200, 14, { ls: 0.05 });
    if (stateT > 200) text(toque() ? 'toque para tentar de novo' : 'aperte ENTER para tentar de novo', 85, 216, 6, { weight: 500 });
  } else if (state === 'win' && winData.fimT >= 0) {
    const a = clamp(winData.fimT / 30, 0, 1);
    text('FIM', 85, 120, 18, { ls: 0.12, alpha: a });
    text(`tempo ${fmtTime(winData.time)}`, 85, 138, 7, { weight: 500, color: '#e4dfa2', alpha: a });
    if (winData.fimT > 40) text(toque() ? 'toque para jogar de novo' : 'aperte ENTER para jogar de novo', 85, 218, 6, { weight: 500 });
  }
}
function render() {
  const it = montagem.item;
  if (it && it.tipo === 'paineis') { drawLevel(); drawHearts(0, coracoesPainel()); }
  else if (it && (it.tipo === 'close' || it.tipo === 'logo' || it.tipo === 'olhos')) { /* o plano toma a tela */ }
  else if (state === 'title') drawTitle();
  else if (state === 'over') drawOver();
  else if (state === 'win') drawWin();
  else { drawLevel(); drawHud(); if (paused) dim(0.5); }
  present();
  overlayText();
}
