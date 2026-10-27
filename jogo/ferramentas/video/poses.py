"""Poses escolhidas para o atlas. (id, plano_ator, quadro, direção_para_onde_olha[, opções])
direção: +1 olha para a direita no recorte, -1 para a esquerda.
Z = ampliação do ator no plano em relação ao quadro geral (herói em pé ~283 px, vilão ~265 px, moça ~215 px).
A luta do herói (fight_hero) era 2,2 e deixava a guarda ~10% mais alta que o herói em pé; 2,55 põe a guarda agachada abaixo dele."""
PX = 3.45   # px do quadro geral por px do atlas (meio bloco do mosaico)

Z = {
    ('ur_hero', 'hero'): 1.75, ('vil_hero', 'hero'): 2.17, ('fight_hero', 'hero'): 2.55,
    ('scaf_hero', 'hero'): 2.6, ('croc_hero', 'hero'): 2.5, ('fire_hero', 'hero'): 2.6, ('water_hero', 'hero'): 2.2,
    ('fightk_hero', 'hero'): 2.55, ('fight_vil', 'vil'): 2.85, ('vil_vil', 'vil'): 2.2,
    ('dueto_duo', 'duo'): 2.65,
    ('girlA_girl', 'girl'): 3.56, ('girlB_girl', 'girl'): 3.56, ('girlC_girl', 'girl'): 3.45,
}
UR = {'limpa': True, 'abre': 21, 'regrow': 5, 'pale': True}

def ciclo(prefixo, clip, quadros, face, opt=None):
    return [(f'{prefixo}.{i:02d}', clip, q, face, opt or {}) for i, q in enumerate(quadros)]

POSES = {
    'hero': (
        # o vídeo só alterna pernas abertas / fechadas, segurando cada uma ~6 quadros; 1013, 1016, 1026 e 1028 perderam a cabeça
        ciclo('hero.walk', 'ur_hero', [1001, 1007, 1018, 1022, 1031, 1037], -1, UR) +
        [('hero.idle.0', 'vil_hero', 413, 1, {'limpa': True, 'abre': 21, 'regrow': 6}),
         ('hero.jump.0', 'fire_hero', 193, -1), ('hero.jump.1', 'fire_hero', 196, -1),
         ('hero.fall.0', 'fire_hero', 204, -1), ('hero.fall.1', 'fire_hero', 206, -1),
         ('hero.swim.0', 'water_hero', 1090, 1), ('hero.swim.1', 'water_hero', 1093, 1),
         ('hero.swim.2', 'water_hero', 1096, 1), ('hero.swim.3', 'water_hero', 1099, 1),
         ('hero.guard.0', 'fight_hero', 490, 1), ('hero.guard.1', 'fight_hero', 494, 1), ('hero.guard.2', 'fight_hero', 498, 1),
         ('hero.punch.0', 'fight_hero', 507, 1), ('hero.punch.1', 'fight_hero', 512, 1), ('hero.punch.2', 'fight_hero', 522, 1),
         ('hero.hurt.0', 'fight_hero', 557, 1), ('hero.hurt.1', 'fight_hero', 560, 1),
         # esquiva na luta (o herói se abaixa sob o chute alto), chute alto e joelhada do contra-ataque (recortes de chute.py)
         ('hero.duck.0', 'fight_hero', 503, 1), ('hero.duck.1', 'fight_hero', 536, 1),
         ('hero.kick.0', 'fightk_hero', 610, 1), ('hero.kick.1', 'fightk_hero', 614, 1), ('hero.kick.2', 'fightk_hero', 614, 1),
         ('hero.knee.0', 'fightk_hero', 624, 1), ('hero.knee.1', 'fightk_hero', 628, 1),
         # agachado diante da grade e passando por baixo dela
         ('hero.crouch.0', 'scaf_hero', 1672, -1), ('hero.crouch.1', 'scaf_hero', 1678, -1),
         ('hero.crawl.0', 'scaf_hero', 1674, -1), ('hero.crawl.1', 'scaf_hero', 1680, -1),
         ('hero.crawl.2', 'scaf_hero', 1686, -1), ('hero.crawl.3', 'scaf_hero', 1690, -1),
         ('hero.down.0', 'fight_hero', 634, 1), ('hero.down.1', 'fight_hero', 638, 1),
         ('hero.climb.0', 'scaf_hero', 1490, -1), ('hero.climb.1', 'scaf_hero', 1500, -1),
         ('hero.climb.2', 'scaf_hero', 1510, -1), ('hero.climb.3', 'scaf_hero', 1520, -1)]),
    'vil': (
        [('vil.guard.0', 'fight_vil', 508, -1), ('vil.guard.1', 'fight_vil', 511, -1), ('vil.guard.2', 'fight_vil', 514, -1),
         ('vil.walk.0', 'fight_vil', 557, -1), ('vil.walk.1', 'fight_vil', 561, -1), ('vil.walk.2', 'fight_vil', 564, -1),
         ('vil.punch.0', 'fight_vil', 546, -1),
         ('vil.kick.0', 'fight_vil', 498, -1),
         ('vil.hurt.0', 'fight_vil', 629, -1), ('vil.hurt.1', 'fight_vil', 631, -1),
         ('vil.down.0', 'fight_vil', 634, -1), ('vil.down.1', 'fight_vil', 638, -1)]),
    'duo': ciclo('duo', 'dueto_duo', list(range(1990, 2129, 2)), 1, {'limpa': True, 'abre': 13, 'regrow': 4, 'origin': (333, 750)}),
    'girl': (
        ciclo('girl.idle', 'girlA_girl', [426, 432, 438, 444, 450, 456, 462, 468, 474, 480], 1) +
        ciclo('girl.cheer', 'girlC_girl', [1860, 1866, 1872, 1880, 1884, 1888], 1) +
        # andando no alto (plano 1381-1486) e na beira do vão: braços abertos, perde o equilíbrio, o raio
        ciclo('girl.walk', 'girlB_girl', [1412, 1428, 1436, 1452, 1460, 1468], -1) +
        ciclo('girl.edge', 'girlC_girl', [1784, 1788, 1792, 1796, 1824, 1828], 1) +
        ciclo('girl.fright', 'girlC_girl', [1800, 1804], 1)),
}
