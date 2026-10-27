# Jogo da Despedida

Recriação pessoal e nostálgica do videogame fictício da abertura da novela *Despedida de Solteiro* (1992).
O herói atravessa o píer, o fosso de fogo, a esteira, o vilão, o jacaré, a escada rolante, o alçapão e a grade
até o raio abrir um vão entre ele e a moça.

**Jogar:** https://machimelofafa.github.io/sugarhoneyhoney/

## Controles

| Tecla | Ação |
| --- | --- |
| ← → | andar |
| Z ou ↑ | pular |
| ↓ | abaixar |
| X | soco (e dar a mão no final) |
| C | chute |
| P | pausa |
| T | filtro de TV |
| M | som |
| Enter | pula a montagem |

No celular aparecem botões na tela.

## Como funciona

O jogo inteiro é um único arquivo, [`jogo/index.html`](jogo/index.html), sem servidor nem dependências (só a fonte
Jost, do Google Fonts). Os atores, o cenário, os planos fechados e a música saem da própria abertura e ficam
embutidos no arquivo.

- `jogo/src/` — casca HTML e módulos JavaScript (`NN-*.js`, concatenados em ordem).
- `jogo/atlas/`, `jogo/cenario.json` — assets extraídos do vídeo.
- `jogo/montar.py` — gera `jogo/index.html` a partir de tudo isso.
- `jogo/ferramentas/` — scripts de extração do vídeo e testes de percurso.
- `qa/` — relatório e capturas de teste.
- `referencia/` — quadros de referência da abertura.

Detalhes do percurso e dos módulos em [`jogo/LEIA-ME.md`](jogo/LEIA-ME.md).

## Rodar localmente

```bash
python3 -m http.server 8123 --directory jogo
```

Abra `http://localhost:8123/index.html`. Com `?dbg=1` o jogo expõe `window.__jogo` e não pausa ao perder o foco.

Para regerar o `index.html` depois de mexer em `jogo/src/`:

```bash
cd jogo && python3 montar.py
```

## Deploy

Todo push na `main` publica `jogo/index.html` no GitHub Pages pelo workflow
[`.github/workflows/pages.yml`](.github/workflows/pages.yml). Lembre de rodar `montar.py` e commitar o
`index.html` gerado antes do push.

## Aviso

Projeto de fã, sem fins lucrativos e sem qualquer ligação com os autores ou detentores dos direitos de
*Despedida de Solteiro*. Imagens e áudio vêm da abertura original e pertencem aos seus donos; estão aqui só por
nostalgia. Se você é o detentor dos direitos e quer que algo saia, abra uma issue.
