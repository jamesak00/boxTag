import pygame
import pygame.mixer
import random
from collections import deque

from sympy.strategies.core import switch

# Define colours
RED = (255, 182, 193)
GREEN = (50, 205, 50)
BLUE = (0, 123, 167)
BLACK = (0, 0, 0)


SOUND_ENABLED = True  # Set to True to enable sounds, False to disable them

# Define the box class
class Box:
    def __init__(self, x, y, colour):
        self.x = x
        self.y = y
        self.colour = colour
        self.rect = pygame.Rect(self.x, self.y, 10, 10)
        self.processed = False
        self.dx = 0  # velocity in x direction
        self.dy = 0  # velocity in y direction

    def draw(self, win):
        pygame.draw.rect(win, self.colour, self.rect)

    def move_towards(self, target, boxes, speed, window_size):
        dx = target.rect.x - self.rect.x
        dy = target.rect.y - self.rect.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > 0:
            dx /= distance
            dy /= distance

        future_rect = self.rect.move(dx * speed, dy * speed)

        if not any(pygame.Rect.colliderect(future_rect, b.rect) for b in boxes if b is not self):
            self.rect.x += dx * speed
            self.rect.y += dy * speed
            self.dx = dx * speed
            self.dy = dy * speed
        else:
            # Bounce off other boxes
            self.rect.x += self.dx
            self.rect.y += self.dy

            # Add a repulsion force
            for b in boxes:
                if b is not self:
                    dx = self.rect.x - b.rect.x
                    dy = self.rect.y - b.rect.y
                    distance = max((dx ** 2 + dy ** 2) ** 0.5, 1)

                    if distance < 20:
                        self.rect.x += dx / distance
                        self.rect.y += dy / distance

            # Keep the box within the window
            self.rect.x = min(max(self.rect.x, 0), window_size[0] - 10)
            self.rect.y = min(max(self.rect.y, 0), window_size[1] - 10)

def change_colour(box, target_colour, boxes):
    queue = deque([box])

    while queue:
        current_box = queue.popleft()
        current_box.colour = target_colour
        current_box.processed = True

        for b in boxes:
            if pygame.Rect.colliderect(current_box.rect, b.rect) and b.colour == current_box.colour and not b.processed:
                queue.append(b)

    # Reset the processed attribute for all boxes
    for box in boxes:
        box.processed = False

def main():
    global SOUND_ENABLED # Declare SOUND_ENABLED as global at the start of the function
    pygame.init()

    # Initialize mixer only if sound is enabled
    if SOUND_ENABLED:
        pygame.mixer.init()

    SPEED = 1  # Adjust this value to change the speed of the boxes
    w = 600
    h = 400
    win = pygame.display.set_mode((w, h), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    boxes = [Box(random.randint(0, w), random.randint(0, h), random.choice([RED, GREEN, BLUE])) for _ in range(200)]

    # Load sounds only if sound is enabled
    red_sound = None
    green_sound = None
    blue_sound = None
    if SOUND_ENABLED:
        try:
            red_sound = pygame.mixer.Sound('sounds/red.wav')
            green_sound = pygame.mixer.Sound('sounds/green.wav')
            blue_sound = pygame.mixer.Sound('sounds/blue.wav')
        except pygame.error as e:
            print(f"Could not load sound files. Sounds will be disabled. Error: {e}")
            SOUND_ENABLED = False # Disable sound if files are missing

    # Create a font object
    font = pygame.font.Font(None, 36)

    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.VIDEORESIZE: # Add this to handle window resizing
                w, h = event.size
                win = pygame.display.set_mode((w, h), pygame.RESIZABLE)

        win.fill(BLACK)

        # Check if all boxes have become the same colour
        if len(set(box.colour for box in boxes)) == 1:
            colour_name = 'RED' if boxes[0].colour == RED else 'GREEN' if boxes[0].colour == GREEN else 'BLUE'
            text_colour = (255, 255, 255) # Set default colour to white

            match colour_name:
                case 'RED':
                    text_colour = RED
                case 'GREEN':
                    text_colour = GREEN
                case 'BLUE':
                    text_colour = BLUE

            print(f"The {colour_name} team won!")
            win_message = font.render(f"The {colour_name} team won!", True, text_colour)
            win.blit(win_message, (w // 2 - win_message.get_width() // 2, h // 2 - win_message.get_height() // 2))
            pygame.display.update()
            pygame.time.wait(3000)
            run = False

        for box in boxes:
            box.draw(win)

            # Adjust the targeting logic
            if box.colour == RED:
                targets = [b for b in boxes if b.colour == GREEN]
            elif box.colour == GREEN:
                targets = [b for b in boxes if b.colour == BLUE]
            elif box.colour == BLUE:
                targets = [b for b in boxes if b.colour == RED]

            if targets:
                target = min(targets, key=lambda b: (box.rect.x - b.rect.x) ** 2 + (box.rect.y - b.rect.y) ** 2)
                box.move_towards(target, boxes, SPEED, pygame.display.get_surface().get_size())

            # Check for collision and convert colour
            if pygame.Rect.colliderect(box.rect, target.rect):
                if box.colour == RED and target.colour == GREEN:
                    change_colour(target, RED, boxes)
                    if SOUND_ENABLED and red_sound: # Play sound only if enabled and loaded
                        red_sound.play()
                elif box.colour == GREEN and target.colour == BLUE:
                    change_colour(target, GREEN, boxes)
                    if SOUND_ENABLED and green_sound: # Play sound only if enabled and loaded
                        green_sound.play()
                elif box.colour == BLUE and target.colour == RED:
                    change_colour(target, BLUE, boxes)
                    if SOUND_ENABLED and blue_sound: # Play sound only if enabled and loaded
                        blue_sound.play()

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
