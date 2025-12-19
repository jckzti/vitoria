import pygame
import json
import random
from shapely.geometry import shape, Point, Polygon, MultiPolygon
import war_system
import economy_system
from power_country import generate_military_power
from utils.country_utils import CountryUtils
from utils.formatters import Formatters
from utils.ui import Button, ContextMenu
from game_time import GameTime

# Inicializa o Pygame
pygame.init()

# Configurações da janela
window_size = (1600, 900) # Adjusted to a more standard resolution, user can maximize
screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
pygame.display.set_caption("Jogo de Estratégia Geopolítica - Victoria Style")

# Cores
WHITE = (255, 255, 255)
LIGHT_SEA_BLUE = (173, 216, 230)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Dicionário para armazenar as coordenadas e propriedades dos países
country_shapes = {}
country_info = {}

# Fonte para textos
font = pygame.font.Font(None, 24)

# Estado do Jogo
player_country = None    # País com o qual o jogador está jogando
inspected_country = None # País atualmente clicado/focado pelo jogador
hovered_country = None   # País sob o cursor do mouse
guerras_ativas = []
battle_log = ""

# Sistema de Tempo
game_time = GameTime()

# UI Elements
btn_choose_country = Button(
    window_size[0] - 220, window_size[1] - 80, 200, 50,
    "Escolher País", font, bg_color=(0, 200, 0), text_color=WHITE
)

context_menu = ContextMenu(font)

# Time Controls UI
btn_pause = Button(window_size[0] - 100, 20, 80, 40, "PAUSE", font, bg_color=(200, 50, 50), text_color=WHITE)
time_buttons = []
speeds = [1, 3, 5, 10]
for i, speed in enumerate(speeds):
    btn = Button(window_size[0] - 320 + (i * 50), 20, 40, 40, f"{speed}x", font, bg_color=(100, 100, 100), text_color=WHITE)
    time_buttons.append({'btn': btn, 'value': i, 'action': 'speed'})


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
        properties['militar'] = generate_military_power(feature['properties'])
        properties['pib'] = properties.get('gdp_md', 0)
        properties['territorios'] = 1
        properties['pop_est'] = properties.get('pop_est', 0) # Ensure population is set

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
        # Encontra a primeira forma para pegar a cor atualizada nas propriedades
        first_shape_points = shapes[0][0]
        if tuple(first_shape_points) in country_info:
            new_color = country_info[tuple(first_shape_points)]["color"]
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


def show_time_controls():
    # Update buttons color based on state
    if game_time.paused:
        btn_pause.text = "PLAY"
        btn_pause.bg_color = (0, 200, 0) # Green for Play
    else:
        btn_pause.text = "PAUSE"
        btn_pause.bg_color = (200, 50, 50) # Red for Pause
    
    btn_pause.draw(screen)
        
    for item in time_buttons:
        if item['action'] == 'speed':
            # Highlight current speed
            if item['value'] == game_time.current_speed_index:
                item['btn'].bg_color = (50, 150, 255) # Blue active
            else:
                item['btn'].bg_color = (100, 100, 100) # Gray inactive
                
        item['btn'].draw(screen)

    # Show Date
    date_surf = font.render(f"DATA: {game_time.get_date_string()}", True, BLACK)
    # Position to the left of speed buttons
    bg_rect = date_surf.get_rect(topright=(window_size[0] - 340, 25))
    bg_rect.inflate_ip(20, 10) # Add padding
    pygame.draw.rect(screen, (240, 240, 240), bg_rect)
    pygame.draw.rect(screen, BLACK, bg_rect, 1)
    screen.blit(date_surf, (bg_rect.x + 10, bg_rect.y + 5))

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
clock = pygame.time.Clock()

while running:
    # Delta time in seconds
    dt = clock.tick(60) / 1000.0

    # Update Game Logic
    new_day = game_time.update(dt)
    
    if new_day:
        # Process economy and military growth
        economy_system.processar_crescimento_diario(country_info)

        # Process active wars
        for guerra in guerras_ativas:
            if guerra["em_andamento"]:
                if guerra["data_inicio"] is None:
                    guerra["data_inicio"] = game_time.get_date_string()
                
                resultado, fim_guerra, change_color = war_system.processar_dia_guerra(guerra, country_info)
                
                if resultado:
                    # Log update
                    battle_log = f"[{game_time.get_date_string()}] {resultado}"
                    if change_color:
                        refresh_country_colors()

    # Draw
    screen.fill(LIGHT_SEA_BLUE)
    draw_countries(screen)
    
    show_info()
    show_hovered_info()
    show_battle_log(battle_log)
    show_time_controls()
    
    # Desenha botão de escolher se houver um país inspecionado e ele não for o atual
    if inspected_country and inspected_country != player_country:
        # Re-update button position if window size changed (optional, keeping simple for now)
        btn_choose_country.rect.topleft = (window_size[0] - 220, window_size[1] - 80)
        btn_choose_country.draw(screen)

    # Desenha menu de contexto
    context_menu.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.VIDEORESIZE:
             window_size = event.size
             screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
             # Update UI positions relative to screen
             btn_choose_country.rect.topleft = (window_size[0] - 220, window_size[1] - 80)
             btn_pause.rect.topleft = (window_size[0] - 100, 20)
             for i, item in enumerate(time_buttons):
                 item['btn'].rect.topleft = (window_size[0] - 320 + (i * 50), 20)
        
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

                # 2. Check UI Interaction (Time Controls)
                elif btn_pause.is_clicked(event):
                    game_time.toggle_pause()
                else:
                    speed_clicked = False
                    for item in time_buttons:
                        if item['btn'].is_clicked(event):
                            game_time.set_speed(item['value'])
                            speed_clicked = True
                            break
                    
                    if not speed_clicked:
                        # 3. Check UI Interaction (Choose Button)
                        if inspected_country and inspected_country != player_country and btn_choose_country.is_clicked(event):
                            player_country = inspected_country
                            battle_log = f"Você escolheu jogar com: {player_country['name']}"
                            inspected_country = None # Limpa a inspeção após escolher

                        # 4. Check Map Interaction (Select/Inspect Country)
                        else:
                            # Se clicou fora do menu, ele já fecha (no handle_click)
                            # Verifica se clicou num país
                            country_properties = get_country_info_at(*event.pos)
                            if country_properties:
                                inspected_country = country_properties
                                # Se clicar num país, fecha menu anterior se existir
                                context_menu.hide()

            elif event.button == 3:  # Right Click
                if player_country:
                    country_properties = get_country_info_at(*event.pos)
                    if country_properties and country_properties != player_country:
                        # Define este país como o inspecionado também
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
        
        # Key Handling (Atalhos de teclado opcionais)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_time.toggle_pause()
            elif event.key == pygame.K_1:
                game_time.set_speed(0) # 1x
            elif event.key == pygame.K_2:
                game_time.set_speed(1) # 3x
            elif event.key == pygame.K_3:
                game_time.set_speed(2) # 5x
            elif event.key == pygame.K_4:
                game_time.set_speed(3) # 10x

    pygame.display.flip()

pygame.quit()
