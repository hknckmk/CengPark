import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1500, 600
GAME_AREA_WIDTH = 1300
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Parking Lot Simulator')

# Colors
gray_color = (128, 128, 128)
white_color = (255, 255, 255)
car_color = (255, 0, 0)
yellow_color = (204, 204, 0)
black_color = (0, 0, 0)
text_color = (255, 255, 255)

# Parking lot configuration
floors = 4
cars_per_floor = 10
places_per_column = 5
floor_width = GAME_AREA_WIDTH // floors
car_width, car_height = floor_width // 3, SCREEN_HEIGHT // (places_per_column * 2)

# Font setup
font = pygame.font.SysFont(None, 24)

# Generate parking spots
parking_spots = []
for floor in range(floors):
    for col in range(2):
        for spot in range(places_per_column):
            x = floor * floor_width + col * (floor_width // 2) + (floor_width // 4 - car_width // 2)
            y = spot * (SCREEN_HEIGHT // places_per_column) + (SCREEN_HEIGHT // (places_per_column * 2) - car_height // 2)
            parking_spots.append({'rect': pygame.Rect(x, y, car_width, car_height), 'floor': floor})

# Randomly fill parking spots
filled_spots = random.sample(parking_spots, k=random.randint(0, len(parking_spots)))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    screen.fill(black_color)

    # Game area background
    pygame.draw.rect(screen, gray_color, pygame.Rect(0, 0, GAME_AREA_WIDTH, SCREEN_HEIGHT))

    # Draw vertical lines to divide floors
    for i in range(1, floors):
        pygame.draw.line(screen, yellow_color, (i * floor_width, 0), (i * floor_width, SCREEN_HEIGHT), 5)

    # Draw parking spot lines
    for spot in parking_spots:
        pygame.draw.rect(screen, white_color, spot['rect'], 2)

    # Draw cars with IDs
    for idx, spot in enumerate(filled_spots):
        pygame.draw.rect(screen, car_color, spot['rect'])
        id_text = font.render(str(idx + 1), True, white_color)
        text_rect = id_text.get_rect(center=spot['rect'].center)
        screen.blit(id_text, text_rect)

    # Display cars per floor information
    for floor in range(floors):
        floor_cars = sum(1 for spot in filled_spots if spot['floor'] == floor)
        floor_text = font.render(f'Floor {floor + 1}: {floor_cars} cars', True, text_color)
        screen.blit(floor_text, (GAME_AREA_WIDTH + 20, 20 + floor * 30))

    # Update display
    pygame.display.flip()

pygame.quit()
