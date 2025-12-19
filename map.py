import pygame
import json
import random
from shapely.geometry import shape, Point, Polygon, MultiPolygon
import war_system
from power_country import generate_military_power
from utils.country_utils import CountryUtils
from utils.formatters import Formatters
from utils.ui import Button, ContextMenu

# Inicializa o Pygame
pygame.init()

# Configurações da janela
window_size = (2980, 1200)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Jogo de Estratégia Geopolítica")

# Cores
WHITE = (255, 255, 255)
LIGHT_SEA_BLUE = (173, 216, 230)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Dicionário para armazenar as coordenadas e propriedades dos países
country_shapes = {}
country_info = {}

# Fonte para textos
font = pygame.font.Font(None, 24)

# Estado do Jogo
player_country = None    # País com o qual o jogador está jogando
inspected_country = None # País atualmente clicado/focado pelo jogador
hovered_country = None   # País sob o cursor do mouse

# UI Elements
btn_choose_country = Button(
    window_size[0] - 220, window_size[1] - 80, 200, 50,
    "Escolher País", font, bg_color=(0, 200, 0), text_color=WHITE
)

context_menu = ContextMenu(font)

# Função para gerar uma cor aleatória
def generate_random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


# Função para carregar o JSON e preparar os dados
def load_geojson(filename):
    with open(filename, encoding='utf-8') as f:
        data = json.load(f)

    for feature in data['features']:
        country_name = feature['properties']['name']
        properties = feature['properties']

        # Dados geopolíticos iniciais (poder militar, PIB, etc.)
        # properties['militar'] = random.randint(50, 100)
        properties['militar'] = generate_military_power(feature['properties'])
        # properties['pib'] = random.uniform(0.5, 2.0)
        properties['pib'] = properties['gdp_md']
        properties['territorios'] = 1


        # Gera uma cor aleatória para o país
        color = generate_random_color()
        properties['color'] = color

        geom = shape(feature['geometry'])
        if isinstance(geom, Polygon):
            polygons = [geom]
        elif isinstance(geom, MultiPolygon):
            polygons = list(geom.geoms)
        else:
            continue

        for polygon in polygons:
            points = []
            for coord in polygon.exterior.coords:
                x, y = coord
                # Ajuste de escala e translação
                x = int((x + 180) * (window_size[0] / 360))
                y = int((90 - y) * (window_size[1] / 180))
                points.append((x, y))
            if country_name not in country_shapes:
                country_shapes[country_name] = []
            country_shapes[country_name].append((points, color))
            country_info[tuple(points)] = properties


def refresh_country_colors():
    for country_name, shapes in country_shapes.items():
        new_color = country_info[tuple(shapes[0][0])]["color"]  # Pega a cor atual do país
        country_shapes[country_name] = [(points, new_color) for points, _ in shapes]


# Função para desenhar os países no Pygame
def draw_countries(screen):
    for country_name, shapes in country_shapes.items():
        for shape_data, color in shapes:
            pygame.draw.polygon(screen, color, shape_data, 0)  # Preenche o polígono com a cor


# Função para obter as propriedades do país sob o mouse
def get_country_info_at(x, y):
    point = Point(x, y)
    for shape_data, properties in country_info.items():
        if Polygon(shape_data).contains(point):
            return properties
    return None


def show_info():
    """Mostra as informações do país que o jogador controla."""
    if player_country:
        population = CountryUtils.get_pop(country=player_country)
        pib = CountryUtils.get_pib(country=player_country)
        pib_unity = Formatters().get_pib_unity(pib)
        military_power = Formatters().format_number(str(player_country['militar']))

        info_text = [
            f"JOGANDO COM: {player_country['name'].upper()}",
            f"PIB: {pib} {pib_unity}",
            f"Militar: {military_power}",
            f"Territórios: {player_country['territorios']}",
            f"População: {population}"
        ]
        
        # Desenha um fundo semi-transparente ou sólido para destacar
        bg_rect = pygame.Rect(10, 10, 300, 20 + len(info_text) * 20)
        pygame.draw.rect(screen, (240, 240, 240), bg_rect)
        pygame.draw.rect(screen, BLACK, bg_rect, 2)

        for i, line in enumerate(info_text):
            text = font.render(line, True, BLACK)
            screen.blit(text, (20, 20 + i * 20))

def show_hovered_info():
    """Mostra as informações do país sob o mouse ou inspecionado."""
    # Prioridade: País inspecionado (clicado) > País sob o mouse
    target = inspected_country if inspected_country else hovered_country
    
    if target:
        population = CountryUtils.get_pop(country=target)
        pib = CountryUtils.get_pib(country=target)
        pib_unity = Formatters().get_pib_unity(pib)
        military_power = Formatters().format_number(str(target['militar']))

        header = "INSPECIONANDO:" if target == inspected_country else "HOVER:"
        
        info_text = [
            f"{header} {target['name_pt'] if 'name_pt' in target else target['name']}",
            f"PIB: {pib} {pib_unity}",
            f"Militar: {military_power}",
            f"Territórios: {target['territorios']}",
            f"População: {population}",
        ]
        
        # Posição inferior esquerda
        start_y = window_size[1] - 150
        bg_rect = pygame.Rect(10, start_y - 10, 300, 20 + len(info_text) * 20)
        pygame.draw.rect(screen, (240, 240, 240), bg_rect)
        pygame.draw.rect(screen, BLACK, bg_rect, 2)

        for i, line in enumerate(info_text):
            text = font.render(line, True, BLACK)
            screen.blit(text, (20, start_y + i * 20))


def show_battle_log(log):
    """Mostra o resultado das batalhas."""
    if not log:
        return
    battle_text = font.render(log, True, BLACK)
    # Centralizado na parte inferior
    text_rect = battle_text.get_rect(center=(window_size[0] // 2, window_size[1] - 40))
    
    # Fundo para leitura
    bg_rect = text_rect.inflate(20, 10)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect)
    pygame.draw.rect(screen, BLACK, bg_rect, 1)
    
    screen.blit(battle_text, text_rect)


# Carrega o GeoJSON
load_geojson('custom.geo.json')

# Loop principal do jogo
running = True
battle_log = ""
guerras_ativas = []

while running:
    screen.fill(LIGHT_SEA_BLUE)
    draw_countries(screen)
    
    show_info()
    show_hovered_info()
    show_battle_log(battle_log)
    
    # Desenha botão de escolher se houver um país inspecionado e ele não for o atual
    if inspected_country and inspected_country != player_country:
        btn_choose_country.draw(screen)

    # Desenha menu de contexto
    context_menu.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Click Handling
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left Click
                # 1. Check UI Interaction (Context Menu)
                action = context_menu.handle_click(event)
                if action == 'attack':
                    if player_country and inspected_country and player_country != inspected_country:
                         # Inicia a guerra
                        nova_guerra = war_system.iniciar_guerra(player_country, inspected_country)
                        guerras_ativas.append(nova_guerra)
                        battle_log = f"Guerra iniciada: {player_country['name']} vs {inspected_country['name']}"

                # 2. Check UI Interaction (Choose Button)
                elif inspected_country and inspected_country != player_country and btn_choose_country.is_clicked(event):
                    player_country = inspected_country
                    battle_log = f"Você escolheu jogar com: {player_country['name']}"
                    inspected_country = None # Limpa a inspeção após escolher

                # 3. Check Map Interaction (Select/Inspect Country)
                else:
                    # Se clicou fora do menu, ele já fecha (no handle_click)
                    # Verifica se clicou num país
                    country_properties = get_country_info_at(*event.pos)
                    if country_properties:
                        inspected_country = country_properties
                        # Se clicar num país, fecha menu anterior se existir (já feito pelo handle_click logicamente, mas garantindo)
                        context_menu.hide()

            elif event.button == 3:  # Right Click
                if player_country:
                    country_properties = get_country_info_at(*event.pos)
                    if country_properties and country_properties != player_country:
                        # Define este país como o inspecionado também, para facilitar
                        inspected_country = country_properties
                        
                        # Abre menu de contexto
                        context_menu.show(event.pos, [
                            {'text': 'Atacar', 'action': 'attack'}
                        ])

        # Mouse Motion (Hover)
        elif event.type == pygame.MOUSEMOTION:
            country_properties = get_country_info_at(*event.pos)
            if country_properties:
                hovered_country = country_properties
            else:
                hovered_country = None
        
        # Key Handling (Apenas atalhos globais úteis, sem ações de jogo escondidas)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                # Avança as guerras existentes (Manter este por enquanto, talvez adicionar botão depois)
                for guerra in guerras_ativas:
                    if guerra["em_andamento"]:
                        resultado, change_color = war_system.calcular_turno_guerra(guerra, country_info)
                        if resultado:
                            battle_log = resultado
                            if change_color:
                                refresh_country_colors()

    pygame.display.flip()

pygame.quit()
