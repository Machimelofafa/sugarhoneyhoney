"""Monta index.html: injeta cenario.json (extraído da abertura) em jogo.src.html."""
import json
from pathlib import Path

aqui = Path(__file__).parent
fonte = (aqui / 'jogo.src.html').read_text(encoding='utf-8')
cenario = json.loads((aqui / 'cenario.json').read_text(encoding='utf-8'))
dados = json.dumps(cenario, separators=(',', ':')).replace('</', '<\\/')
(aqui / 'index.html').write_text(fonte.replace('__CENARIO__', dados), encoding='utf-8')
print('index.html:', len(fonte) + len(dados), 'bytes')
