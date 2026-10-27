#!/bin/bash
PY=/tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/venv-cv/bin/python
cd /tmp/claude-1000/-home-davi-projects-despedida-de-solteiro/07df2b5d-2815-479c-8871-a5d0d614de38/scratchpad/lab
$PY spr2.py vil hero 358 424 3 2.13 > log_vil_hero.txt 2>&1 &
$PY spr2.py vil vil 358 424 3 1.70 > log_vil_vil.txt 2>&1 &
$PY spr2.py fight hero 490 640 4 2.17 > log_fight_hero.txt 2>&1 &
$PY spr2.py fight vil 490 640 4 2.88 > log_fight_vil.txt 2>&1 &
$PY spr2.py water hero 1086 1126 3 2.15 > log_water.txt 2>&1 &
$PY spr2.py fire hero 166 204 2 2.15 > log_fire.txt 2>&1 &
$PY spr2.py scaf hero 1492 1716 4 2.1 > log_scaf.txt 2>&1 &
$PY spr2.py ur hero 998 1080 2 1.83 > log_ur.txt 2>&1 &
$PY spr2.py girlA girl 426 490 3 3.39 > log_gA.txt 2>&1 &
$PY spr2.py girlB girl 1372 1488 4 3.35 > log_gB.txt 2>&1 &
$PY spr2.py girlC girl 1778 1890 4 3.35 > log_gC.txt 2>&1 &
wait
