"""Monta index.html: casca (src/shell-topo.html) + cenário + atlas de atores + olhos do título + peças extras do cenário
+ planos fechados + logotipo + créditos (+ música, se houver atlas/musica.*) + módulos src/js/NN-*.js em ordem."""
import json, base64
from pathlib import Path

aqui = Path(__file__).parent
at = aqui / 'atlas'
casca = (aqui / 'src' / 'shell-topo.html').read_text(encoding='utf-8')
cenario = json.loads((aqui / 'cenario.json').read_text(encoding='utf-8'))
dataurl = lambda p, tipo: f'data:{tipo};base64,' + base64.b64encode(p.read_bytes()).decode()

atlas = json.loads((at / 'atlas.json').read_text(encoding='utf-8'))
cenario['atlas'] = {
    'px': atlas['px'],
    'sprites': {k: {c: v[c] for c in ('x', 'y', 'w', 'h', 'ax', 'ay', 'f')} for k, v in atlas['sprites'].items()},
    'img': dataurl(at / 'atlas.png', 'image/png'),
}
olhos = json.loads((at / 'olhos.json').read_text(encoding='utf-8'))
olhos['img'] = dataurl(at / 'olhos.png', 'image/png')
cenario['olhos'] = olhos          # faixa dos olhos da abertura para a tela-título (ferramentas/video/olhos.py)
cenario['extra'] = json.loads((at / 'extra.json').read_text(encoding='utf-8'))      # grade, alçapão, raio, estouro
closes = json.loads((at / 'closes.json').read_text(encoding='utf-8'))
closes['img'] = dataurl(at / 'closes.png', 'image/png')
cenario['closes'] = closes        # planos fechados da montagem (ferramentas/video/closes.py)
logo = json.loads((at / 'logo.json').read_text(encoding='utf-8'))
logo['img'] = dataurl(at / 'logo.jpg', 'image/jpeg')
cenario['logo'] = logo
cenario['creditos'] = json.loads((at / 'creditos.json').read_text(encoding='utf-8'))
musica = sorted(at.glob('musica.*'))
if musica:                        # áudio da abertura (uso pessoal): toca na abertura, na fase e no fim
    tipo = {'.m4a': 'audio/mp4', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.opus': 'audio/ogg', '.webm': 'audio/webm'}[musica[0].suffix]
    cenario['musica'] = dataurl(musica[0], tipo)

dados = json.dumps(cenario, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
js = '\n'.join(p.read_text(encoding='utf-8') for p in sorted((aqui / 'src' / 'js').glob('[0-9]*.js')))
html = casca.replace('__CENARIO__', dados) + "\n<script>\n(() => {\n'use strict';\n" + js + "\n})();\n</script>\n"
(aqui / 'index.html').write_text(html, encoding='utf-8')
print('index.html:', len(html), 'bytes')
