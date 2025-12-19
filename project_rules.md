# Regras e Diretrizes do Projeto

Este documento define os padrões, convenções e arquitetura para o desenvolvimento contínuo do Jogo de Estratégia Geopolítica.

## 🎯 Objetivos do Projeto

Criar um simulador geopolítico profundo e realista, mantendo uma interface acessível. O foco deve ser na lógica de estratégia (diplomacia, economia, guerra) suportada por uma visualização clara em mapa.

## 🏗️ Arquitetura

O projeto segue uma estrutura modular para separar a lógica do jogo da renderização visual.

### Módulos Principais
1.  **Core (`map.py`)**:
    *   Responsável pelo ciclo de vida do jogo (Game Loop).
    *   Gerenciamento de eventos (Input do usuário).
    *   Renderização via Pygame.
    *   *Nota*: Futuramente, a lógica de estado do jogo deve ser desacoplada deste arquivo para um `GameManager` ou similar.

2.  **Lógica de Combate (`war_system.py`)**:
    *   Gerencia estados de guerra.
    *   Cálculo de danos, perdas e transferências de recursos.
    *   Deve ser puramente lógico (sem dependências de Pygame).

3.  **Lógica de Entidades (`power_country.py`)**:
    *   Definição e cálculo de atributos dos países.
    *   Balanceamento de jogo.

4.  **Dados (`custom.geo.json`)**:
    *   Fonte da verdade para fronteiras e dados iniciais.
    *   *Regra*: Não modificar a estrutura do GeoJSON original, apenas carregar e manipular em memória, a menos que seja para salvar o estado do jogo.

## 📝 Convenções de Código

### Linguagem
*   **Código (Variáveis, Funções, Classes)**: Inglês (Recomendado para padronização futura) ou Português (Mantendo o padrão atual). *Decisão atual: Manter consistência com o código existente (misto, mas tendendo ao inglês para estrutura e português para strings de UI).*
*   **Comentários e Strings de UI**: Português.

### Estilo (Python)
*   Seguir **PEP 8** para formatação.
*   **Nomes de Variáveis**: `snake_case` (ex: `selected_country`, `military_power`).
*   **Nomes de Classes**: `PascalCase` (ex: `CountryUtils`, `WarSystem`).
*   **Constantes**: `UPPER_CASE` (ex: `WINDOW_SIZE`, `WHITE`).

### Tratamento de Erros
*   Evitar "falhas silenciosas". Logs de erro devem ser claros.
*   Validações de nulos (`None`) devem ser feitas antes de acessar propriedades de países selecionados.

## 🚀 Fluxo de Desenvolvimento (Melhorias Futuras)

Ao trabalhar em melhorias ("refactoring"), seguir estas prioridades:

1.  **Desacoplamento**: Retirar lógica de negócio de dentro do loop de renderização (`map.py`).
2.  **Performance**: Otimizar o desenho dos polígonos (cache de superfícies se necessário), pois renderizar centenas de polígonos a cada frame pode ser pesado.
3.  **UI/UX**: Melhorar a interface de usuário (menus, textos) para não depender apenas de texto renderizado diretamente na tela.
4.  **Zoom/Pan**: Implementar câmera móvel, já que o mapa mundo é grande.

## 🤖 Instruções para IA

*   Ao criar novas funcionalidades, verifique se já existem funções auxiliares em `utils/`.
*   Mantenha o `war_system.py` sem dependências visuais. Ele deve retornar estados ou logs que o `map.py` decide como mostrar.
*   Sempre atualize o `README.md` se adicionar novas dependências ou mudar os controles.
