// ===================================================================
// Passo da lógica (60 por segundo)
// ===================================================================
function update() {
  frame++; stateT++;
  if (emMontagem()) { if (!paused) passoMontagem(); }
  else if (state === 'title') { if (pressed.start || pressed.jump) startGame(); }
  else if (state === 'play' && !paused) {
    playFrames++;
    if (caption) { caption.t++; if (caption.t > caption.dur) caption = null; }
    for (const p of pendentes) p.t--;
    const prontos = pendentes.filter(p => p.t <= 0); pendentes = pendentes.filter(p => p.t > 0);
    for (const p of prontos) p.f();
    if (!emMontagem()) { updateHero(); updateVillain(); updateCroc(); updateGirl(); updateRaio(); passoCreditos(); }
    updateShards();
  } else if (state === 'win') {
    if (winData.fimT >= 0) { winData.fimT++; if (winData.fimT > 40 && (pressed.start || pressed.jump)) { musicaPara(); setState('title'); } }
  } else if (state === 'over') {
    updateShards();
    if (stateT > 200 && (pressed.start || pressed.jump)) setState('title');
  }
  pressed.jump = pressed.punch = pressed.kick = pressed.start = pressed.up = false;
}
