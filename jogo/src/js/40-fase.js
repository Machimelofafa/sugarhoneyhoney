// ===================================================================
// Fase: pisos na grade (coluna, linha); y = linha dos pés.
// Percurso tirado da abertura: píer → fosso de fogo → escada da esquerda → esteira que sobe →
// piso do vilão → jacaré → chão cinza → escada rolante → teto da moça. O rio é só fundo.
// ===================================================================
const P = (id, x0, x1, y, extra) => Object.assign({ id, x0, x1, y }, extra || {});
// rampa: (x0, y0) e (x1, y1) são as pontas da superfície
const S = (id, x0, y0, x1, y1, extra) => Object.assign({ id, x0, y0, x1, y1 }, extra || {});
const PLATS = [
  P('pier', 126, 168, 217),
  P('fosso', 58, 126, 226),                 // chão do fogo, na frente da parede de pedra
  S('escadaE', 22, 161, 58, 219),           // degraus cinza da esquerda (o pé de baixo fica 7 linhas acima do fosso)
  P('patamar', 2, 22, 161),
  P('vfloor', 2, 97, 137),
  P('crocLedge', 97, 131, 139),
  P('ledgeR', 131, 167, 130),
  S('rolante', 127, 58, 165, 122.3),        // escada rolante escura: o pé fica no fim do chão cinza, 8 linhas acima dele
  P('roof', 10, 127, 58),
];
// esteira vertical da esquerda: leva do patamar até o piso do vilão
const LIFT = { x0: 9, x1: 18, top: 137, bottom: 161, speed: 0.9 };
// rio embaixo do chão cinza: cair nele é afundar
const RIO = { x0: 131, x1: 168, y0: 142, y1: 172 };

// cena do abraço (tirada do vídeo): distância inicial entre os dois, quadros do atlas, passos de jogo por quadro
const DUO_DX = 29, DUO_FRAMES = 70, DUO_STEP = 4;
// corpo dos atores na grade (o herói tem ~64 linhas de altura no quadro geral)
const HERO_H = 62, HERO_HALF = 4.5;
const VIL_H = 58, VIL_HALF = 5;

function surfY(p, x) { return p.y !== undefined ? p.y : p.y0 + (x - p.x0) * (p.y1 - p.y0) / (p.x1 - p.x0); }
const onPlat = (p, x) => x >= p.x0 && x <= p.x1;

const GRAV = 0.15, JUMP = 3.4, WALK = 0.5, MAXFALL = 4, STEPUP = 10, STEPDOWN = 3;
function findLanding(x, y0, y1) {
  let best = null, by = Infinity;
  for (const p of PLATS) {
    if (!onPlat(p, x)) continue;
    const s = surfY(p, x);
    if (y0 <= s + 0.01 && y1 >= s && s < by) { best = p; by = s; }
  }
  return best;
}
function findStep(x, y, cur) {
  let best = null, bd = Infinity;
  for (const p of PLATS) {
    if (p === cur || !onPlat(p, x)) continue;
    const s = surfY(p, x);
    if (s >= y - STEPUP && s <= y + STEPDOWN && Math.abs(s - y) < bd) { best = p; bd = Math.abs(s - y); }
  }
  return best;
}
const overlap = (a, b) => a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;

// ---------- fogo do fosso ----------
// A animação do vídeo (12 passos) quase sempre cobre o fosso inteiro, o que não deixa passar.
// Aqui o fosso vira três chamas que sobem e descem em onda da direita para a esquerda; cada chama
// mostra as colunas dela tiradas dos passos do vídeo em que está apagada, baixa ou alta.
const FOGO = {
  y: 226, ciclo: 300,
  slots: [
    { x0: 44, x1: 66, atraso: 100, apagado: [5, 6], baixo: [7, 8], alto: [0, 1, 2, 3, 9, 11] },
    { x0: 67, x1: 86, atraso: 50, apagado: [3, 4], baixo: [5, 0], alto: [1, 6, 7, 8, 9, 10] },
    { x0: 87, x1: 127, atraso: 0, apagado: [1], baixo: [0, 2], alto: [3, 4, 5, 6, 7, 8, 9, 10, 11] },
  ],
};
// fase de cada chama no ciclo: apagada 0-139, subindo 140-159, acesa 160-279, descendo 280-299
function quadroDoFogo(slot, t) {
  const p = ((t - slot.atraso) % FOGO.ciclo + FOGO.ciclo) % FOGO.ciclo;
  const passo = Math.floor(t / STEP_FRAMES);
  const l = p < 140 ? slot.apagado : (p < 160 || p >= 280) ? slot.baixo : slot.alto;
  return l[passo % l.length];
}
// topo da chama por coluna em cada passo do vídeo (0 = sem chama), medido nas cores da chama
let TOPO_CHAMA = null;
function medirChamas() {
  const L = A.layers.fire;
  const ehChama = PALRGB.map(([r, g, b]) => r > 100 && g > 40 && r - b > 40 && Math.abs(r - g) > 15);
  TOPO_CHAMA = L.frames.map(f => {
    const idx = unb64(f), topo = new Int16Array(L.w);
    for (let c = 0; c < L.w; c++) {
      let n = 0, t = 0;
      for (let r = 172 - L.y; r < L.h; r++) if (ehChama[idx[r * L.w + c]]) { if (!n) t = L.y + r; n++; }
      if (n >= 2) topo[c] = t;
    }
    return topo;
  });
}
// passo do vídeo que cada coluna do fosso mostra no instante t (-1 = fora das chamas). Entre duas chamas vizinhas
// o corte muda de lugar (até 5 colunas) para cair onde as duas estão mais baixas: sem chama cortada a prumo.
let colunasFogo = null, colunasT = -1;
function quadrosPorColuna(t) {
  if (colunasT === t) return colunasFogo;
  const L = A.layers.fire, ks = FOGO.slots.map(s => quadroDoFogo(s, t));
  const col = new Int8Array(L.w).fill(-1);
  FOGO.slots.forEach((s, i) => { for (let x = s.x0; x <= s.x1; x++) col[x - L.x] = ks[i]; });
  const alt = (k, x) => { const tp = TOPO_CHAMA[k][x - L.x]; return tp ? FOGO.y - tp : 0; };
  for (let i = 0; i + 1 < FOGO.slots.length; i++) {
    const b = FOGO.slots[i].x1, kl = ks[i], kr = ks[i + 1];
    let corte = b, menor = Infinity;
    for (let x = b - 5; x <= b + 5; x++) {
      const perda = alt(kl, x + 1) + alt(kr, x);      // chama da esquerda que ficaria à direita do corte e vice-versa
      if (perda < menor) { menor = perda; corte = x; }
    }
    for (let x = b - 5; x <= b + 6; x++) col[x - L.x] = x <= corte ? kl : kr;
  }
  colunasT = t; colunasFogo = col;
  return col;
}
// a chama pega o herói se passar mais de 5 linhas acima dos pés dele, em qualquer coluna do tronco
function fogoPega(x, y, t) {
  if (y < FOGO.y - 60) return false;
  const L = A.layers.fire, col = quadrosPorColuna(t);
  for (let cx = Math.ceil(x - 2.5); cx <= Math.floor(x + 2.5); cx++) {
    const k = col[cx - L.x];
    if (k === undefined || k < 0) continue;
    const topo = TOPO_CHAMA[k][cx - L.x];
    if (topo && y - topo > 5) return true;
  }
  return false;
}

// ---------- jacaré ----------
// quadros do jacaré na camada 'croc' (tirados da abertura): 0 deitado, 1 levantando, 2-3 em pé, 4 abaixando.
// Deitado ele é chão (o herói pisa nas costas dele, como no vídeo); nos outros a parte verde morde.
let TOPO_JACARE = null;
function medirJacare() {
  const L = A.layers.croc;
  const verde = PALRGB.map(([r, g, b]) => g > 60 && g > r + 20 && g > b + 20);
  TOPO_JACARE = L.frames.map(f => {
    const idx = unb64(f), topo = new Int16Array(L.w);
    for (let c = 0; c < L.w; c++) for (let r = 0; r < L.h; r++) if (verde[idx[r * L.w + c]]) { topo[c] = L.y + r; break; }
    return topo;
  });
}
function jacarePega(x, y) {
  const k = crocFrame(); if (k === 0) return false;
  const L = A.layers.croc;
  for (let cx = Math.ceil(x - 3); cx <= Math.floor(x + 3); cx++) {
    const c = cx - L.x; if (c < 0 || c >= L.w) continue;
    const topo = TOPO_JACARE[k][c];
    if (topo && topo < 137 && y > topo + 2 && y - HERO_H < 139) return true;
  }
  return false;
}
medirChamas(); medirJacare();

// ---------- tamanho dos atores: no alto da fase o herói aparece menor no vídeo (~205-230 px contra ~283 embaixo) ----------
const escHeroi = y => y >= 137 ? 1 : clamp(0.8 + (y - 58) * 0.2 / 79, 0.8, 1);
const alturaHeroi = () => HERO_H * escHeroi(hero.y) * (hero.crouch ? 0.56 : 1);

// ---------- grade entre os postes do alto (plano 1495-1716) ----------
// Desce até o teto e fecha a passagem; sobe só até a altura do herói agachado, como quando ele passa por baixo
// dela na abertura. Embaixo, se ela descer em cima dele, machuca e o empurra de volta.
const GRADE = { x0: 88, x1: 100, baixo: 57, alto: -37, baixa: 170, sobe: 46, alta: 118, desce: 24, atraso: 40 };
function gradeDy() {
  const G = GRADE, c = G.baixa + G.sobe + G.alta + G.desce, p = ((playFrames + G.atraso) % c + c) % c;
  if (p < G.baixa) return 0;
  if (p < G.baixa + G.sobe) return G.alto * (p - G.baixa) / G.sobe;
  if (p < G.baixa + G.sobe + G.alta) return G.alto;
  return G.alto * (1 - (p - G.baixa - G.sobe - G.alta) / G.desce);
}
const gradePe = () => GRADE.baixo + gradeDy();        // linha de baixo da grade agora

// ---------- alçapão no teto, à direita da grade (abre e fecha sozinho, como no plano da grade) ----------
const ALC = { x0: 106, x1: 119, fechado: 190, abrindo: 8, aberto: 80, fechando: 8, atraso: 0 };
function alcapaoFase() {
  const a = ALC, c = a.fechado + a.abrindo + a.aberto + a.fechando, p = ((playFrames + a.atraso) % c + c) % c;
  if (p < a.fechado) return 'fechado';
  if (p < a.fechado + a.abrindo) return 'abrindo';
  if (p < a.fechado + a.abrindo + a.aberto) return 'aberto';
  return 'fechando';
}
const alcapaoQuadro = () => { const f = alcapaoFase(); return f === 'fechado' ? 0 : f === 'aberto' ? 2 : 1; };

// ---------- o vão: o raio quebra o teto entre a moça (x 30) e o herói ----------
const MOCA_BEIRA = 30;
const VAO = { x0: MOCA_BEIRA + 5, x1: MOCA_BEIRA + 21 };
const vao = { abre: 0, aberto: false };
