// ===================================================================
// Cenário extraído da abertura de 1992: grade de 170 × 238 células,
// cada célula 1,86 vez mais larga que alta (8,27 × 4,445 px no quadro).
// Os atores vivem na mesma tela, mas num mosaico próprio (ver 20-atores.js).
// ===================================================================
const A = JSON.parse(document.getElementById('cenario').textContent);
const W = A.W, H = A.H, ASPECT = 1.86;
const PAL = A.pal;
const STEP_FRAMES = 10;          // o cenário original anima a ~6 passos por segundo
const FONT = "'Jost', 'Futura', 'Century Gothic', 'Avenir Next', 'Trebuchet MS', sans-serif";
const OUT = '#000000';
const DBG = new URLSearchParams(location.search).has('dbg');   // ganchos de teste locais
const EXTRA = A.extra;           // grade, alçapão, raio e estouro (ferramentas/video/cenario_extra.py, graficos.py)
const CLOSES = A.closes;         // planos fechados da montagem (ferramentas/video/closes.py)
const LOGO = A.logo;             // logotipo 3D do fim (ferramentas/video/logo.py)
const CREDITOS = A.creditos;     // letreiros: linhas, caixas em px do quadro e quadros do vídeo (ferramentas/video/creditos.py)
const VFPS = 29.97;              // quadros por segundo do vídeo da abertura

// ---------- utilidades ----------
const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
function hexToRgb(h) { const n = parseInt(h.slice(1), 16); return [n >> 16, (n >> 8) & 255, n & 255]; }
function R(ctx, x, y, w, h, c) { ctx.fillStyle = c; ctx.fillRect(x, y, w, h); }
function unb64(s) { const t = atob(s), a = new Uint8Array(t.length); for (let i = 0; i < t.length; i++) a[i] = t.charCodeAt(i); return a; }
const PALRGB = PAL.map(hexToRgb);

// ---------- telas ----------
// buf: o cenário na grade de células; screen: a saída (escala inteira na vertical, célula 1,86:1)
const buf = document.createElement('canvas'); buf.width = W; buf.height = H;
const g = buf.getContext('2d');
const screen = document.getElementById('screen');
const sc = screen.getContext('2d');
let K = 1, CW = 2, F = 1;        // F: px da tela por px do quadro geral do vídeo
