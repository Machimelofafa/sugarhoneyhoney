# QA — Despedida de Solteiro

Data: 26 de outubro de 2026. Testes locais no navegador interno do Codex, baseado em Chrome 156, no Linux. As dimensões móveis abaixo são emulações, em pixels CSS; não são testes em aparelhos físicos.

## Resultado

O percurso é concluível. Na primeira partida, com a página normal e comandos de teclado, perdi os quatro corações no fogo e confirmei a tela de derrota e o retorno ao título. Na segunda, usei comandos reais de teclado enviados pelo navegador, com a telemetria de `?dbg=1` para acompanhar o tempo e o estado: atravessei o fogo, venci o vilão, passei pelo jacaré, subi a escada rolante e cheguei à vitória com três corações. Não alterei posição, vida ou estado nessa segunda partida. O combate foi conduzido por uma sequência de teclas guiada pela telemetria.

O teste determinístico existente, `jogo/ferramentas/teste-percurso.js`, foi repetido três vezes: três vitórias, com três, quatro e quatro corações ao fim do percurso. A [tela de vitória](vitoria.jpg) foi registrada em outra execução instrumentada. Após a animação, Enter retornou ao título.

## Problemas encontrados

### P2 — A tela do jogo fica pequena demais em celulares

1. Emule uma tela de 320 × 568, densidade de pixels 2 e ponteiro tátil, e inicie a partida.
2. A área jogável mede apenas **158 × 119 pixels CSS**, embora a tela tenha 320 pixels de largura. Em 667 × 375, densidade 2, ela também mede 158 × 119.
3. Isso prejudica a leitura dos personagens e do cenário, especialmente na horizontal. A escala inteira calculada em `jogo/src/js/85-saida.js:6` contribui para o resultado.

Evidências: [celular compacto](celular-320-dpr2.jpg) e [celular horizontal](celular-horizontal.jpg).

### P2 — Não há comando de pausa no modo tátil

1. Emule um ponteiro tátil e inicie a partida.
2. Os controles de teclado desaparecem e os botões disponíveis são direções, soco e pulo; não há pausa. Tocar no cenário durante a partida também não pausa: em um teste por passos, os quadros de jogo avançaram de 113 para 133 após o toque.

Referências: `jogo/src/shell-topo.html:80` e `jogo/src/js/90-entrada.js:18`. [Captura dos controles](celular-sem-pausa.jpg).

### P2 — Botões táteis não respondem à ativação pelo teclado

1. Emule um ponteiro tátil, inicie a partida e foque o botão acessível **Esquerda**.
2. Ative-o com Enter: após dez passos, a posição permaneceu em x=150 e a direção não ficou pressionada. O mesmo teste no botão **SOCO** manteve o herói em estado normal.
3. Os botões são expostos como botões na árvore de acessibilidade, mas suas ações são tratadas por eventos de ponteiro em `jogo/src/js/90-entrada.js:19`. As teclas de jogo continuam funcionando como atalhos independentes.

Além disso, a árvore expõe o canvas apenas como “Tela do jogo”, sem anunciar vida, vitória ou derrota. Isso foi observado na árvore de acessibilidade; falta avaliação com um leitor de tela real.

### P3 — Botão PULAR fica cortado em 320 pixels de largura

Na emulação de 320 × 568 e densidade 2, o botão PULAR ocupa de x=264 a x=328, ultrapassando em 8 pixels a largura visível de 320. A página usa `overflow: hidden`; a parte direita do botão fica cortada. [Captura](celular-320-dpr2.jpg). Ver `jogo/src/shell-topo.html:22` e as dimensões dos controles a partir da linha 80.

### P3 — Texto da pausa se sobrepõe à mensagem inicial

Inicie uma partida e aperte P assim que o controle estiver ativo, enquanto “SUBA ATÉ ELA” ainda estiver visível. “PAUSA” é desenhado sobre a mensagem. [Captura](pausa-sobreposicao.jpg). Ambas as camadas são desenhadas em `jogo/src/js/85-saida.js:83`.

### P3 — Repetição automática de P, C e M alterna opções novamente

O tratamento de `keydown` não ignora eventos com `repeat=true` para pausa, filtro e som. Em um teste com a repetição de P simulada, o jogo estava pausado, recebeu um `keydown` repetido e voltou a avançar: os quadros passaram de 19 para 29. O efeito de manter a tecla fisicamente pressionada ainda deve ser confirmado em um teclado real. Ver `jogo/src/js/90-entrada.js:6`.

### P3 — Instrução de reinício no celular menciona apenas Enter

Após a derrota, a tela diz “aperte ENTER para tentar de novo” mesmo quando só os controles táteis estão visíveis. Tocar no cenário efetivamente retorna ao título, mas essa alternativa não é informada. A tela de vitória também menciona apenas Enter. [Captura da derrota](celular-fim-instrucao.jpg). Ver `jogo/src/js/85-saida.js:86`.

## Verificações aprovadas

- Teclado: iniciar com Enter, andar com as setas, pular com Z e seta para cima, socar com X, pausar e retomar com P. Durante a pausa os quadros de jogo permaneceram em 9; após retomar chegaram a 19.
- Toque emulado: iniciar com PULAR, manter Esquerda para andar, acionar PULAR e SOCO individualmente.
- Fogo e água: cada um retirou um coração e trouxe o herói de volta ao píer. Jacaré deitado não causou dano no ponto testado; levantado causou dano.
- Pontos de retorno: testes instrumentados verificaram o patamar da escada, o piso após o vilão, a margem e o teto. Para provocar a queda, o herói foi posicionado no rio pelo modo de teste.
- Filtro de TV e som: os botões mudaram seus estados e as preferências permaneceram após recarregar. Um teste instrumentado observou oito osciladores com áudio ativo, nenhum adicional com som desligado e um adicional ao religá-lo e pular; o contexto de áudio estava `running`.
- Tela cheia: entrada e saída pelo botão foram confirmadas. A inspeção de avisos e erros do navegador nas sessões normais consultadas não retornou mensagens.
- A montagem em uma cópia temporária gerou um `index.html` idêntico ao existente; `node --check` passou. SHA-256 do arquivo verificado: `5d8b9fdb8ec3d0dd2f6908cc0346babf4d3cb068164f61584ba9f8a5cc59302b`.
- Em uma amostra de desktop, o contador da lógica avançou 180 quadros em 3,023 segundos, aproximadamente 59,5 atualizações por segundo. Isso não é uma medição de quadros renderizados nem um teste de desempenho em celular.

## Limites da avaliação

Não foram testados aparelhos físicos, toque simultâneo com dois dedos, Safari ou Firefox, reprodução audível em alto-falantes, um leitor de tela real nem a abertura por `file://`. A troca de aba não produziu evidência conclusiva da pausa automática no navegador interno. A referência visual da fase foi inspecionada, mas não foi feita uma comparação quadro a quadro suficiente para declarar fidelidade perfeita à abertura. O código do jogo não foi alterado durante este QA.
