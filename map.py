import pygame
import json
import random
import os
from shapely.geometry import shape, Point, Polygon, MultiPolygon
import war_system
import economy_system
from power_country import generate_military_power
from utils.country_utils import CountryUtils
from utils.formatters import Formatters
from utils.ui import Button, ContextMenu
from game_time import GameTime
from resource_system import ResourceSystem
from growth_system import GrowthSystem

# Inicializa o Pygame
pygame.init()

# Configurações da janela
window_size = (1600, 900)  # Adjusted to a more standard resolution, user can maximize
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
flag_cache = {}

# Fonte para textos
font = pygame.font.Font(None, 24)

# Estado do Jogo
player_country = None  # País com o qual o jogador está jogando
inspected_country = None  # País atualmente clicado/focado pelo jogador
hovered_country = None  # País sob o cursor do mouse
guerras_ativas = []
battle_log = ""

# Camera Control
camera_offset_x = 0
camera_offset_y = 0
zoom_scale = 1.0
min_zoom = 0.5
max_zoom = 10.0
dragging = False
last_mouse_pos = (0, 0)

# Sistema de Tempo
game_time = GameTime()

# Sistema de Recursos
resource_system = ResourceSystem()

# Sistema de Crescimento (PIB e População)
growth_system = GrowthSystem()

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
    btn = Button(window_size[0] - 320 + (i * 50), 20, 40, 40, f"{speed}x", font, bg_color=(100, 100, 100),
                 text_color=WHITE)
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
        properties['pop_est'] = properties.get('pop_est', 0)  # Ensure population is set

        # Carrega recursos do país
        properties['resources'] = resource_system.get_country_resources(country_name)

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
                # These are now "World Coordinates" (Base scale)
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


def get_flag_image(properties):
    if not properties:
        return None

    # Tenta vários códigos ISO possíveis
    candidates = []

    # 1. iso_a2 (padrão)
    if 'iso_a2' in properties and properties['iso_a2'] != -99 and properties['iso_a2'] != "-99":
        candidates.append(str(properties['iso_a2']).lower())

    # 2. iso_a2_eh (fallback comum)
    if 'iso_a2_eh' in properties and properties['iso_a2_eh'] != -99 and properties['iso_a2_eh'] != "-99":
        candidates.append(str(properties['iso_a2_eh']).lower())

    # 3. wb_a2 (World Bank)
    if 'wb_a2' in properties and properties['wb_a2'] != -99 and properties['wb_a2'] != "-99":
        candidates.append(str(properties['wb_a2']).lower())

    for iso_code in candidates:
        if iso_code in flag_cache:
            return flag_cache[iso_code]

        path = os.path.join("assets", "flags", f"{iso_code}.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                # Redimensiona para algo razoável (largura 50)
                w = 50
                ratio = img.get_height() / img.get_width()
                h = int(w * ratio)
                img = pygame.transform.smoothscale(img, (w, h))
                flag_cache[iso_code] = img
                return img
            except Exception as e:
                # Se falhar o smoothscale, tenta scale normal
                try:
                    img = pygame.image.load(path)
                    w = 50
                    ratio = img.get_height() / img.get_width()
                    h = int(w * ratio)
                    img = pygame.transform.scale(img, (w, h))
                    flag_cache[iso_code] = img
                    return img
                except:
                    print(f"DEBUG: Error loading flag {path}: {e}")
                    continue

    return None


# Coordinate Transformations
def world_to_screen(x, y):
    return (int(x * zoom_scale + camera_offset_x), int(y * zoom_scale + camera_offset_y))


def screen_to_world(x, y):
    return ((x - camera_offset_x) / zoom_scale, (y - camera_offset_y) / zoom_scale)


# Função para desenhar os países no Pygame
def draw_countries(screen):
    for country_name, shapes in country_shapes.items():
        for shape_data, color in shapes:
            # Transform points to screen space
            transformed_points = [world_to_screen(p[0], p[1]) for p in shape_data]

            # Simple culling: check if any point is within screen bounds + padding
            # This is a very rough optimization
            xs = [p[0] for p in transformed_points]
            ys = [p[1] for p in transformed_points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            if max_x < 0 or min_x > window_size[0] or max_y < 0 or min_y > window_size[1]:
                continue

            pygame.draw.polygon(screen, color, transformed_points, 0)  # Preenche o polígono com a cor


# Função para obter as propriedades do país sob o mouse
def get_country_info_at(screen_x, screen_y):
    # Convert screen click to world coordinates
    world_x, world_y = screen_to_world(screen_x, screen_y)
    point = Point(world_x, world_y)

    for shape_data, properties in country_info.items():
        # Polygon creation is heavy, but Shapely is reasonably fast for point-in-polygon
        # Optimization: Check bounding box of shape_data first if needed
        if Polygon(shape_data).contains(point):
            return properties
    return None


def show_time_controls():
    # Update buttons color based on state
    if game_time.paused:
        btn_pause.text = "PLAY"
        btn_pause.bg_color = (0, 200, 0)  # Green for Play
    else:
        btn_pause.text = "PAUSE"
        btn_pause.bg_color = (200, 50, 50)  # Red for Pause

    btn_pause.draw(screen)

    for item in time_buttons:
        if item['action'] == 'speed':
            # Highlight current speed
            if item['value'] == game_time.current_speed_index:
                item['btn'].bg_color = (50, 150, 255)  # Blue active
            else:
                item['btn'].bg_color = (100, 100, 100)  # Gray inactive

        item['btn'].draw(screen)

    # Show Date
    date_surf = font.render(f"DATA: {game_time.get_date_string()}", True, BLACK)
    # Position to the left of speed buttons
    bg_rect = date_surf.get_rect(topright=(window_size[0] - 340, 25))
    bg_rect.inflate_ip(20, 10)  # Add padding
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

        flag = get_flag_image(player_country)

        # Prepara texto de recursos
        res_list = player_country.get('resources', [])
        res_icons = " ".join([resource_system.get_resource_icon(r) for r in res_list])

        info_text = [
            f"JOGANDO COM: {player_country['name'].upper()}",
            f"PIB: {pib} {pib_unity}",
            f"Militar: {military_power}",
            f"Territórios: {player_country['territorios']}",
            f"População: {population}",
            f"Recursos: {res_icons if res_icons else 'Nenhum'}"
        ]

        # Desenha um fundo semi-transparente ou sólido para destacar
        bg_rect = pygame.Rect(10, 10, 300, 20 + len(info_text) * 20)
        # Aumenta altura se tiver bandeira e ela for maior que o espaço de texto (raro, mas bom garantir)
        if flag:
            # Espaço extra para a bandeira no topo se quiser, ou ao lado.
            # Vamos colocar a bandeira no canto superior direito do box.
            pass

        pygame.draw.rect(screen, (240, 240, 240), bg_rect)
        pygame.draw.rect(screen, BLACK, bg_rect, 2)

        if flag:
            screen.blit(flag, (bg_rect.right - flag.get_width() - 10, bg_rect.top + 10))

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

        flag = get_flag_image(target)

        header = "INSPECIONANDO:" if target == inspected_country else "HOVER:"

        # Prepara texto de recursos
        res_list = target.get('resources', [])
        res_icons = " ".join([resource_system.get_resource_icon(r) for r in res_list])

        info_text = [
            f"{header} {target['name_pt'] if 'name_pt' in target else target['name']}",
            f"PIB: {pib} {pib_unity}",
            f"Militar: {military_power}",
            f"Territórios: {target['territorios']}",
            f"População: {population}",
            f"Recursos: {res_icons if res_icons else 'Nenhum'}"
        ]

        # Posição inferior esquerda
        start_y = window_size[1] - 150
        bg_rect = pygame.Rect(10, start_y - 10, 300, 20 + len(info_text) * 20)
        pygame.draw.rect(screen, (240, 240, 240), bg_rect)
        pygame.draw.rect(screen, BLACK, bg_rect, 2)

        if flag:
            # Desenha bandeira no topo direito do box
            screen.blit(flag, (bg_rect.right - flag.get_width() - 10, bg_rect.top + 10))

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
        
        # Process GDP and Population growth (dynamic)
        growth_system.process_all_countries(country_info)

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

        elif event.type == pygame.MOUSEWHEEL:
            # Zoom logic
            old_zoom = zoom_scale
            if event.y > 0:
                zoom_scale *= 1.1
            elif event.y < 0:
                zoom_scale /= 1.1

            # Clamp zoom
            zoom_scale = max(min_zoom, min(zoom_scale, max_zoom))

            # Zoom towards mouse cursor
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Adjust offset so the point under mouse stays stationary
            # formula: new_offset = mouse - (mouse - old_offset) * (new_zoom / old_zoom)
            camera_offset_x = mouse_x - (mouse_x - camera_offset_x) * (zoom_scale / old_zoom)
            camera_offset_y = mouse_y - (mouse_y - camera_offset_y) * (zoom_scale / old_zoom)

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
                        if inspected_country and inspected_country != player_country and btn_choose_country.is_clicked(
                                event):
                            player_country = inspected_country
                            battle_log = f"Você escolheu jogar com: {player_country['name']}"
                            inspected_country = None  # Limpa a inspeção após escolher

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

            elif event.button == 2:  # Middle click to start drag
                dragging = True
                last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                dragging = False

        # Mouse Motion (Hover & Drag)
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mx, my = event.pos
                dx = mx - last_mouse_pos[0]
                dy = my - last_mouse_pos[1]
                camera_offset_x += dx
                camera_offset_y += dy
                last_mouse_pos = event.pos
            else:
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
                game_time.set_speed(0)  # 1x
            elif event.key == pygame.K_2:
                game_time.set_speed(1)  # 3x
            elif event.key == pygame.K_3:
                game_time.set_speed(2)  # 5x
            elif event.key == pygame.K_4:
                game_time.set_speed(3)  # 10x

    pygame.display.flip()

pygame.quit()
