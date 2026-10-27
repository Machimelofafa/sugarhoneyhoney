# Jogo da abertura de "Despedida de Solteiro" (1992)

Recriação pessoal do videogame fictício da abertura da novela. Os atores (herói, vilão, moça e o abraço final) são
recortes do próprio vídeo, redesenhados ao vivo no efeito de mosaico do original; o cenário vem de `cenario.json`;
os olhos da tela-título são os blocos do mosaico da própria abertura.

Percurso (o da abertura): píer → fosso de fogo (três chamas sobem e descem em onda; passe quando apagam ou pule as
baixas) → escada da esquerda → esteira que sobe → vilão (tem que nocautear; abaixe sob o chute alto) → jacaré (passe
por cima quando ele deita) → chão cinza até o fim → vire e suba a escada rolante → teto → alçapão (abre e fecha;
quem está em cima cai na água) → grade entre os postes (espere subir e passe agachado; se descer em cima, machuca)
→ o raio quebra o teto e abre um vão entre o herói e a moça → pare do lado de cá e aperte X para dar a mão a ela.
O rio é fundo: cair nele afunda. O vilão nocauteado se levanta, mas já não luta.

Montagem: como na abertura, o jogo corta para os planos fechados do vídeo nos mesmos momentos (o golpe na luta, os
olhos da moça no nocaute, os tênis e o sorriso depois do jacaré, ela olhando para cima, a queda no alçapão com o
coração que racha, a grade, o raio, o abraço, o casal e o logotipo). A abertura do jogo e o fim repetem a linha do
tempo do vídeo (quadros 1-352 e 1933-2307). Os créditos voltam como texto, no lugar e no tempo em que aparecem
(botão Créditos desliga). Enter pula a montagem.

- `index.html` — o jogo, num arquivo só. **Gerado**: `python3 montar.py`.
- `src/shell-topo.html` — a casca (estilos, canvas, botões). `src/js/NN-*.js` — os módulos, concatenados em ordem:
  `00-base` constantes/telas · `10-cenario` camadas, corações, grade, alçapão, vão, raio · `20-atores` atlas + mosaico
  ao vivo · `30-audio` efeitos e música · `40-fase` pisos, esteira vertical, rio, fogo, jacaré, grade, alçapão, vão
  (o dano vem dos pixels da chama e do bicho) · `50-heroi` estado e física · `60-inimigos` vilão, jacaré e moça ·
  `65-montagem` planos fechados e créditos · `70-logica` passo · `75-quadros` que pose cada ator mostra, HUD ·
  `80-telas` título, fim · `85-saida` escala, filtro de TV, texto · `90-entrada` teclado/toque · `99-main` laço e
  ganchos de teste.
- `cenario.json` — cenário extraído do vídeo (170×238 células, 31 cores, camadas animadas).
  `ferramentas/reparo_cenario.py` refez o píer (tinha um fantasma do herói), o chão cinza do jacaré (virara verde) e
  os ladrilhos das esteiras (setas borradas) a partir de quadros limpos do vídeo.
- `atlas/` — gerado por `ferramentas/video/` (ver o LEIA-ME de lá): `atlas.png/json` (atores), `olhos.png/json`
  (título), `extra.json` (grade, alçapão, raio, estouro), `closes.png/json` (planos fechados), `logo.jpg/json`,
  `creditos.json`, `musica.m4a` (o áudio da abertura, formato 140 do YouTube; uso pessoal). A música toca pelo WebAudio:
  a abertura e o fim seguem a linha do tempo do vídeo; na fase ela fica num laço de 16 compassos (13,143 → 43,948 s,
  o trecho que se repete na música).
- `ferramentas/teste-percurso.js` — percurso automático (fogo → escada → esteira → luta → jacaré → rolante → abraço)
  para colar no console; `ferramentas/grava.js` grava esse percurso em PNGs para conferir glitches.
- `antigo/` — a versão com atores desenhados à mão, só de referência.

Teclas: ← → andar · Z ou ↑ pular · ↓ abaixar · X soco (e dar a mão) · C chute · P pausa · T filtro de TV · M som.
Teste: `python3 -m http.server 8123 --directory jogo` e `http://localhost:8123/index.html?dbg=1`
(`?dbg=1` expõe `window.__jogo` e não pausa ao perder o foco).
