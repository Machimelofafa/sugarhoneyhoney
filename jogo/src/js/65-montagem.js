// ===================================================================
// Montagem: a abertura corta do jogo para planos fechados (rostos, tênis, água, coração) e escreve
// os créditos por cima. Aqui os mesmos planos, tirados do vídeo, entram nos mesmos momentos do jogo,
// e os letreiros voltam no lugar e no tempo em que aparecem no vídeo.
// ===================================================================
const CL = CLOSES.planos, CLPOS = CLOSES.pos;
let closesImg = null, logoImg = null;
(() => {
  const a = new Image(); a.onload = () => { closesImg = a; }; a.src = CLOSES.img;
  const b = new Image(); b.onload = () => { logoImg = b; }; b.src = LOGO.img;
})();

// item da montagem: { tipo, a, b } com a..b = quadros do vídeo que ele cobre (toca na velocidade do vídeo)
const close = nome => ({ tipo: 'close', nome, a: CL[nome].a, b: CL[nome].b });
const montagem = { fila: [], item: null, t: 0, fim: null };
function tocar(itens, fim) {
  if (montagem.item) {                       // já tem montagem: entra no fim da fila
    montagem.fila.push(...itens);
    if (fim) { const f0 = montagem.fim; montagem.fim = () => { if (f0) f0(); fim(); }; }
    return;
  }
  montagem.fila = itens.slice(); montagem.fim = fim || null; proximoPlano();
}
function proximoPlano() {
  montagem.item = montagem.fila.shift() || null; montagem.t = 0;
  if (!montagem.item) { const f = montagem.fim; montagem.fim = null; if (f) f(); }
}
const emMontagem = () => !!montagem.item;
const duracaoPlano = it => Math.round((it.b - it.a + 1) * 60 / VFPS);
const quadroVideo = () => montagem.item.a + Math.floor(montagem.t * VFPS / 60);
function passoMontagem() {
  montagem.t++;
  // Enter (ou tocar na tela) pula o resto
  if (pressed.start && montagem.t > 8) {
    const fim = montagem.fim; montagem.fila = []; montagem.fim = null; montagem.item = null;
    // a música acompanha o pulo: começo da fase (depois da abertura) ou o logotipo (no fim)
    if (state === 'intro') musicaEm(352 / VFPS, true);
    else if (state === 'win') musicaEm(2191 / VFPS, false);
    if (fim) fim();
    return;
  }
  if (montagem.t >= duracaoPlano(montagem.item)) proximoPlano();
}

// plano fechado: uma imagenzinha com uma cor por bloco do mosaico, esticada na grade de blocos do plano
function desenhaClose(ctx) {
  const it = montagem.item, p = CL[it.nome], w = ctx.canvas.width, h = ctx.canvas.height;
  const v = clamp(quadroVideo(), p.a, p.b), [sx, sy] = CLPOS[p.q[v - p.a]];
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, w, h);
  if (!closesImg) return;
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(closesImg, sx, sy, p.nx, p.ny, p.F[0] * F, p.F[1] * F, p.nx * p.P[0] * F, p.ny * p.P[1] * F);
}
// logotipo 3D: um quadro a cada dois do vídeo; parado no fim e escurecendo
function desenhaLogo(ctx, v, alfa) {
  const L = LOGO, w = ctx.canvas.width, h = ctx.canvas.height;
  const k = clamp(Math.floor((v - L.a) / L.passo), 0, L.n - 1);
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, w, h);
  if (!logoImg) return;
  ctx.save(); ctx.imageSmoothingEnabled = true; ctx.globalAlpha = alfa;
  ctx.drawImage(logoImg, (k % L.cols) * L.w, Math.floor(k / L.cols) * L.h, L.w, L.h, 0, 0, w, h);
  ctx.restore();
}
// close do painel da esquerda (quadros 208-258): o mesmo cenário ampliado, os corações entrando um a um
const PAINEL = { x: 41, y: 0, w: 41, h: 57, entra: [230, 237, 245, 252] };
const coracoesPainel = () => PAINEL.entra.filter(q => quadroVideo() >= q).length;

// ---------- letreiros ----------
const PLAY_CRED = ['JAYME', 'EDUARDO', 'MARIA ESTELA', 'ANA ROSA', 'CRISTINA', 'BÁRBARA', 'OTHON', 'LÉA', 'DANTON', 'GUGA',
  'as crianças', 'apresentando', 'SERGIO', 'LOLITA'];
const credFila = PLAY_CRED.map(k => CREDITOS.findIndex(c => c.l.join(' / ').includes(k)));
const cred = { visto: new Set(), i: 0, t: 0, espera: 220 };
function reiniciaCreditos() { cred.visto.clear(); cred.i = 0; cred.t = 0; cred.espera = 220; }
// durante a fase, os letreiros que no vídeo passam sobre o jogo vão entrando em ordem, um de cada vez
function passoCreditos() {
  while (cred.i < credFila.length && cred.visto.has(credFila[cred.i]) && cred.t === 0) cred.i++;
  if (cred.i >= credFila.length) return;
  if (cred.espera > 0) { cred.espera--; return; }
  const c = CREDITOS[credFila[cred.i]];
  cred.t++;
  if (cred.t >= (c.b - c.a + 1) * 60 / VFPS) { cred.visto.add(credFila[cred.i]); cred.i++; cred.t = 0; cred.espera = 200; }
}
// cada linha é esticada na caixa medida no vídeo; branco com sombra preta, como na abertura
function desenhaLetreiro(c, alfa, v) {
  sc.save();
  sc.globalAlpha = alfa;
  for (let i = 0; i < c.l.length; i++) {
    if (c.a2 && i >= 2 && v !== undefined && v < c.a2) continue;
    const [x0, y0, x1, y1] = c.c[i], txt = c.l[i];
    const minusc = txt !== txt.toUpperCase();
    const px = (y1 - y0) * F / (minusc ? 0.8 : 0.71);
    sc.font = `700 ${px}px ${FONT}`;
    if ('letterSpacing' in sc) sc.letterSpacing = '0px';
    const larg = sc.measureText(txt).width || 1, esc = (x1 - x0) * F / larg;
    sc.save();
    sc.translate(x0 * F, y1 * F); sc.scale(esc, 1);
    const s = Math.max(1, 4 * F);
    sc.fillStyle = 'rgba(0,0,0,0.85)'; sc.fillText(txt, s / esc, s);
    sc.lineWidth = Math.max(1, 2.5 * F); sc.strokeStyle = 'rgba(0,0,0,0.75)'; sc.lineJoin = 'round'; sc.strokeText(txt, 0, 0);
    sc.fillStyle = '#ffffff'; sc.fillText(txt, 0, 0);
    sc.restore();
  }
  sc.restore();
}
function desenhaCreditos() {
  if (!creditosOn) return;
  const it = montagem.item;
  if (it && it.tipo !== 'geral' && it.tipo !== 'duo') {
    const v = quadroVideo();
    CREDITOS.forEach((c, i) => {
      if (v < c.a || v > c.b) return;
      cred.visto.add(i);
      desenhaLetreiro(c, clamp(Math.min(v - c.a + 1, c.b - v + 1) / 5, 0, 1), v);
    });
    return;
  }
  if (state === 'play' && !it && cred.i < credFila.length && cred.espera <= 0 && cred.t > 0) {
    const c = CREDITOS[credFila[cred.i]], dur = (c.b - c.a + 1) * 60 / VFPS;
    desenhaLetreiro(c, clamp(Math.min(cred.t, dur - cred.t) / 10, 0, 1));
  }
}
