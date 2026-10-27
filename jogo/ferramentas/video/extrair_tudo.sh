#!/bin/bash
# Recorta todos os atores de todos os planos e monta o atlas + index.html.
# uso: TRABALHO=/algum/diretorio PY=/caminho/do/python ./extrair_tudo.sh
# precisa de $TRABALHO/fr/f_NNNN.jpg (ver LEIA-ME.md) e de python com numpy, opencv-python e scipy.
cd "$(dirname "$0")"
PY=${PY:-python3}
export OMP_NUM_THREADS=2 OPENCV_FOR_THREADS_NUM=2
run() { "$PY" extrair.py "$@" & }
#   plano  ator  intervalos de quadros (só corpo inteiro; os close-ups de rosto ficam de fora)
run vil    hero 358 424
run vil    vil  358 424
run fight  hero 490 568 602 640
run fight  vil  490 568 602 640
run croc   hero 694 778
run water  hero 1084 1126
run scaf   hero 1490 1540 1626 1700
run ur     hero 997 1070
run fire   hero 164 206
run girlA  girl 426 487
run girlB  girl 1372 1486
run girlC  girl 1780 1890
wait
"$PY" extrair_dueto.py       # a cena do abraço (herói e moça juntos), quadros 1990-2128
"$PY" chute.py               # o chute alto e a joelhada, recortados de novo (o recorte da luta perdia as pernas)
"$PY" atlas.py               # recortes escolhidos em poses.py -> ../../atlas/atlas.png + atlas.json
"$PY" olhos.py               # faixa dos olhos da abertura -> ../../atlas/olhos.png + olhos.json
"$PY" cenario_extra.py       # grade e alçapão do alto -> ../../atlas/extra.json
"$PY" graficos.py            # raio e estouro do golpe -> extra.json
"$PY" closes.py              # planos fechados da montagem -> ../../atlas/closes.png + closes.json
"$PY" logo.py                # logotipo 3D -> ../../atlas/logo.jpg + logo.json
"$PY" creditos.py            # letreiros -> ../../atlas/creditos.json
python3 ../../montar.py      # index.html
