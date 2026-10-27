// Percurso automático da fase, para conferir que dá para ganhar: cola no console (ou no javascript_tool) da página
// aberta com ?dbg=1. Devolve o registro de cada trecho; a última linha diz o estado final ('win' = deu a mão a ela).
// Percurso: píer → fogo → escada → esteira → vilão → jacaré → rolante → alçapão → grade (agachado) → raio → vão → resgate.
// As montagens (planos fechados) são puladas assim que aparecem.
(async () => {
  const j = window.__jogo; j.congelar(true); j.startGame(); j.pulaMontagem(); j.setCaption(null);
  const h = j.hero(), v = j.villain(), c = j.croc(); const log = [];
  const L = (...a) => log.push(a.map(x => typeof x === 'number' ? +x.toFixed(1) : x).join(' '));
  const step = (n = 1) => { for (let i = 0; i < n; i++) { j.fastForward(1); if (j.montagem.item) j.pulaMontagem(); } };
  const ate = (cond, max, antes) => { let n = 0; while (!cond() && n++ < max && j.state === 'play') { if (antes) antes(); step(); } return n; };
  const solta = () => { for (const k of ['left', 'right', 'up', 'down']) j.keys[k] = false; };
  const gid = () => h.ground && h.ground.id;
  // 1) fogo: espera a chama da direita (FOGO.slots[2]) começar a apagar e atravessa andando
  const C = j.FOGO.slots[2];
  let n = ate(() => ((j.playFrames() - C.atraso) % j.FOGO.ciclo + j.FOGO.ciclo) % j.FOGO.ciclo === 0, 400); L('espera o fogo', n);
  j.keys.left = true; n = ate(() => gid() === 'patamar' || h.lifting, 600); L('fogo + escada', n, 'hp', h.hp, gid(), h.x, h.y);
  n = ate(() => gid() === 'vfloor', 200); j.keys.left = false; L('esteira', n, 'hp', h.hp, gid(), h.x, h.y);
  // 2) luta: aproxima; abaixa quando o vilão arma o chute alto; soca e chuta até ele cair
  n = ate(() => v.state === 'down', 3000, () => {
    const d = v.x - h.x; j.keys.down = v.state === 'windup' || v.state === 'kick';
    j.keys.left = !j.keys.down && d < -19; j.keys.right = !j.keys.down && d > 19;
    if (!j.keys.down && Math.abs(d) <= 21 && h.state === 'normal' && h.ground) { h.dir = d < 0 ? -1 : 1; if (Math.random() < 0.5) j.pressed.punch = true; else j.pressed.kick = true; }
  });
  solta(); L('luta', n, 'hp', h.hp, 'vilão', v.hp, v.state);
  // 3) jacaré: vai até a beira do piso, espera ele deitar e atravessa por cima
  j.keys.right = true; n = ate(() => h.x >= 92, 400); j.keys.right = false;
  n += ate(() => c.phase === 'down' && c.t < 10, 400);
  j.keys.right = true; n += ate(() => gid() === 'ledgeR' && h.x > 135, 300); L('jacaré', n, 'hp', h.hp, gid(), h.x);
  // 4) chão cinza até o fim → vira para a esquerda e entra na escada rolante → sobe até o teto
  n = ate(() => h.x >= 165.9, 200); j.keys.right = false; j.keys.left = true;
  n += ate(() => gid() === 'rolante', 60); L('pé da rolante', n, gid(), h.x, h.y);
  n = ate(() => gid() === 'roof', 900); j.keys.left = false; L('teto', n, 'hp', h.hp, h.x);
  // 5) alçapão: espera ele fechar e atravessa até a frente da grade
  n = ate(() => j.alcapaoFase() === 'fechando', 400); n += ate(() => j.alcapaoFase() === 'fechado', 20);
  j.keys.left = true; n += ate(() => h.x <= j.GRADE.x1 + 4.6 || h.hidden, 200); j.keys.left = false;
  L('alçapão', n, 'hp', h.hp, h.x, h.state);
  // 6) grade: espera subir, agacha e passa por baixo
  n = ate(() => j.gradeDy() <= j.GRADE.alto + 0.5, 600);
  j.keys.down = true; j.keys.left = true; n += ate(() => h.x < j.GRADE.x0 - 6, 200); j.keys.down = false;
  L('grade', n, 'hp', h.hp, h.x, h.state);
  // 7) o raio abre o vão; anda até o ponto do resgate e dá a mão
  n = ate(() => j.vao.aberto, 400); n += ate(() => h.x <= j.girl().x + 32, 300); j.keys.left = false;
  j.pressed.punch = true; step(); L('resgate', n, 'hp', h.hp, h.x, j.state);
  L('fim', 'estado', j.state, 'hp', h.hp, 'quadros', j.frame());
  j.congelar(false); return log;
})()
