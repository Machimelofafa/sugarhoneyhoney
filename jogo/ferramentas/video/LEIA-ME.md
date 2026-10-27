# Atores da abertura, recortados do vídeo

O jogo usa os atores do vídeo da abertura (YouTube `j3jSDuN2qDk`, 1992) em vez de desenhos: herói, vilão, moça e a cena do
abraço final. Esta pasta tem o que gera `jogo/atlas/atlas.png` + `atlas.json` a partir do vídeo. Uso pessoal; não publique
o atlas nem o vídeo.

## Como o vídeo é feito (medido)
- O jogo é o recorte `x=264, y=14, 1408×1058` de cada quadro 1080p. O cenário é um mosaico de 170×238 células
  (8,27 × 4,445 px) que anima; os planos de perto são zooms desse cenário (ver a memória `project-video-geometry`).
- Os atores são vídeo real com efeito de **mosaico de bloco fixo na tela**: 6,95×8,8 px no quadro geral e 13,93×17,75 nos
  close-ups (9,96×13,35 nas escadas). Cada plano tem uma ampliação própria do ator (`Z` em `poses.py`), diferente do zoom
  do cenário. Medida: herói em pé ≈ 283 px no quadro geral, vilão ≈ 265, moça ≈ 215.
- Os quadros 570-598 (luta), 1541-1625 (escada) e vários outros são close-ups de rosto: não entram.

## Reproduzir
```bash
export TRABALHO=$HOME/despedida-trabalho            # quadros e recortes (centenas de MB)
mkdir -p $TRABALHO/fr && cd $TRABALHO
yt-dlp -f 137 -o abertura1080.mp4 https://www.youtube.com/watch?v=j3jSDuN2qDk
ffmpeg -i abertura1080.mp4 -vf "crop=1408:1058:264:14" -q:v 1 fr/f_%04d.jpg     # f_0121 = referencia/fase_visao_geral.png
cd <este diretório> && ./extrair_tudo.sh            # ~10 min; precisa de numpy, opencv-python, scipy
python chute.py && python atlas.py                  # depois de extrair_tudo (as poses novas usam cut/fightk_hero)
python cenario_extra.py && python graficos.py && python closes.py && python logo.py && python creditos.py
yt-dlp -f 140 -o ../../atlas/musica.m4a https://www.youtube.com/watch?v=j3jSDuN2qDk   # o áudio da abertura (opcional)
```

## Arquivos
| arquivo | o que faz |
|---|---|
| `extrair.py` | recorta um ator num intervalo de quadros -> `$TRABALHO/cut/<plano>_<ator>/NNNN.png` (RGBA em px do vídeo) |
| `seg2.py seg3.py seg4.py pal.py` | segmentação por regras de cor + exclusão da paleta do cenário (herói e vilão) |
| `moca.py` | a moça: tudo que é "quente" (r > b+12) sobre o cenário azul/roxo; limpo e simples |
| `cabeca.py` | acrescenta cabelo + rosto acima do ponto mais alto da máscara (cabelo escuro some na paleta) |
| `limpa.py` | tira barras finas do cenário coladas na máscara (abertura grande + reconstrução curta) |
| `dueto.py extrair_dueto.py` | a cena do abraço: herói e moça num recorte só, com origem fixa no quadro do vídeo |
| `poses.py` | **a lista de poses do atlas** (plano, quadro, direção, ampliação `Z`) — edite aqui |
| `atlas.py` | reduz cada recorte à escala do quadro geral e empacota em `jogo/atlas/`; antes apaga cores que só o cenário tem (fio vermelho da placa, oliva das esteiras, verde do jacaré) e pedaços soltos, e acerta a cor do herói por plano (o plano do andar é bem mais escuro) |
| `olhos.py` | blocos do mosaico da faixa dos olhos (quadros 38-98) para a tela-título -> `jogo/atlas/olhos.png` |
| `chute.py` | recorta de novo o chute alto e a joelhada (614-628), que o recorte geral da luta deixava sem pernas -> `cut/fightk_hero/` |
| `cenario_extra.py` | do plano da grade (1495-1716, zoom 3,13): fundo sem grade, a grade que desliza e os 3 estados do alçapão, na grade do cenário -> `jogo/atlas/extra.json` |
| `graficos.py` | o raio (quadro 1803) e o estouro vermelho com estrela (576) na grade do cenário -> `extra.json` |
| `closes.py` | os planos fechados (rostos, tênis, água, coração, casal): uma cor por bloco do mosaico de cada plano (passo medido por plano), sem os letreiros, quadros repetidos uma vez só -> `jogo/atlas/closes.png/json` |
| `logo.py` | o logotipo 3D (2191-2251), JPEG pequeno -> `jogo/atlas/logo.jpg/json` |
| `creditos.py` | texto de cada letreiro + caixa de cada linha e quadros em que aparece (medidos; acertos à mão no fim) -> `jogo/atlas/creditos.json` |
| `folha.py ver.py tira.py` | folhas de contato dos recortes e das poses (para escolher quadros e conferir proporções) |
| `medir_mosaico.py medz.py` | medem o passo do mosaico e a ampliação do herói por plano |
| `antigo/` | a primeira tentativa (amostragem em grade, `z` chutados) — superada |

## No jogo
`jogo/src/js/20-atores.js` redesenha o ator ao vivo na grade do mosaico (cobertura de cada bloco >= 42 %), então o movimento
mistura as cores dos blocos como no vídeo. Depois de mudar `poses.py` rode `atlas.py` e `python3 jogo/montar.py`.
Teste local: `python3 -m http.server 8123 --directory jogo` e abra `http://localhost:8123/index.html?dbg=1`
(`?dbg=1` liga `window.__jogo`: `startGame`, `setHero`, `fastForward`, `folha(ids)` com todas as poses etc.).
