import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
import random
import string
import time
import threading

# Screen dimensions
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 600
DISPLAY_WIDTH = 200
SIMULATOR_CAPTION = 'Ceng Parking Lot Simulator'

# Parking lot configuration
FLOORS = 4
CARS_PER_FLOOR = 10

class Car:
    def __init__(self, car_id, car_color):
        self.car_id = car_id
        self.car_color = car_color

class CarQueue:
    def __init__(self, no_cars):
        self.no_cars = no_cars
        self.queue = []
        self.lock = threading.Lock()  

    def add_car(self, car):
        with self.lock:  
            if len(self.queue) < self.no_cars:
                self.queue.append(car)
                return True
            else:
                print("Queue is full. Cannot add car.")
                #TODO: Handle full queue case
                return False

    def remove_car(self):
        with self.lock:  
            if self.queue:
                return self.queue.pop(0)
            else:
                print("Queue is empty. Cannot remove car.")
                #TODO: Handle empty queue case
                return None

    def get_queue(self):
        with self.lock:  
            return list(self.queue)  

    def get_queue_size(self):
        with self.lock:  
            return len(self.queue)

    def is_full(self):
        with self.lock:  
            return len(self.queue) >= self.no_cars

    def is_empty(self):
        with self.lock:  
            return len(self.queue) == 0

class ParkingLot:
    def __init__(self, floors, places_per_floor):
        self.floors = floors
        self.places_per_floor = places_per_floor
        self.spots = [[None for _ in range(places_per_floor)] for _ in range(floors)]
        self.lock = threading.Lock() 

    def park_car(self, floor, spot, car):
        with self.lock:  
            if self.spots[floor][spot] is None:
                entry_time = time.time()  
                self.spots[floor][spot] = (car, entry_time)
                return True
            else:
                print(f"Spot {spot} on floor {floor} is already occupied.")
                return False

    def remove_car(self, floor, spot):
        with self.lock:  
            if self.spots[floor][spot] is not None:
                car, entry_time = self.spots[floor][spot]
                self.spots[floor][spot] = None
                return car, entry_time
            else:
                print(f"Spot {spot} on floor {floor} is already empty.")
                return None

    def get_number_of_cars(self, floor):
        with self.lock:  
            return sum(1 for spot in self.spots[floor] if spot is not None)

    def get_total_cars(self):
        with self.lock:  
            return sum(self.get_number_of_cars(floor) for floor in range(self.floors))

    def read_spot(self, floor, spot):
        with self.lock: 
            return self.spots[floor][spot]
        
    def get_1D_spots(self):
        with self.lock:  
            return [spot for floor in self.spots for spot in floor]

class GameEngine:
    class Drawer:
        def __init__(self, screen_width, screen_height, display_width, floors, cars_per_floor, simulator_caption, car_queue: CarQueue, parking_lot):

            self.car_queue = car_queue
            self.parking_lot = parking_lot

            self.screen_width = screen_width
            self.screen_height = screen_height
            self.display_width = display_width
            self.game_area_width = screen_width - display_width

            self.floors = floors
            self.cars_per_floor = cars_per_floor
            self.places_per_column = cars_per_floor // 2
            self.queue_places_per_column = 2

            self.parking_height = self.places_per_column * screen_height // (self.places_per_column + self.queue_places_per_column + 1)
            self.queue_height = self.queue_places_per_column * screen_height // (self.places_per_column + self.queue_places_per_column + 1)
            self.empty_height = screen_height - self.parking_height - self.queue_height
            self.floor_width = self.game_area_width // floors
            self.car_width, self.car_height = self.floor_width // 3, self.parking_height // (self.places_per_column * 1.2)

            self.floor_font_size = 50
            self.display_font = pygame.font.SysFont(None, 24)
            self.floor_font = pygame.font.SysFont(None, self.floor_font_size)
            self.gray_color = (128, 128, 148)
            self.white_color = (255, 255, 255)
            self.yellow_color = (204, 204, 0)
            self.black_color = (0, 0, 0)
            self.text_color = (255, 255, 255)
            
            self.car_colors = [
                (0, 0, 0),        # Black
                (210, 192, 210),  # Cream
                (128, 128, 128),  # Gray
                (192, 192, 192),  # Silver
                (0, 0, 255),      # Blue
                (0, 128, 255),    # Light Blue
                (255, 0, 0),      # Red
                (139, 0, 0),      # Dark Red
                (0, 128, 0),      # Green
                (255, 165, 0),    # Orange
                (128, 0, 128),    # Purple
                (210, 180, 140),  # Tan
                (255, 215, 0),    # Gold
                (105, 105, 105),  # Dark Gray
                (70, 130, 180),   # Steel Blue
                (0, 100, 0),      # Dark Green
                (220, 20, 60),    # Crimson
                (112, 128, 144),  # Slate Gray
                (47, 79, 79),     # Dark Slate Gray
                (169, 169, 169)   # Light Gray
            ]

            self.parking_spots = self.init_parking_spots()
            self.queue_spots = self.init_queue_spots()
            self.floor_character_spots = self.init_floor_character_spots()
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption(simulator_caption)

        def init_parking_spots(self):
            parking_spots = []
            for floor in range(self.floors):
                for col in range(2):
                    for spot in range(self.places_per_column):
                        x = floor * self.floor_width + col * (self.floor_width // 2) + self.floor_width // 4 - self.car_width // 2 + ((2 * (col % 2) - 1) * self.car_width) // 6.5
                        y = spot * (self.parking_height // self.places_per_column) + (self.parking_height // (self.places_per_column * 2) - self.car_height // 2)
                        parking_spots.append(pygame.Rect(x, y, self.car_width, self.car_height))
            return parking_spots    

        def init_queue_spots(self):
            queue_spots = []
            for queue in range(self.queue_places_per_column):
                for floor in range(self.floors):
                    for col in range(2):
                        x = floor * self.floor_width + col * (self.floor_width // 2) + (self.floor_width // 4 - self.car_width // 2)
                        y = queue * (self.parking_height // self.places_per_column) + (self.parking_height // (self.places_per_column * 2) - self.car_height // 2) + self.empty_height + self.parking_height
                        queue_spots.append(pygame.Rect(x, y, self.car_width, self.car_height))
            return queue_spots
        
        def init_floor_character_spots(self):
            floor_character_spots = []
            for floor in range(self.floors):
                x = floor * self.floor_width + self.floor_width // 2 - 3 * self.floor_font_size // 10
                y = self.parking_height // 2 - 3 * self.floor_font_size // 10
                floor_character_spots.append((string.ascii_uppercase[floor], (x, y)))
            return floor_character_spots
        
        def draw(self):
            # Clear screen
            self.screen.fill(self.black_color)

            # Game area background
            pygame.draw.rect(self.screen, self.gray_color, pygame.Rect(0, 0, self.game_area_width, self.screen_height))

            # Draw vertical lines to divide floors
            for i in range(1, self.floors):
                pygame.draw.line(self.screen, self.yellow_color, (i * self.floor_width, 0), (i * self.floor_width, self.parking_height), 5)

            # Draw horizontal line to separate parking and queue areas
            pygame.draw.line(self.screen, (60, 30, 20), (3 * self.car_width // 2, self.parking_height + self.empty_height - 10), (self.game_area_width, self.parking_height + self.empty_height - 10), 10)

            # Draw parking spot lines
            for park_ind in range(self.cars_per_floor):
                for floor in range(self.floors):
                    spot = self.parking_spots[floor * self.cars_per_floor + park_ind]
                    pygame.draw.rect(self.screen, self.white_color, spot, 2)
                    id_text = self.display_font.render(str(park_ind + 1), True, self.white_color)
                    text_rect = id_text.get_rect(center=spot.center)
                    self.screen.blit(id_text, text_rect)

            # Draw queue spot lines
            for queue in self.queue_spots:
                pygame.draw.rect(self.screen, self.white_color, queue, 2)

            # Draw Floor Characters
            for char, position in self.floor_character_spots:
                text = self.floor_font.render(char, True, self.white_color)
                self.screen.blit(text, position)

            # Draw parked cars
            for car, spot in zip(self.parking_lot.get_1D_spots(), self.parking_spots):
                if car is not None:
                    pygame.draw.rect(self.screen, car[0].car_color, spot)
                    id_text = self.display_font.render(str(car[0].car_id), True, self.white_color)
                    text_rect = id_text.get_rect(center=spot.center)
                    self.screen.blit(id_text, text_rect)

            # Display queue cars
            for car, queue_spot in zip(self.car_queue.get_queue(), self.queue_spots):
                pygame.draw.rect(self.screen, car.car_color, queue_spot)
                id_text = self.display_font.render(str(car.car_id), True, self.white_color)
                text_rect = id_text.get_rect(center=queue_spot.center)
                self.screen.blit(id_text, text_rect)

            # Display cars per floor information
            for floor in range(self.floors):
                floor_cars = self.parking_lot.get_number_of_cars(floor)
                floor_text = self.display_font.render(f'Floor {floor + 1}: {floor_cars} cars', True, self.text_color)
                self.screen.blit(floor_text, (self.game_area_width + 20, 20 + floor * 30))

            # Update display
            pygame.display.flip()

    def __init__(self, screen_width, screen_height, display_width, simulator_caption, floors, cars_per_floor):
        pygame.init()
        self.parking_lot = ParkingLot(floors, cars_per_floor)
        self.car_queue = CarQueue(4 * floors) 
        self.drawer = self.Drawer(screen_width, screen_height, display_width, floors, cars_per_floor, simulator_caption, self.car_queue, self.parking_lot)

    def run(self):
        # Main loop
        running = True
        last_time = time.time()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        # Add a car to the queue
                        car_id = random.randint(0, 100)
                        car_color = random.choice(self.drawer.car_colors)
                        new_car = Car(car_id, car_color)
                        if self.car_queue.add_car(new_car):
                            print(f"Car {car_id} added to the queue.")
                        else:
                            print("Queue is full. Cannot add car.")
                

            current_time = time.time()
            if current_time - last_time >= 1:
                last_time = current_time  # Reset the timer

                # Move a car from the queue to the parking lot
                if not self.car_queue.is_empty():
                    car = self.car_queue.remove_car()
                    for floor in range(self.parking_lot.floors):
                        for spot in range(self.parking_lot.places_per_floor):
                            if self.parking_lot.park_car(floor, spot, car):
                                break
                        else:
                            # Continue to the next floor if no spot is available
                            continue
                        break

            self.drawer.draw()
        pygame.quit()

if __name__ == "__main__":
    game_engine = GameEngine(SCREEN_WIDTH, SCREEN_HEIGHT, DISPLAY_WIDTH, SIMULATOR_CAPTION, FLOORS, CARS_PER_FLOOR)
    game_engine.run()
