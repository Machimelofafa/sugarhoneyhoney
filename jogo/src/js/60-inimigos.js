// ===================================================================
// Vilão, jacaré e a moça
// ===================================================================
// o vilão guarda o piso do meio; não chega perto da esteira para o herói poder subir
const VIL_MIN = 34, VIL_MAX = 92;
function updateVillain() {
  const v = villain;
  v.t++; if (v.hitLock > 0) v.hitLock--;
  // nocauteado: fica no chão um tempo e se levanta (o quadro geral da abertura mostra ele se erguendo), mas já não luta
  if (v.state === 'down') { if (v.t > 220) { v.state = 'rise'; v.t = 0; } return; }
  if (v.state === 'rise') { if (v.t > 32) { v.state = 'tonto'; v.t = 0; } return; }
  if (v.state === 'tonto') {                // treina golpes sozinho no piso dele, como no quadro geral do fim
    const alvo = 62, d = alvo - v.x;
    if (Math.abs(d) > 0.5) { v.x += Math.sign(d) * 0.15; v.walk += 0.15; v.dir = Math.sign(d); }
    return;
  }
  if (v.cool > 0) v.cool--;
  const heroHere = !hero.hidden && hero.state !== 'burn' && hero.y > 115 && hero.y < 145 && hero.x < 104;
  const d = hero.x - v.x;
  if (v.state === 'hurt') { if (v.t > 20) { v.state = 'guard'; v.t = 0; } return; }
  if (v.state === 'windup') { if (v.t >= 18) { v.state = 'kick'; v.t = 0; SFX.punch(); } return; }
  if (v.state === 'pwind') { if (v.t >= 7) { v.state = 'punch'; v.t = 0; SFX.punch(); } return; }
  if (v.state === 'kick' || v.state === 'punch') {
    // chute alto (passa por cima de quem se abaixa) ou soco, mais curto e rápido
    const chute = v.state === 'kick', alc = chute ? 20 : 15;
    const box = { x0: Math.min(v.x + v.dir * 4, v.x + v.dir * alc), x1: Math.max(v.x + v.dir * 4, v.x + v.dir * alc), y0: v.y - (chute ? 58 : 48), y1: v.y - (chute ? 38 : 30) };
    if (v.t >= 2 && v.t <= (chute ? 10 : 7) && overlap(heroBox(), box)) golpeNoHeroi(chute ? 'kick' : 'soco');
    if (v.t >= (chute ? 16 : 12)) { v.state = 'guard'; v.t = 0; v.cool = chute ? 38 : 30; }
    return;
  }
  if (heroHere) {
    v.dir = d >= 0 ? 1 : -1;
    if (Math.abs(d) > 17) {
      const nx = clamp(v.x + v.dir * 0.24, VIL_MIN, VIL_MAX);
      v.state = nx !== v.x ? 'walk' : 'guard';
      v.walk += Math.abs(nx - v.x); v.x = nx;
    } else {
      v.state = 'guard';
      if (v.cool <= 0) { v.state = Math.abs(d) <= 13 && Math.random() < 0.45 ? 'pwind' : 'windup'; v.t = 0; }
    }
  } else { v.state = 'guard'; v.dir = -1; }
}
function golpeNoHeroi(kind) {
  const y = villain.y - (kind === 'kick' ? 50 : 40);
  if (!hurtHero(villain.x, kind)) return;
  estouros.push({ x: hero.x - villain.dir * 2, y, t: 0 });
  // o primeiro chute que pega: o close do herói atingido, com a estrela amarela sobre a explosão vermelha
  if (kind === 'kick' && !feitos.impacto) { feitos.impacto = true; tocar([close('impacto')]); }
}

// jacaré: deitado → levantando → em pé → abaixando (quadros tirados da abertura)
const CROC_FASES = { down: 150, rise: 12, up: 70, lower: 12 };
function updateCroc() {
  croc.t++;
  if (croc.t >= CROC_FASES[croc.phase]) {
    croc.t = 0;
    croc.phase = { down: 'rise', rise: 'up', up: 'lower', lower: 'down' }[croc.phase];
    if (croc.phase === 'rise' && Math.abs(hero.x - 112) < 50 && Math.abs(hero.y - 139) < 40) SFX.snap();
  }
}
function crocFrame() {
  if (croc.phase === 'down') return 0;
  if (croc.phase === 'rise') return 1;
  if (croc.phase === 'lower') return 4;
  return Math.floor(croc.t / STEP_FRAMES) % 2 ? 3 : 2;
}

// a moça: anda de um lado para o outro no alto e gira, como nos planos dela; torce quando o herói chega lá em cima;
// depois do raio fica na beira do vão, perdendo o equilíbrio
function updateGirl() {
  const m = girl; m.t++;
  if (m.estado === 'beira') { m.x = MOCA_BEIRA; m.dir = 1; return; }
  if (state === 'play' && !hero.hidden && hero.y < 90) { m.estado = 'torce'; m.dir = hero.x > m.x ? 1 : -1; return; }
  if (m.estado === 'torce') { m.estado = 'espera'; m.t = 0; m.pausa = 40; }
  if (m.estado === 'espera') { if (m.t > m.pausa) { m.estado = 'anda'; m.alvo = m.x < 30 ? 44 : 16; } return; }
  const d = m.alvo - m.x;
  if (Math.abs(d) < 0.3) { m.estado = 'espera'; m.t = 0; m.pausa = 90 + Math.floor(Math.random() * 100); m.dir = -m.dir; return; }
  m.dir = Math.sign(d); m.x += m.dir * 0.22; m.walk += 0.22;
}
