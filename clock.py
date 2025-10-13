import pygame
import sys
import datetime

pygame.init()
size = (800, 800)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Date and Time Display")

# Load custom TTF font (make sure the file exists in the same folder)
font_path = "ShareTechMono-Regular.ttf"  # replace with your font filename
font_date = pygame.font.Font(font_path, 64)
font_time = pygame.font.Font(font_path, 128)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    screen.fill(BLACK)

    date_surface = font_date.render(date_str, True, WHITE)
    time_surface = font_time.render(time_str, True, WHITE)

    date_rect = date_surface.get_rect(center=(size[0] // 2, size[1] // 4))
    time_rect = time_surface.get_rect(center=(size[0] // 2, size[1] * 2 // 4))

    screen.blit(date_surface, date_rect)
    screen.blit(time_surface, time_rect)

    pygame.display.flip()
    clock.tick(30)
