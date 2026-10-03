import os
import sys



from data import TEAMS
from database import init_db


WIDTH = 1280
HEIGHT = 760
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (30, 130, 65)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Football")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 32)


def draw_text(text, x, y, color=WHITE, center=False):
    surface = font.render(str(text), True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)
    return rect


def main_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        screen.fill(GREEN)
        draw_text("Ultimate Football", WIDTH // 2, HEIGHT // 2 - 30, center=True)
        draw_text("Press ENTER to start", WIDTH // 2, HEIGHT // 2 + 30, center=True)
        pygame.display.flip()
        clock.tick(FPS)


def main():
    init_db()
    print(f"Loaded {len(TEAMS)} teams")
    main_menu()
    print("Game started successfully")


if __name__ == "__main__":
    main()
