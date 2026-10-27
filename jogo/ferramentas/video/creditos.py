"""Créditos da abertura: o texto de cada letreiro (lido no vídeo), e medidos no vídeo a caixa de cada linha (px do quadro
1408x1058) e os quadros em que ele aparece. O jogo redesenha cada linha esticada na caixa medida.
saída: jogo/atlas/creditos.json"""
import cv2, numpy as np, json, os
from seg2 import FR
# linhas, quadro em que o letreiro está inteiro, região onde procurar (x0, y0, x1, y1)
CREDITOS = [
    (['PAULO GORGULHO', 'LÚCIA VERÍSSIMO'], 31, (200, 0, 1208, 1058)),
    (['FELIPE CAMARGO', 'TÁSSIA CAMARGO'], 85, (200, 0, 1208, 1058)),
    (['novela de', 'WALTER NEGRÃO'], 240, (500, 450, 1408, 760)),
    (['colaboração', 'ROSE CALZA', 'ANGELA CARNEIRO', 'MARGARETH BOURY'], 340, (480, 570, 1360, 1020)),
    (['JAYME PERIARD', 'ELIAS GLEIZER'], 365, (40, 140, 800, 420)),
    (['EDUARDO GALVÃO', 'LUCINHA LINS'], 450, (600, 680, 1408, 1040)),
    (['MARIA ESTELA'], 510, (300, 850, 1100, 1058)),
    (['ANA ROSA'], 555, (300, 850, 1100, 1058)),
    (['CRISTINA MULLINS'], 620, (150, 850, 1250, 1058)),
    (['BÁRBARA FÁZIO'], 720, (300, 800, 1200, 1058)),
    (['OTHON BASTOS'], 765, (300, 800, 1200, 1058)),
    (['JACYRA SAMPAIO', 'ANDRÉ VALLI'], 860, (60, 70, 900, 340)),
    (['LÉA CAMARGO', 'CINIRA CAMARGO'], 915, (60, 680, 1000, 1058)),
    (['PATRÍCIA PERRONE', 'FREDERICO MAYRINK'], 970, (60, 715, 1020, 1015)),
    (['DANTON MELLO', 'MARIA DUDA'], 1030, (60, 680, 1000, 1058)),
    (['GUGA COELHO', 'CASTRO GONZAGA'], 1100, (330, 715, 1195, 1015)),
    (['as crianças', 'PATRICK DE OLIVEIRA', 'FERNANDA NOBRE'], 1330, (200, 650, 1250, 1058)),
    (['apresentando', 'HELENA RANALDI', 'RITA GUEDES', 'JOÃO VITTI'], 1400, (60, 650, 1000, 1058)),
    (['SERGIO VIOTTI', 'como Dr. Gabriel'], 1460, (600, 700, 1408, 1058)),
    (['participação especial', 'MAURO MENDONÇA'], 1590, (60, 745, 1020, 1015)),
    (['participação especial', 'LOLITA RODRIGUES'], 1695, (480, 10, 1408, 300)),
    (['participação especial', 'YONÁ MAGALHÃES'], 1750, (480, 10, 1408, 300)),
    (['MARCOS PAULO', 'como Sérgio Santarém'], 1825, (480, 40, 1408, 345)),
    (['direção', 'REYNALDO BOURY', 'CLÁUDIO CAVALCANTI', 'CARLOS MANGA JUNIOR'], 1970, (40, 200, 1080, 760)),
    (['direção geral', 'REYNALDO BOURY'], 2176, (240, 330, 1165, 640)),
]
def branco(img, reg):
    b, g, r = [img[..., k].astype(np.int16) for k in range(3)]
    mn, mx = np.minimum(np.minimum(r, g), b), np.maximum(np.maximum(r, g), b)
    m = (mn > 175) & (mx - mn < 60)
    out = np.zeros_like(m); x0, y0, x1, y1 = reg; out[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    return out
res = []
for linhas, q, reg in CREDITOS:
    m = branco(cv2.imread(FR % q), reg)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    # linhas de texto: faixas de linhas da imagem com bastante branco
    prof = m.sum(1); on = prof > max(6, 0.04 * prof.max())
    faixas = []; y = 0
    while y < len(on):
        if on[y]:
            y0 = y
            while y < len(on) and on[y]: y += 1
            if y - y0 >= 6: faixas.append((y0, y))
        y += 1
    # junta faixas muito próximas (acentos) e fica com as n mais altas na ordem
    junt = []
    for f in faixas:
        if junt and f[0] - junt[-1][1] < 6: junt[-1] = (junt[-1][0], f[1])
        else: junt.append(f)
    caixas = []
    for (y0, y1) in junt:
        cols = np.nonzero(m[y0:y1].sum(0))[0]
        caixas.append([int(cols.min()), int(y0), int(cols.max() + 1), int(y1)])
    if len(caixas) != len(linhas): print('ATENÇÃO', linhas, 'achei', len(caixas), caixas)
    caixas = caixas[:len(linhas)]
    # quadros em que aparece: o branco dentro das caixas acima de 25% do quadro de referência
    cx0 = min(c[0] for c in caixas); cy0 = min(c[1] for c in caixas); cx1 = max(c[2] for c in caixas); cy1 = max(c[3] for c in caixas)
    ref = m[cy0:cy1, cx0:cx1].sum()
    def tem(n):
        if n < 1 or n > 2307: return False
        return branco(cv2.imread(FR % n), (cx0, cy0, cx1, cy1))[cy0:cy1, cx0:cx1].sum() > 0.25 * ref
    a = q
    while tem(a - 1): a -= 1
    b = q
    while tem(b + 1): b += 1
    res.append(dict(l=linhas, c=caixas, a=a, b=b))
    print(a, b, linhas, caixas)
# acertos à mão: letreiros no mesmo lugar em seguida (a medida automática junta os intervalos; a troca foi achada
# comparando a máscara do texto com a de cada letreiro), linhas com acento partidas e a linha fina de 'apresentando'
ACERTOS = {
    'JAYME PERIARD': dict(c1=[125, 414, 688, 482]),
    'MARIA ESTELA': dict(b=526), 'ANA ROSA': dict(a=527),
    'BÁRBARA FÁZIO': dict(b=738, c=[[363, 847, 1018, 931]]), 'OTHON BASTOS': dict(a=739),
    'LÉA CAMARGO': dict(b=940), 'PATRÍCIA PERRONE': dict(a=941, b=996), 'DANTON MELLO': dict(a=997),
    'apresentando': dict(c=[[126, 578, 566, 617], [126, 651, 809, 718], [126, 757, 642, 825], [125, 864, 581, 931]]),
    'LOLITA RODRIGUES': dict(b=1724, c=[[582, 67, 1295, 128], [557, 175, 1303, 243]]), 'YONÁ MAGALHÃES': dict(a=1725),
    'REYNALDO BOURY': dict(a2=1946),          # na direção, os dois nomes de baixo entram depois
}
for r in res:
    for chave, ac in ACERTOS.items():
        if chave in r['l'] and not (chave == 'REYNALDO BOURY' and r['l'][0] != 'direção'):
            if 'c1' in ac: r['c'][1] = ac['c1']
            for k in ('a', 'b', 'c', 'a2'):
                if k in ac: r[k] = ac[k]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'atlas', 'creditos.json')
json.dump(res, open(out, 'w'), ensure_ascii=False, separators=(',', ':'))
