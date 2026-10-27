// ===================================================================
// Laço principal (60 quadros por segundo, passo fixo)
// ===================================================================
let last = 0, acc = 0, congelado = false;
function loop(t) {
  if (!last) last = t;
  acc += Math.min(100, t - last); last = t;
  while (acc >= 1000 / 60) { if (!congelado) update(); acc -= 1000 / 60; }
  render();
  requestAnimationFrame(loop);
}
function start(data) {
  try { const s = JSON.parse(localStorage.getItem('despedida-config-2') || '{}'); crt = s.crt !== false; muted = !!s.muted; creditosOn = !!s.creditos; } catch (e) { /* sem armazenamento */ }
  if (data && typeof data.crt === 'boolean') crt = data.crt;
  if (data && typeof data.muted === 'boolean') muted = data.muted;
  bCrt.setAttribute('aria-pressed', String(crt));
  bSom.setAttribute('aria-pressed', String(!muted));
  bCred.setAttribute('aria-pressed', String(creditosOn));
  if (matchMedia('(pointer: coarse)').matches) document.body.classList.add('touch');
  montarAnimacoes();
  newGame();
  layout();
  addEventListener('resize', layout);

  // ganchos de teste locais (?dbg=...), não aparecem no jogo publicado
  const q = new URLSearchParams(location.search);
  if (DBG) window.__jogo = {
    get state() { return state; }, hero: () => hero, villain: () => villain, croc: () => croc, girl: () => girl, ANIM, SP, PLATS, setState, startGame, keys, pressed,
    setHero: (x, y) => { hero.x = x; hero.y = y; hero.lifting = false; hero.vy = 0; hero.ground = findLanding(x, y - 1, y + 1); },
    setCheckpoint: (x, y) => { checkpoint = { x, y }; }, FOGO, quadroDoFogo, fogoPega, playFrames: () => playFrames, setPlayFrames: n => { playFrames = n; },
    setVillain: o => Object.assign(villain, o), setPaused: v => { paused = v; }, congelar: v => { congelado = v; }, gameOver: () => startGameOver(), setCaption: c => { caption = c; }, frame: () => frame, stateT: () => stateT,
    fastForward: n => { for (let i = 0; i < n; i++) update(); render(); },
    montagem, pulaMontagem: () => { while (montagem.item) { montagem.t = 1e9; passoMontagem(); } }, tocar, close, CL, GRADE, gradeDy, ALC, alcapaoFase, VAO, vao,
    feitos: () => feitos, setFeitos: o => Object.assign(feitos, o), raio: () => raio, setGirl: o => Object.assign(girl, o), cred, CREDITOS,
    escHeroi, alturaHeroi, startWin, render, MUS, musicaPos: () => actx ? musicaPos() : 0, actx: () => actx,
    // folha de poses com o mosaico real: ids em grade, 8 por linha, pés numa linha de base
    folha: (ids, flipAll) => {
      const w = screen.width, h = screen.height;
      cc.fillStyle = '#1a1030'; cc.fillRect(0, 0, w, h);
      ids.forEach((id, k) => {
        const col = k % 8, row = Math.floor(k / 8);
        const xv = 90 + col * 172, yv = 340 + row * 345;
        desenharAtor(cc, F, id, xv, yv, flipAll ? SP[id].f !== -1 : false, 1);
        cc.fillStyle = '#9ff'; cc.font = Math.round(11 * F * 1.6) + 'px sans-serif'; cc.fillText(id + (SP[id].f > 0 ? ' >' : ' <'), (xv - 60) * F, (yv + 14) * F);
      });
      sc.drawImage(comp, 0, 0);
    },
  };
  if (q.get('dbg') === 'step') { render(); return; }
  requestAnimationFrame(loop);
}
const hot = window.claude && window.claude.hot;
if (hot && hot.snapshot) hot.snapshot(() => ({ crt, muted }));
carregarAtlas(() => {
  if (hot && hot.ready) hot.ready(start); else start((hot && hot.data) || {});
});
