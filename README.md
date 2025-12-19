# Jogo de Estratégia Geopolítica

Um jogo de estratégia em tempo real desenvolvido em Python onde você controla um país, gerencia recursos e compete pela dominação global através de diplomacia e guerra.

## 📋 Sobre o Projeto

Este projeto é um simulador geopolítico que utiliza dados reais (GeoJSON) para renderizar o mapa do mundo. O jogo calcula o poder militar e econômico dos países com base em dados como PIB e população, permitindo conflitos e anexação de territórios.

## 🚀 Funcionalidades Atuais

- **Renderização de Mapa**: Mapa-múndi interativo gerado a partir de arquivos GeoJSON.
- **Sistema de Dados**: Cálculo automático de poder militar baseado em PIB e População.
- **Interação**: Seleção de países, visualização de estatísticas (PIB, População, Poder Militar).
- **Sistema de Guerra**:
  - Declaração de guerra entre países vizinhos/selecionados.
  - Combate por turnos com logs de batalha.
  - Anexação de território e economia após vitória.
  - Sistema de rendição e recuo.

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3
- **Motor Gráfico**: Pygame
- **Processamento de Geometria**: Shapely
- **Dados**: GeoJSON

## 📦 Instalação

1. Certifique-se de ter o Python instalado.
2. Instale as dependências necessárias:

```bash
pip install pygame shapely
```

## 🎮 Como Jogar

1. Execute o arquivo principal:
   ```bash
   python map.py
   ```

2. **Controles**:
   - **Botão Esquerdo do Mouse**:
    - Clique em um país para inspecioná-lo.
    - Se ainda não escolheu um país, clique no botão "Escolher País" no canto inferior direito para jogar com ele.
  - **Botão Direito do Mouse**: Abre o menu de ações ao clicar em um país inimigo (apenas se já estiver jogando com um país).
  - **Mouse Sobre**: Mostra informações rápidas do país sob o cursor.
  - **Tecla 'Z'**: Avançar turno das guerras em andamento.

## 📂 Estrutura do Projeto

- `map.py`: Arquivo principal contendo o loop do jogo e renderização.
- `war_system.py`: Lógica do sistema de combate e resolução de turnos.
- `power_country.py`: Algoritmos para cálculo de força militar.
- `custom.geo.json`: Base de dados geográfica e estatística dos países.
- `utils/`: Funções auxiliares de formatação e manipulação de dados.
