// Grava o percurso automático em PNGs (para conferir glitches): precisa de ?dbg=1 e de um receptor HTTP em 127.0.0.1:8124
// (POST /?name=arquivo.png grava o corpo). Uso no console: await gravar(prefixo, cadaN, escala)
window.gravar = async (pref = 'p', cada = 12, escala = 0.5) => {
  const j = window.__jogo, s = document.getElementById('screen');
  const t = document.createElement('canvas'); t.width = Math.round(s.width * escala); t.height = Math.round(s.height * escala);
  const tc = t.getContext('2d'); tc.imageSmoothingEnabled = false;
  let k = 0, fila = [];
  const snap = () => { tc.drawImage(s, 0, 0, t.width, t.height); const nome = `${pref}_${String(k++).padStart(3, '0')}.png`;
    fila.push(new Promise(r => t.toBlob(b => fetch('http://127.0.0.1:8124/?name=' + nome, { method: 'POST', body: b }).then(r), 'image/png'))); };
  const ff = j.fastForward; let n = 0;
  j.fastForward = m => { for (let i = 0; i < m; i++) { ff(1); if (++n % cada === 0) snap(); } };
  const src = await (await fetch('/ferramentas/teste-percurso.js?' + Date.now())).text();
  const log = await eval(src);
  j.fastForward = ff; await Promise.all(fila); return { log, quadros: k };
};
