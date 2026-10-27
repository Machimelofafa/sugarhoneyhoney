// ===================================================================
// Entrada
// ===================================================================
const KEYMAP = { ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right', ArrowUp: 'up', KeyW: 'up', ArrowDown: 'down', KeyS: 'down', KeyZ: 'jump', Space: 'jump', KeyK: 'jump', KeyX: 'punch', KeyJ: 'punch', KeyC: 'kick', KeyL: 'kick' };
const EDGE = { jump: 1, punch: 1, kick: 1, up: 1 };
const pausa = () => { if (state === 'play' || state === 'intro') { paused = !paused; musicaPausa(paused); } };
addEventListener('keydown', e => {
  audioOn();
  const k = KEYMAP[e.code];
  if (k) { e.preventDefault(); if (!keys[k] && EDGE[k]) pressed[k] = true; keys[k] = true; }
  if (e.code === 'Enter') { pressed.start = true; e.preventDefault(); }
  if (e.repeat) return;                      // segurar a tecla não fica ligando e desligando
  if (e.code === 'KeyT') toggleCrt();
  if (e.code === 'KeyM') toggleSom();
  if (e.code === 'KeyP' || e.code === 'Escape') pausa();
});
addEventListener('keyup', e => { const k = KEYMAP[e.code]; if (k) keys[k] = false; });
addEventListener('blur', () => { for (const k in keys) keys[k] = false; if (state === 'play' && !DBG && !paused) pausa(); });
document.addEventListener('visibilitychange', () => { if (document.hidden && state === 'play' && !DBG && !paused) pausa(); });
screen.addEventListener('pointerdown', () => { audioOn(); if (paused) pausa(); else pressed.start = true; });
for (const b of document.querySelectorAll('.tbtn')) {
  const k = b.dataset.k;
  if (k === 'pause') { b.addEventListener('click', e => { e.preventDefault(); audioOn(); pausa(); }); continue; }
  // ativado pelo teclado (Enter/Espaço com o botão em foco): um toque rápido
  b.addEventListener('click', e => { if (e.detail === 0) { if (EDGE[k]) pressed[k] = true; else { keys[k] = true; setTimeout(() => { keys[k] = false; }, 180); } } });
  const on = e => { e.preventDefault(); audioOn(); if (b.setPointerCapture) b.setPointerCapture(e.pointerId); if (!keys[k] && EDGE[k]) pressed[k] = true; keys[k] = true; b.classList.add('on'); if (k === 'jump' && state !== 'play') pressed.start = true; };
  const off = e => { e.preventDefault(); keys[k] = false; b.classList.remove('on'); };
  b.addEventListener('pointerdown', on);
  b.addEventListener('pointerup', off);
  b.addEventListener('pointercancel', off);
  b.addEventListener('lostpointercapture', off);
  b.addEventListener('contextmenu', e => e.preventDefault());
}
const bCrt = document.getElementById('bCrt'), bSom = document.getElementById('bSom'), bFull = document.getElementById('bFull'), bCred = document.getElementById('bCred');
function save() { try { localStorage.setItem('despedida-config-2', JSON.stringify({ crt, muted, creditos: creditosOn })); } catch (e) { /* sem armazenamento */ } }
function toggleCrt() { crt = !crt; bCrt.setAttribute('aria-pressed', String(crt)); save(); }
function toggleSom() { muted = !muted; bSom.setAttribute('aria-pressed', String(!muted)); musicaVolume(); save(); }
function toggleCred() { creditosOn = !creditosOn; bCred.setAttribute('aria-pressed', String(creditosOn)); save(); }
bCrt.addEventListener('click', e => { toggleCrt(); e.currentTarget.blur(); });
bCred.addEventListener('click', e => { toggleCred(); e.currentTarget.blur(); });
bSom.addEventListener('click', e => { toggleSom(); e.currentTarget.blur(); });
bFull.addEventListener('click', e => {
  e.currentTarget.blur();
  try {
    if (document.fullscreenElement) document.exitFullscreen();
    else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(() => {});
  } catch (err) { /* sem tela cheia aqui */ }
});
document.addEventListener('fullscreenchange', layout);
