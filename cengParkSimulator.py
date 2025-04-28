import pygame
import random
import string

# Initialize pygame
pygame.init()

# Screen dimensions
DISPLAY_WIDTH = 200
GAME_AREA_WIDTH = 1300
SCREEN_WIDTH, SCREEN_HEIGHT = DISPLAY_WIDTH + GAME_AREA_WIDTH, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Ceng Parking Lot Simulator')

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
queue_places_per_column = 2
parking_height = places_per_column * SCREEN_HEIGHT // (places_per_column + queue_places_per_column + 1)
queue_height = queue_places_per_column * SCREEN_HEIGHT // (places_per_column + queue_places_per_column + 1)
empty_height = SCREEN_HEIGHT - parking_height - queue_height
floor_width = GAME_AREA_WIDTH // floors
car_width, car_height = floor_width // 3, parking_height // (places_per_column * 1.2)

# Font setup
floor_font_size = 50
display_font = pygame.font.SysFont(None, 24)
floor_font = pygame.font.SysFont(None, floor_font_size)

# Generate parking spots
parking_spots = []
for floor in range(floors):
    for col in range(2):
        for spot in range(places_per_column):
            x = floor * floor_width + col * (floor_width // 2) + floor_width // 4 - car_width // 2 + ((2 * (col % 2) - 1) * car_width) // 6.5
            y = spot * (parking_height // places_per_column) + (parking_height // (places_per_column * 2) - car_height // 2)
            parking_spots.append({'rect': pygame.Rect(x, y, car_width, car_height), 'floor': floor})

queue_spots = []
for floor in range(floors):
    for col in range(2):
        for queue in range(queue_places_per_column):
            x = floor * floor_width + col * (floor_width // 2) + (floor_width // 4 - car_width // 2)
            y = queue * (parking_height // places_per_column) + (parking_height // (places_per_column * 2) - car_height // 2) + empty_height + parking_height
            queue_spots.append(pygame.Rect(x, y, car_width, car_height))

floor_character_spots = []
for floor in range(floors):
    x = floor * floor_width + floor_width // 2 - 3 * floor_font_size // 10
    y = parking_height // 2 - 3 * floor_font_size // 10
    floor_character_spots.append((string.ascii_uppercase[floor], (x, y)))

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
        pygame.draw.line(screen, yellow_color, (i * floor_width, 0), (i * floor_width, parking_height), 5)

    pygame.draw.line(screen, white_color, (3 * car_width // 2, parking_height + empty_height - 10), (GAME_AREA_WIDTH - 2, parking_height + empty_height - 10), 2)

    # Draw parking spot lines
    for park_ind in range(cars_per_floor):
        for floor in range(floors):
            spot = parking_spots[floor * cars_per_floor + park_ind]
            pygame.draw.rect(screen, white_color, spot['rect'], 2)
            id_text = display_font.render(str(park_ind + 1), True, white_color)
            text_rect = id_text.get_rect(center=spot['rect'].center)
            screen.blit(id_text, text_rect)

    # Draw queue spot lines
    for queue in queue_spots:
        pygame.draw.rect(screen, white_color, queue, 2)

    # Draw Floor Characters
    for char, position in floor_character_spots:
        text = floor_font.render(char, True, white_color)
        screen.blit(text, position)

    # Draw cars with IDs
    for idx, spot in enumerate(filled_spots):
        pygame.draw.rect(screen, car_color, spot['rect'])
        id_text = display_font.render(str(idx + 101), True, white_color)
        text_rect = id_text.get_rect(center=spot['rect'].center)
        screen.blit(id_text, text_rect)

    # Display cars per floor information
    for floor in range(floors):
        floor_cars = sum(1 for spot in filled_spots if spot['floor'] == floor)
        floor_text = display_font.render(f'Floor {floor + 1}: {floor_cars} cars', True, text_color)
        screen.blit(floor_text, (GAME_AREA_WIDTH + 20, 20 + floor * 30))

    # Update display
    pygame.display.flip()

pygame.quit()
