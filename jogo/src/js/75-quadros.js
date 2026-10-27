// ===================================================================
// Que quadro do atlas cada ator mostra, e o desenho dos atores
// ===================================================================
const pick = (ator, nome, i) => { const l = ANIM[ator][nome]; return l[((Math.floor(i) % l.length) + l.length) % l.length]; };

function heroSprite() {
  const h = hero;
  const moving = (keys.left || keys.right) && state === 'play';
  if (h.state === 'burn') return pick('hero', 'hurt', 1);
  if (h.state === 'sink') return pick('hero', 'swim', h.walk / 5);
  if (h.state === 'trap' || h.state === 'abismo') return pick('hero', 'fall', 1);
  if (h.state === 'hurt') return pick('hero', 'hurt', h.hurtT > 12 ? 0 : 1);
  if (h.state === 'punch') return pick('hero', 'punch', h.punchT < 6 ? 0 : h.punchT < 13 ? 2 : 1);
  if (h.state === 'kick') return h.kickT < 8 ? pick('hero', 'kick', 0) : h.kickT < 18 ? pick('hero', 'kick', h.kickT < 13 ? 1 : 2) : pick('hero', 'knee', h.kickT < 24 ? 0 : 1);
  if (h.lifting) return pick('hero', 'climb', frame / 9);
  if (!h.ground) return h.vy < 0 ? pick('hero', 'jump', h.vy < -1.6 ? 0 : 1) : pick('hero', 'fall', h.vy > 2 ? 1 : 0);
  const luta = vilaoDeCabeca() && h.ground.id === 'vfloor' && Math.abs(h.x - villain.x) < 40;
  if (h.crouch) {
    if (luta) return pick('hero', 'duck', frame / 14);              // esquiva do chute alto
    return moving ? pick('hero', 'crawl', h.walk / 2.2) : pick('hero', 'crouch', frame / 30);
  }
  if (h.landT > 0) return pick('hero', 'down', 0);
  if (moving) return pick('hero', 'walk', h.walk / 4.5);     // ritmo do vídeo: troca de pose a cada ~9 quadros andando
  return luta ? pick('hero', 'guard', frame / 14) : pick('hero', 'idle', 0);
}
function villainSprite() {
  const v = villain;
  if (v.state === 'down') return pick('vil', 'down', v.t > 12 ? 1 : 0);
  if (v.state === 'rise') return v.t < 8 ? pick('vil', 'down', 1) : v.t < 16 ? pick('vil', 'down', 0) : pick('vil', 'hurt', v.t < 24 ? 1 : 0);
  if (v.state === 'hurt') return pick('vil', 'hurt', v.t > 9 ? 1 : 0);
  if (v.state === 'windup') return pick('vil', 'guard', 2);
  if (v.state === 'kick') return pick('vil', 'kick', 0);
  if (v.state === 'pwind') return pick('vil', 'guard', 1);
  if (v.state === 'punch') return pick('vil', 'punch', 0);
  if (v.state === 'walk') return pick('vil', 'walk', v.walk / 2.5);
  if (v.state === 'tonto' && Math.abs(v.x - 62) > 0.5) return pick('vil', 'walk', v.walk / 2.5);
  return pick('vil', 'guard', frame / 16);
}
function girlSprite() {
  const m = girl;
  if (m.estado === 'beira') return raio ? pick('girl', 'fright', frame / 8) : pick('girl', 'edge', frame / 10);
  if (m.estado === 'torce') return pick('girl', 'cheer', frame / 9);
  if (m.estado === 'anda') return pick('girl', 'walk', m.walk / 2.2);
  return pick('girl', 'idle', frame / 8);
}

function actorAlpha() {
  if (state === 'play' || state === 'intro' || state === 'win') return paused ? 0.5 : 1;
  if (state === 'over') return stateT < 40 ? 1 - 0.7 * stateT / 40 : 0;
  return 0;
}
function drawActor(ctx, id, a, alfa, esc) {
  desenharAtor(ctx, F, id, a.x * OVX, a.y * OVY, SP[id].f !== a.dir, alfa, esc);
}
function drawActors(ctx) {
  if (!atlasData) return;
  const al = actorAlpha(); if (al <= 0) return;
  const it = montagem.item;
  if (state === 'win') {
    drawActor(ctx, villainSprite(), villain, al);
    const k = it && it.tipo === 'duo' ? Math.min(DUO_FRAMES - 1, Math.floor(montagem.t / DUO_STEP)) : DUO_FRAMES - 1;
    desenharAtor(ctx, F, ANIM.duo.duo[k], girl.x * OVX, girl.y * OVY, winData.side < 0, al);
    return;
  }
  drawActor(ctx, girlSprite(), girl, al);
  drawActor(ctx, villainSprite(), villain, al);
  const pisca = state === 'play' && (hero.inv > 0 && (hero.inv >> 2) % 2 || hero.state === 'burn' && (hero.burnT >> 1) % 2);
  if (!hero.hidden && !pisca) drawActor(ctx, heroSprite(), hero, al, escHeroi(hero.y));
}
function drawHud() {
  drawHearts(0, state === 'intro' ? 4 : hero.hp);
  drawHearts(1, state === 'intro' ? 4 : villain.hp);
  for (const p of shards) R(g, Math.round(p.x), Math.round(p.y), 1, 1, p.c);
  // estouro vermelho com a estrela amarela no golpe (o do close da luta, pequeno)
  for (const e of estouros) if (e.t < 5 || (e.t >> 1) % 2 === 0) drawImpacto(e.x, e.y, e.t < 3 ? 0.35 + e.t * 0.08 : 0.55);
  // o raio cai no meio do vão, com um clarão
  if (raio && raio.t < 30) {
    if ((raio.t >> 1) % 3 !== 2) drawRaio((VAO.x0 + VAO.x1) / 2, 62);
    if (raio.t < 8) { g.fillStyle = `rgba(255,250,215,${0.55 - raio.t * 0.07})`; g.fillRect(0, 0, W, H); }
  }
}
