// ===================================================================
// Estado do jogo e herói
// ===================================================================
let state = 'title', stateT = 0, frame = 0, playFrames = 0;
let paused = false, crt = true, creditosOn = false;
let hero, villain, croc, girl, checkpoint, shards = [], respawnT = 0, caption = null;
let introHearts = 0, winData = null, overData = null;
let feitos = {};          // momentos da abertura que já passaram (cada plano fechado entra uma vez)
let estouros = [];        // estouro vermelho com a estrela amarela nos golpes da luta
let raio = null;          // o raio que quebra o teto e abre o vão
let pendentes = [];       // ações marcadas para daqui a alguns quadros (o corte para a moça depois do nocaute)

const INICIO = { x: 150, y: 217 };
function newGame() {
  hero = { x: INICIO.x, y: INICIO.y, vx: 0, vy: 0, dir: -1, ground: null, state: 'normal', hp: 4, inv: 0, hurtT: 0, punchT: 0, kickT: 0, burnT: 0, walk: 0, hidden: false, lifting: false, landT: 0, crouch: false };
  hero.ground = PLATS.find(p => p.id === 'pier');
  villain = { x: 70, y: 137, dir: -1, hp: 4, state: 'guard', t: 0, cool: 40, walk: 0, hitLock: 0 };
  croc = { phase: 'down', t: 0 };
  girl = { x: 30, y: 60, dir: 1, estado: 'espera', t: 0, pausa: 60, alvo: 44, walk: 0 };
  checkpoint = { x: INICIO.x, y: INICIO.y };
  shards = []; respawnT = 0; playFrames = 0; winData = null; overData = null; introHearts = 0;
  feitos = {}; estouros = []; raio = null; pendentes = []; vao.abre = 0; vao.aberto = false;
}

const keys = { left: false, right: false, up: false, down: false, jump: false, punch: false, kick: false };
const pressed = { jump: false, punch: false, kick: false, start: false, up: false };
function setState(s) { state = s; stateT = 0; }
const depois = (n, f) => pendentes.push({ t: n, f });
function startGame() {
  audioOn(); if (!temMusica()) SFX.start();
  newGame();
  setState('intro');
  musicaEm(0, true);
  // a abertura do vídeo até o começo do jogo: olhos com o elenco, o quadro geral, o painel enchendo de corações
  // e a moça com as mãos na boca (quadros 1-352)
  tocar([{ tipo: 'olhos', a: 1, b: 106 }, { tipo: 'geral', a: 107, b: 207 }, { tipo: 'paineis', a: 208, b: 258 }, close('maos')],
    () => { setState('play'); caption = { small: 'fase única', big: 'SUBA ATÉ ELA', t: 0, dur: 170 }; });
}

const heroBox = () => ({ x0: hero.x - HERO_HALF, x1: hero.x + HERO_HALF, y0: hero.y - alturaHeroi(), y1: hero.y });

// devolve true se o golpe pegou
function hurtHero(fromX, kind) {
  if (hero.hidden || hero.state === 'burn' || hero.state === 'sink' || hero.state === 'trap' || hero.state === 'abismo') return false;
  if (kind !== 'fire' && kind !== 'water' && hero.inv > 0) return false;
  if (window.__jogo) console.log('hurt', kind, frame, hero.x.toFixed(1), hero.y.toFixed(1));
  hero.hp--; hero.crouch = false;
  shatterSlot(0, hero.hp);
  SFX.hurt();
  if (kind === 'fire' || kind === 'water') {
    // queimou ou caiu no rio: fica um instante (afundando, no rio) e volta ao último ponto seguro
    hero.state = kind === 'fire' ? 'burn' : 'sink'; hero.burnT = kind === 'fire' ? 34 : 60; hero.vx = 0; hero.vy = 0; hero.lifting = false;
    if (kind === 'water') SFX.splash();
    return true;
  }
  if (hero.hp <= 0) { startGameOver(); return true; }
  hero.inv = 100; hero.state = 'hurt'; hero.hurtT = 26; hero.lifting = false;
  const away = hero.x < fromX ? -1 : 1;
  hero.vx = away * (kind === 'croc' ? 0.6 : 0.9); hero.vy = -1.6; hero.ground = null;
  return true;
}
function respawn() {
  hero.hidden = false; hero.x = checkpoint.x; hero.y = checkpoint.y; hero.vx = 0; hero.vy = 0; hero.lifting = false; hero.crouch = false;
  hero.ground = findStep(hero.x, hero.y, null) || findLanding(hero.x, hero.y - 1, hero.y + 1);
  hero.state = 'normal'; hero.inv = 120; hero.walk = 0;
}
// caiu pelo alçapão (na água, embaixo) ou no vão: perde um coração e volta ao ponto seguro do alto
function caiuFora(kind) {
  const h = hero;
  h.hidden = true; h.state = 'normal'; h.vy = 0; h.hp--;
  const volta = () => { shatterSlot(0, h.hp); if (h.hp <= 0) startGameOver(); else respawnT = 1; };
  if (kind === 'trap') {
    SFX.splash();
    // como na abertura: o herói afunda, a moça cruza os braços enquanto um coração racha, ele passa a mão no rosto
    const itens = feitos.agua ? [close('agua')] : [close('agua'), close('aflicao'), close('rosto')];
    feitos.agua = true;
    respawnT = 1e9; tocar(itens, volta);
  } else { SFX.hurt(); respawnT = 50; shatterSlot(0, h.hp); if (h.hp <= 0) { respawnT = 1e9; depois(40, startGameOver); } }
}

function updateHero() {
  const h = hero;
  if (h.hidden) { if (--respawnT <= 0) respawn(); return; }
  if (h.state === 'burn' || h.state === 'sink') {
    // queimando fica parado; afundando no rio desce devagar, como na abertura
    if (h.state === 'sink') { h.y += 0.35; h.walk += 0.35; }
    if (--h.burnT <= 0) {
      if (h.hp <= 0) { startGameOver(); return; }
      h.hidden = true; respawnT = 30;
    }
    return;
  }
  if (h.state === 'trap' || h.state === 'abismo') {          // caindo pelo alçapão aberto ou dentro do vão
    h.vy = Math.min(h.vy + GRAV, MAXFALL); h.y += h.vy;
    if (h.y > (h.state === 'trap' ? 104 : 112)) caiuFora(h.state);
    return;
  }
  if (h.state === 'espanto') { h.vx = 0; return; }             // o raio caiu na frente dele
  if (h.inv > 0) h.inv--;
  if (h.landT > 0) h.landT--;
  let dx = (keys.left ? -1 : 0) + (keys.right ? 1 : 0);
  if (h.lifting) dx = 0;              // na esteira vertical ele vai agarrado até o alto
  if (h.state === 'hurt') { dx = 0; if (--h.hurtT <= 0 && h.ground) h.state = 'normal'; if (h.hurtT < -60) h.state = 'normal'; }
  if (h.state === 'punch') {
    dx = 0; h.punchT++;
    if (h.punchT >= 6 && h.punchT <= 10) punchHit();
    if (h.punchT >= 18) h.state = 'normal';
  }
  if (h.state === 'kick') {           // chute alto e joelhada do contra-ataque: mais lento, mais longe, não dá para defender
    dx = 0; h.kickT++;
    if (h.kickT >= 9 && h.kickT <= 15) kickHit();
    if (h.kickT >= 30) h.state = 'normal';
  }

  if (h.state === 'normal') {
    // agachar: segura ↓ no chão; embaixo da grade baixa não dá para levantar
    const preso = h.crouch && h.y <= 62 && h.x + HERO_HALF > GRADE.x0 && h.x - HERO_HALF < GRADE.x1 && gradePe() > h.y - HERO_H * escHeroi(h.y) - 1;
    h.crouch = !!h.ground && !h.lifting && (keys.down || preso);
    if (dx) h.dir = dx;
    const wantsJump = (pressed.jump || pressed.up) && !h.crouch;
    if (pressed.punch && h.ground && podeResgatar()) { startWin(); return; }
    if (pressed.punch && h.ground && !h.crouch) { h.state = 'punch'; h.punchT = 0; SFX.punch(); }
    else if (pressed.kick && h.ground && !h.crouch) { h.state = 'kick'; h.kickT = 0; SFX.punch(); }
    else if (wantsJump && (h.ground || h.lifting)) { h.vy = -JUMP; h.vx = dx * WALK; h.ground = null; h.lifting = false; SFX.jump(); }
  } else h.crouch = false;
  const target = h.state === 'normal' ? dx * (h.crouch ? WALK * 0.5 : WALK) : 0;
  if (h.ground) h.vx = h.state === 'hurt' ? h.vx * 0.85 : target;
  else h.vx += (target - h.vx) * (h.state === 'hurt' ? 0.02 : 0.14);

  const px = h.x, py = h.y;
  h.x = clamp(h.x + h.vx, 4, W - 4);
  h.walk += Math.abs(h.x - px);

  // esteira vertical: só puxa para cima quem está dentro dela, abaixo do piso do vilão
  const inLift = h.x >= LIFT.x0 && h.x <= LIFT.x1 && h.y > LIFT.top + 0.5 && h.y <= LIFT.bottom + 0.5 && h.vy >= -0.5;
  h.lifting = false;
  if (inLift && h.state !== 'hurt') {
    h.ground = null; h.vy = 0; h.vx = 0; h.y = Math.max(LIFT.top, h.y - LIFT.speed); h.lifting = true; h.crouch = false;
    h.x += ((LIFT.x0 + LIFT.x1) / 2 - h.x) * 0.2;
    if (h.y <= LIFT.top) { h.lifting = false; h.ground = findLanding(h.x, h.y - 1, h.y + 1); }
  } else if (h.ground) {
    if (!onPlat(h.ground, h.x)) {
      const q = findStep(h.x, h.y, h.ground);
      if (q) { h.ground = q; h.y = surfY(q, h.x); } else { h.ground = null; h.vy = 0; }
    } else {
      h.y = surfY(h.ground, h.x);
      // pé de rampa que nasce no meio deste chão (a escada rolante): entra nela andando no sentido em que ela sobe
      const sd = Math.sign(h.x - px);
      if (sd && h.ground.y !== undefined) for (const q of PLATS) {
        if (q.y !== undefined || !onPlat(q, h.x)) continue;
        const sq = surfY(q, h.x);
        if (h.y - sq > 0 && h.y - sq <= STEPUP && surfY(q, h.x + sd * 0.5) < sq) { h.ground = q; h.y = sq; break; }
      }
    }
  }
  if (!h.ground && !h.lifting) {
    h.vy = Math.min(h.vy + GRAV, MAXFALL);
    h.y += h.vy;
    // no ar, ao passar pela beira de um chão um pouco acima dos pés, sobe nele (não cai no vão ao lado do degrau)
    for (const q of PLATS) {
      if (h.vy < -1 || q.y === undefined || !onPlat(q, h.x) || onPlat(q, px)) continue;
      if (h.y - q.y >= 0 && h.y - q.y <= STEPUP) { h.ground = q; h.y = q.y; h.vy = 0; if (h.state === 'hurt' && h.hurtT <= 0) h.state = 'normal'; break; }
    }
  }
  if (!h.ground && !h.lifting) {
    if (h.vy >= 0) {
      const q = findLanding(h.x, py, h.y);
      if (q) {
        if (h.vy > 2.2) h.landT = 8;
        h.ground = q; h.y = surfY(q, h.x); h.vy = 0;
        if (h.state === 'hurt' && h.hurtT <= 0) h.state = 'normal';
      }
    }
  }
  afterMove(px);
}

const vilaoDeCabeca = () => villain.state !== 'down' && villain.state !== 'rise' && villain.state !== 'tonto';
const podeResgatar = () => vao.aberto && hero.ground && hero.ground.id === 'roof' && hero.x >= girl.x + 24 && hero.x <= girl.x + 42;

function afterMove(px) {
  const h = hero;
  // o corpo do vilão fecha a passagem: não dá para atravessar nem pulando (depois do nocaute ele já não segura ninguém)
  if (vilaoDeCabeca() && h.y > villain.y - VIL_H + 12 && h.y < villain.y + 6) {
    const d = h.x - villain.x, lado = Math.abs(px - villain.x) > 0.01 ? Math.sign(px - villain.x) : (d >= 0 ? 1 : -1);
    if (Math.abs(d) < 8 || Math.sign(d) !== lado) h.x = villain.x + lado * 8;
  }
  // fogo do fosso: a chama do quadro atual queima
  if (h.y > FOGO.y - 62 && h.x > 40 && h.x < 128 && fogoPega(h.x, h.y, playFrames)) { hurtHero(h.x, 'fire'); return; }
  if (h.y > H + 40) { hurtHero(h.x, 'fire'); return; }
  // rio: quem cai do chão cinza na água afunda (a queda do píer não chega tão alto)
  if (!h.ground && !h.lifting && h.x > RIO.x0 && h.x < RIO.x1 && h.y > RIO.y0 && h.y < RIO.y1) { hurtHero(h.x, 'water'); return; }
  // jacaré
  if (h.inv <= 0 && h.state !== 'hurt' && h.y > 100 && h.y < 145 && h.x > 94 && h.x < 135 && jacarePega(h.x, h.y)) { SFX.snap(); hurtHero(112, 'croc'); }
  const gid = h.ground && h.ground.id;
  // ---- no alto ----
  if (h.y > 40 && h.y <= 62) {
    // grade: fecha a passagem para quem não cabe embaixo dela; se desce em cima dele, machuca e empurra de volta
    const pe = gradePe(), topo = h.y - alturaHeroi();
    if (h.x + HERO_HALF > GRADE.x0 && h.x - HERO_HALF < GRADE.x1 && topo < pe + 1) {
      const vinha = px - HERO_HALF >= GRADE.x1 - 0.6 ? 1 : px + HERO_HALF <= GRADE.x0 + 0.6 ? -1 : 0;
      if (vinha) {
        h.x = vinha > 0 ? GRADE.x1 + HERO_HALF : GRADE.x0 - HERO_HALF;
        // na abertura ele para diante da grade e a montagem corta para a moça e um coração
        if (vinha > 0 && !feitos.grade && h.state === 'normal') { feitos.grade = true; tocar([close('surpresa')]); }
      } else if (hurtHero(GRADE.x0, 'grade')) { h.x = GRADE.x1 + HERO_HALF + 1; h.vx = 1; }
    }
    // passou por baixo: close do herói e ponto seguro do lado de lá
    if (!feitos.passou && gid === 'roof' && h.x < GRADE.x0 - HERO_HALF - 1) { feitos.passou = true; checkpoint = { x: 82, y: 58 }; tocar([close('rosto2')]); }
    // alçapão: se abre embaixo dele, cai
    if (gid === 'roof' && h.state === 'normal' && h.x >= ALC.x0 && h.x <= ALC.x1 && alcapaoFase() === 'aberto') {
      h.state = 'trap'; h.ground = null; h.vy = 0.4; h.crouch = false; SFX.hurt(); return;
    }
    // o raio cai quando ele se aproxima da moça, e o vão fica entre os dois
    if (feitos.passou && !raio && !vao.aberto && gid === 'roof' && h.x < 78) iniciaRaio();
    if (vao.abre > 0.4 && gid === 'roof' && h.x > VAO.x0 + 1 && h.x < VAO.x1 - 1 && h.state === 'normal') {
      h.state = 'abismo'; h.ground = null; h.vy = 0.3; h.crouch = false; return;
    }
  }
  // pontos de retorno e momentos da abertura
  if ((gid === 'escadaE' && h.x < 40 || gid === 'patamar') && checkpoint.y > 161) checkpoint = { x: 21, y: 161 };
  if (gid === 'vfloor' && !vilaoDeCabeca() && checkpoint.y > 137) checkpoint = { x: 92, y: 137 };
  if (gid === 'ledgeR' && checkpoint.y > 130) checkpoint = { x: 150, y: 130 };
  if (gid === 'ledgeR' && !feitos.jacare) { feitos.jacare = true; tocar([close('tenis'), close('sorriso')]); }   // os tênis e a moça sorrindo
  if (gid === 'roof' || gid === 'rolante' && h.y < 70) {
    if (checkpoint.y > 58) checkpoint = { x: 124, y: 58 };
    if (gid === 'roof' && !feitos.alto) { feitos.alto = true; tocar([close('olha')]); }                       // ela olha para o alto
  }
}

function iniciaRaio() {
  raio = { t: 0 }; hero.state = 'espanto'; hero.vx = 0; hero.crouch = false;
  girl.estado = 'beira'; girl.x = MOCA_BEIRA; girl.dir = 1;
  SFX.raio();
}
function updateRaio() {
  if (!raio) return;
  raio.t++;
  if (raio.t > 8) vao.abre = Math.min(1, vao.abre + 0.06);
  if (raio.t === 36) {
    // a moça na beira, o raio, ela perde o equilíbrio; depois o close dela com a cabeça para trás
    tocar([close('beira'), close('cabeca')], () => { raio = null; vao.aberto = true; vao.abre = 1; hero.state = 'normal'; caption = { small: 'estenda a mão', big: 'X', t: 0, dur: 150 }; });
  }
}

const atingeVilao = (alcance, y0, y1) => {
  const pb = { x0: Math.min(hero.x + hero.dir * 3, hero.x + hero.dir * alcance), x1: Math.max(hero.x + hero.dir * 3, hero.x + hero.dir * alcance), y0: hero.y - y0, y1: hero.y - y1 };
  const vb = { x0: villain.x - VIL_HALF, x1: villain.x + VIL_HALF, y0: villain.y - VIL_H, y1: villain.y };
  return overlap(pb, vb);
};
function punchHit() {
  if (!vilaoDeCabeca() || villain.hitLock > 0 || !atingeVilao(16, 52, 28)) return;
  if ((villain.state === 'guard' || villain.state === 'walk') && Math.random() < 0.3) {   // o vilão se defende de vez em quando
    villain.hitLock = 12; SFX.punch(); villain.x = clamp(villain.x + hero.dir * 1.5, VIL_MIN, VIL_MAX);
    if (Math.random() < 0.5) { villain.state = 'windup'; villain.t = 6; villain.dir = hero.x < villain.x ? -1 : 1; }   // e às vezes revida
    return;
  }
  acertaVilao(3);
}
function kickHit() {
  if (!vilaoDeCabeca() || villain.hitLock > 0 || !atingeVilao(22, 58, 30)) return;
  acertaVilao(5);
}
function acertaVilao(empurra) {
  villain.hp--; villain.hitLock = 14;
  shatterSlot(1, villain.hp);
  SFX.hit();
  estouros.push({ x: villain.x - hero.dir * 2, y: villain.y - 44, t: 0 });
  if (villain.hp <= 0) {
    villain.state = 'down'; villain.t = 0; SFX.ko(); caption = { small: 'nocaute', big: 'K.O.', t: 0, dur: 110 };
    depois(40, () => tocar([close('olhos')]));          // os olhos e a boca da moça
  } else { villain.state = 'hurt'; villain.t = 0; villain.x = clamp(villain.x + hero.dir * empurra, VIL_MIN, VIL_MAX); villain.cool = Math.max(villain.cool, 30); }
}

function shatterSlot(side, k) {
  if (k < 0 || k > 3) return;
  const c = slotCenter(side, k);
  for (let i = 0; i < 14; i++) shards.push({ x: c.x - 4 + Math.random() * 8, y: c.y - 5 + Math.random() * 10, vx: (Math.random() - 0.5) * 0.7, vy: -Math.random() * 1.6, life: 40 + Math.random() * 20, c: Math.random() < 0.4 ? HEART_DARK : HEART_RED });
}
function updateShards() {
  for (const p of shards) { p.vy += 0.09; p.x += p.vx; p.y += p.vy; p.life--; }
  shards = shards.filter(p => p.life > 0 && p.y < H);
  for (const e of estouros) e.t++;
  estouros = estouros.filter(e => e.t < 16);
}
function startWin() {
  setState('win'); winData = { time: playFrames, fimT: -1 }; hero.state = 'normal'; hero.vx = 0; hero.lifting = false; hero.crouch = false;
  // a cena do abraço, tirada do vídeo, começa com o herói a DUO_DX células da moça, do outro lado do vão
  winData.side = 1; hero.x = girl.x + DUO_DX; hero.dir = -1; girl.dir = 1;
  if (temMusica()) musicaEm(1933 / VFPS, false); else SFX.win();
  // o fim da abertura: os créditos da direção, o abraço, o casal com o coração crescendo e o logotipo
  tocar([close('direcao'), { tipo: 'duo', a: 1989, b: 2128 }, close('casal'), { tipo: 'logo', a: 2191, b: 2307 }], () => { winData.fimT = 0; });
}
function startGameOver() { setState('over'); overData = { pieces: null }; SFX.over(); musicaPara(); }
