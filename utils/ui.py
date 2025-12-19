import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, bg_color=(200, 200, 200), text_color=(0, 0, 0), hover_color=(170, 170, 170)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.current_color = bg_color

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.bg_color

        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2) # Border

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class ContextMenu:
    def __init__(self, font):
        self.options = [] # List of dictionaries: {'text': str, 'action': func, 'rect': Rect}
        self.font = font
        self.visible = False
        self.position = (0, 0)
        self.width = 150
        self.item_height = 30
        self.bg_color = (50, 50, 50)
        self.text_color = (255, 255, 255)
        self.hover_color = (80, 80, 80)

    def show(self, pos, options):
        """
        options: list of dicts {'text': 'Attack', 'action': 'attack'}
        """
        self.visible = True
        self.position = pos
        self.options = []
        for i, opt in enumerate(options):
            rect = pygame.Rect(pos[0], pos[1] + i * self.item_height, self.width, self.item_height)
            self.options.append({
                'text': opt['text'],
                'action_id': opt['action'],
                'rect': rect
            })

    def hide(self):
        self.visible = False
        self.options = []

    def draw(self, screen):
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()
        
        # Draw background container
        total_height = len(self.options) * self.item_height
        container_rect = pygame.Rect(self.position[0], self.position[1], self.width, total_height)
        pygame.draw.rect(screen, self.bg_color, container_rect)
        pygame.draw.rect(screen, (200, 200, 200), container_rect, 1) # Border

        for opt in self.options:
            color = self.bg_color
            if opt['rect'].collidepoint(mouse_pos):
                color = self.hover_color
            
            pygame.draw.rect(screen, color, opt['rect'])
            
            text_surf = self.font.render(opt['text'], True, self.text_color)
            # Left align with some padding
            text_rect = text_surf.get_rect(midleft=(opt['rect'].left + 10, opt['rect'].centery))
            screen.blit(text_surf, text_rect)

    def handle_click(self, event):
        if not self.visible:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for opt in self.options:
                if opt['rect'].collidepoint(event.pos):
                    self.hide()
                    return opt['action_id']
            # If clicked outside, hide
            self.hide()
        return None
