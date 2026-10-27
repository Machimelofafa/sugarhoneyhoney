// ===================================================================
// Som
// ===================================================================
let actx = null, muted = false;
function audioOn() {
  if (!actx) { try { actx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { actx = null; } }
  if (actx && actx.state === 'suspended') actx.resume();
  carregaMusica();
}
function tone(f0, f1, dur, type = 'square', vol = 0.05, delay = 0) {
  if (muted || !actx) return;
  const t = actx.currentTime + delay, o = actx.createOscillator(), gn = actx.createGain();
  o.type = type; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
  gn.gain.setValueAtTime(vol, t); gn.gain.exponentialRampToValueAtTime(0.0008, t + dur);
  o.connect(gn).connect(actx.destination); o.start(t); o.stop(t + dur + 0.02);
}
function noise(dur, vol = 0.06, delay = 0) {
  if (muted || !actx) return;
  const t = actx.currentTime + delay, n = Math.floor(actx.sampleRate * dur);
  const b = actx.createBuffer(1, n, actx.sampleRate), d = b.getChannelData(0);
  for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
  const src = actx.createBufferSource(), gn = actx.createGain(), f = actx.createBiquadFilter();
  f.type = 'highpass'; f.frequency.value = 700;
  src.buffer = b; gn.gain.value = vol;
  src.connect(f).connect(gn).connect(actx.destination); src.start(t);
}
const SFX = {
  jump: () => tone(260, 640, 0.13),
  punch: () => noise(0.06, 0.07),
  hit: () => { tone(200, 80, 0.14, 'square', 0.07); noise(0.08, 0.06); },
  hurt: () => tone(520, 110, 0.32, 'sawtooth', 0.05),
  heart: () => tone(988, 988, 0.07, 'square', 0.04),
  snap: () => { noise(0.1, 0.08); tone(140, 70, 0.1, 'square', 0.05); },
  splash: () => { noise(0.25, 0.06); noise(0.12, 0.04, 0.12); },
  raio: () => { noise(0.6, 0.12); tone(110, 35, 0.7, 'sawtooth', 0.08); },
  ko: () => [392, 330, 262, 196].forEach((f, i) => tone(f, f, 0.12, 'square', 0.05, i * 0.1)),
  win: () => [523, 659, 784, 1046, 784, 1046].forEach((f, i) => tone(f, f, 0.16, 'square', 0.05, i * 0.13)),
  over: () => [392, 370, 349, 330, 262].forEach((f, i) => tone(f, f * 0.98, 0.22, 'triangle', 0.07, i * 0.2)),
  start: () => [262, 330, 392, 523].forEach((f, i) => tone(f, f, 0.09, 'square', 0.04, i * 0.07)),
};

// ---------- música: o áudio da abertura (atlas/musica.*), tocado pelo WebAudio para o laço da fase não ter emenda ----------
// A abertura do jogo e o fim repetem a linha do tempo do vídeo, então a música entra no mesmo ponto. Na fase ela fica num
// laço de 16 compassos: o trecho que começa em 13,1 s volta igual em 43,9 s (medido pela autossimilaridade, tempo a tempo);
// as pontas foram afinadas pela correlação da onda, para a emenda cair em fase e em cima de um tempo da batida.
const MUS = { buf: null, src: null, ganho: null, ini: 0, t0: 0, laco: false, A: 13.143, B: 43.9477, carregando: false, pendente: null, pausada: null };
const temMusica = () => !!A.musica;
function carregaMusica() {
  if (!A.musica || MUS.buf || MUS.carregando || !actx) return;
  MUS.carregando = true;
  const bin = unb64(A.musica.slice(A.musica.indexOf(',') + 1));
  actx.decodeAudioData(bin.buffer, b => {
    MUS.buf = b;
    if (MUS.pendente) { const [seg, laco, t] = MUS.pendente; MUS.pendente = null; musicaEm(seg + actx.currentTime - t, laco); }
  }, () => { MUS.carregando = false; });
}
function musicaEm(seg, laco) {
  musicaPara();
  if (!actx || !A.musica) return;
  if (!MUS.buf) { MUS.pendente = [seg, laco, actx.currentTime]; carregaMusica(); return; }
  if (!MUS.ganho) { MUS.ganho = actx.createGain(); MUS.ganho.connect(actx.destination); }
  musicaVolume();
  const s = actx.createBufferSource(); s.buffer = MUS.buf;
  if (laco) { s.loop = true; s.loopStart = MUS.A; s.loopEnd = MUS.B; }
  s.connect(MUS.ganho); s.start(0, clamp(seg, 0, MUS.buf.duration - 0.05));
  MUS.src = s; MUS.ini = seg; MUS.t0 = actx.currentTime; MUS.laco = !!laco;
}
function musicaPos() {
  let p = MUS.ini + actx.currentTime - MUS.t0;
  if (MUS.laco && p > MUS.B) p = MUS.A + (p - MUS.A) % (MUS.B - MUS.A);
  return p;
}
function musicaPara() {
  MUS.pendente = null; MUS.pausada = null;
  if (MUS.src) { try { MUS.src.stop(); } catch (e) { /* já parou */ } MUS.src.disconnect(); MUS.src = null; }
}
function musicaPausa(sim) {            // pausa guardando o ponto; volta de onde parou
  if (sim) { if (MUS.src) { const pos = [musicaPos(), MUS.laco]; musicaPara(); MUS.pausada = pos; } }
  else if (MUS.pausada) { const [p, l] = MUS.pausada; MUS.pausada = null; musicaEm(p, l); }
}
function musicaVolume() { if (MUS.ganho) MUS.ganho.gain.value = muted ? 0 : 0.7; }
