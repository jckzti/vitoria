import pygame
import json
import random
from shapely.geometry import shape, Point, Polygon, MultiPolygon
import war_system
from power_country import generate_military_power
from utils.country_utils import CountryUtils
from utils.formatters import Formatters

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

# País selecionado pelo jogador
selected_country = None
hovered_country = None  # País sobre o qual o mouse está passando

# Menu de ações
menu_visible = False
menu_options = ["A - Atacar", "Z - Avançar"]
menu_position = (0, 0)

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
        properties['territórios'] = 1


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
    """Mostra as informações do país selecionado."""
    if selected_country:
        population = CountryUtils.get_pop(country=selected_country)
        pib = CountryUtils.get_pib(country=selected_country)
        pib_unity = Formatters().get_pib_unity(pib)

        info_text = [
            f"Você está jogando com {selected_country['name']}",
            f"PIB: {pib} {pib_unity}",
            f"Militar: {selected_country['militar']}",
            f"Territórios: {selected_country['territórios']}",
            f"População: {population}"
        ]
        for i, line in enumerate(info_text):
            text = font.render(line, True, BLACK)
            screen.blit(text, (80, 50 + i * 20))


def show_hovered_info():
    """Mostra as informações do país sobre o qual o mouse está passando."""
    if hovered_country:
        population = CountryUtils.get_pop(country=hovered_country)
        pib = CountryUtils.get_pib(country=hovered_country)
        pib_unity = Formatters().get_pib_unity(pib)

        info_text = [
            f"País: {hovered_country['name_pt']}",
            f"PIB: {pib} {pib_unity}",
            f"Militar: {hovered_country['militar']}",
            f"Territórios: {hovered_country['territórios']}",
            f"População: {population}",
        ]
        for i, line in enumerate(info_text):
            text = font.render(line, True, BLACK)
            screen.blit(text, (80, (screen.get_height() - 200) + i * 20))


def show_battle_log(log):
    """Mostra o resultado das batalhas."""
    battle_text = font.render(log, True, BLACK)
    screen.blit(battle_text, (20, window_size[1] - 40))


def show_menu():
    """Exibe o menu de ações ao clicar com o botão direito."""
    if menu_visible:
        for i, option in enumerate(menu_options):
            text = font.render(option, True, WHITE)
            screen.blit(text, (menu_position[0], menu_position[1] + i * 20))


def attack_country(attacker, defender):
    """Simula um ataque de um país a outro."""
    poder_atacante = attacker["militar"] + random.randint(-10, 20)
    poder_defensor = defender["militar"] + random.randint(-10, 20)

    if poder_atacante > poder_defensor:
        # Sucesso no ataque: anexar parte do PIB e força militar
        anexar_porcentagem = 0.3  # 30% de anexação

        attacker["pib"] += defender["pib"] * anexar_porcentagem
        attacker["militar"] += int(defender["militar"] * anexar_porcentagem)
        attacker["territórios"] += defender["territórios"]

        defender["territórios"] = 0  # País conquistado
        defender["militar"] = 0
        defender["pib"] = 0
        defender["color"] = attacker["color"]  # Mudança de cor para o país conquistador

        log = f"{attacker['name']} anexou {defender['name']} com sucesso!"
    else:
        log = f"{defender['name']} defendeu com sucesso o ataque de {attacker['name']}!"

    # Atualização da força militar e PIB do atacante devido ao custo do ataque
    attacker["militar"] -= int(attacker["militar"] * 0.1)  # 10% de perda militar
    attacker["pib"] -= attacker["pib"] * 0.05  # 5% de perda no PIB

    return log


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
    show_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo do mouse
                menu_visible = False
                country_properties = get_country_info_at(*event.pos)
                if country_properties:
                    hovered_country = country_properties
            elif event.button == 3:  # Botão direito do mouse
                if selected_country and hovered_country and selected_country != hovered_country:
                    if hovered_country["territórios"] > 0:
                        menu_visible = True
                        menu_position = event.pos
                else:
                    menu_visible = False
        elif event.type == pygame.MOUSEMOTION:
            country_properties = get_country_info_at(*event.pos)
            if country_properties:
                hovered_country = country_properties
            else:
                hovered_country = None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and hovered_country:
                selected_country = hovered_country
            elif event.key == pygame.K_a and menu_visible:
                # if selected_country and hovered_country and selected_country != hovered_country:
                #     battle_log = attack_country(selected_country, hovered_country)
                #     menu_visible = False
                if selected_country and hovered_country and selected_country != hovered_country:
                    # Inicia a guerra em vez de um ataque único
                    nova_guerra = war_system.iniciar_guerra(selected_country, hovered_country)
                    guerras_ativas.append(nova_guerra)
                    battle_log = f"Guerra iniciada: {selected_country['name']} vs {hovered_country['name']}"
                    menu_visible = False
            elif event.key == pygame.K_z:
                # Avança as guerras existentes
                for guerra in guerras_ativas:
                    if guerra["em_andamento"]:
                        resultado = war_system.calcular_turno_guerra(guerra, country_info)
                        if resultado:
                            battle_log = resultado

    pygame.display.flip()

pygame.quit()
