
import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont("Arial", 60, bold=True)
font = pygame.font.SysFont("Arial", 30)

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (30, 150, 30)

# Load images
background = pygame.image.load("Background.jpg").convert()
track = pygame.image.load("Track.png").convert()
original_car = pygame.image.load("Car.png").convert_alpha()

background = pygame.transform.scale(background, (WIDTH, HEIGHT))
track = pygame.transform.scale(track, (WIDTH, HEIGHT))
original_car = pygame.transform.scale(original_car, (60, 100))

# ------------------------------------------------
# TRACK MASK
# ------------------------------------------------

# IMPORTANT: These coordinates must identify a pixel
# that is actually on the road, not on the grass.
ROAD_COLOUR = track.get_at((400, 300))[:3]

# Create a surface containing two copies of the track.
# This allows collision detection to work even when
# the scrolling track passes the top/bottom boundary.
track_double = pygame.Surface((WIDTH, HEIGHT * 2))
track_double.blit(track, (0, 0))
track_double.blit(track, (0, HEIGHT))

# Create a mask containing only pixels similar to
# the road colour. Grass pixels are ignored.
track_mask = pygame.mask.from_threshold(track_double,ROAD_COLOUR,(35, 35, 35, 255))

mask_image = track_mask.to_surface()

pygame.image.save(mask_image, "Track_Mask.png")

# ------------------------------------------------
# GAME VARIABLES
# ------------------------------------------------

car_rect = original_car.get_rect(center=(400, 450))
car_angle = 0

speed = 0
max_speed = 10
scroll_y = 0

game_state = "menu"

# ------------------------------------------------
# MENU
# ------------------------------------------------

play_button = pygame.Rect(300, 280, 200, 60)
quit_button = pygame.Rect(300, 370, 200, 60)

def draw_menu():

    screen.fill(GREEN)

    title = title_font.render("RACING GAME", True, WHITE)
    screen.blit(title, title.get_rect(center=(400, 150)))

    pygame.draw.rect(screen, BLACK, play_button)
    pygame.draw.rect(screen, BLACK, quit_button)

    play_text = font.render("PLAY", True, WHITE)
    quit_text = font.render("QUIT", True, WHITE)

    screen.blit(play_text, play_text.get_rect(center=play_button.center))
    screen.blit(quit_text, quit_text.get_rect(center=quit_button.center))

    pygame.display.update()

# ------------------------------------------------
# MAIN GAME LOOP
# ------------------------------------------------

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Menu mouse controls
        if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:

            if play_button.collidepoint(event.pos):
                game_state = "playing"
                speed = 0
                scroll_y = 0
                car_angle = 0
                car_rect.center = (400, 450)

            if quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

        # Keyboard controls
        if event.type == pygame.KEYDOWN:

            if game_state == "menu" and event.key == pygame.K_SPACE:
                game_state = "playing"

            elif event.key == pygame.K_ESCAPE:
                game_state = "menu"

    # ------------------------------------------------
    # MENU SCREEN
    # ------------------------------------------------

    if game_state == "menu":
        draw_menu()

    # ------------------------------------------------
    # GAME SCREEN
    # ------------------------------------------------

    elif game_state == "playing":

        keys = pygame.key.get_pressed()

        # --------------------------------------------
        # ACCELERATION AND BRAKING
        # --------------------------------------------

        if keys[pygame.K_UP]:
            speed = min(speed + 0.1, max_speed)

        if keys[pygame.K_DOWN]:
            speed = max(speed - 0.15, 0)

        # --------------------------------------------
        # STEERING AND CAR ROTATION
        # --------------------------------------------

        if keys[pygame.K_LEFT]:
            car_rect.x -= 3
            car_angle = min(car_angle + 2, 30)

        elif keys[pygame.K_RIGHT]:
            car_rect.x += 3
            car_angle = max(car_angle - 2, -30)

        else:
            # Gradually straighten the car when
            # the player stops steering.
            if car_angle > 0:
                car_angle -= 1
            elif car_angle < 0:
                car_angle += 1

        # Keep car inside the screen boundaries
        car_rect.x = max(0, min(WIDTH - car_rect.width, car_rect.x))

        # --------------------------------------------
        # ROTATE THE CAR IMAGE
        # --------------------------------------------

        # Rotate the original image rather than rotating
        # an already rotated image. This avoids losing
        # image quality every time the car turns.

        rotated_car = pygame.transform.rotate(original_car, car_angle)

        # Keep the centre of the car in the same position
        # because rotating an image changes its dimensions.
        rotated_rect = rotated_car.get_rect(center=car_rect.center)

        # Create a NEW mask for the rotated car.
        # This is important because its shape has changed.
        car_mask = pygame.mask.from_surface(rotated_car)

        # --------------------------------------------
        # COLLISION DETECTION
        # --------------------------------------------

        # The track is scrolling down the screen.
        # Therefore, the car's screen position must be
        # translated into its position on the double mask.
        #
        # Adding HEIGHT places the car inside the second
        # copy of the track.
        #
        # Subtracting scroll_y ensures that the mask
        # moves in exactly the same way as the track image.

        offset = (
            rotated_rect.left,
            rotated_rect.top - scroll_y + HEIGHT
        )

        # Count the number of car pixels that overlap
        # with road pixels.
        overlapping_pixels = track_mask.overlap_area(
            car_mask, offset
        )

        # Count all visible pixels in the rotated car.
        total_car_pixels = car_mask.count()

        # Work out how many car pixels are NOT on the road.
        outside_pixels = total_car_pixels - overlapping_pixels

        # Convert this into a percentage.
        outside_percentage = (
            outside_pixels / total_car_pixels
        ) * 100

        # --------------------------------------------
        # SLOW DOWN WHEN OFF THE TRACK
        # --------------------------------------------

        if outside_percentage > 60:
            speed = max(speed - 0.2, 0)

        # --------------------------------------------
        # SCROLLING BACKGROUND AND TRACK
        # --------------------------------------------

        # Increase scroll_y according to the car's speed.
        scroll_y = (scroll_y + speed) % HEIGHT

        # Draw two copies of the background so that
        # there is no gap when the screen scrolls.
        screen.blit(background, (0, scroll_y - HEIGHT))
        screen.blit(background, (0, scroll_y))

        # Draw two copies of the track.
        screen.blit(track, (0, scroll_y - HEIGHT))
        screen.blit(track, (0, scroll_y))

        # Draw the rotated car.
        screen.blit(rotated_car, rotated_rect)

        # --------------------------------------------
        # DISPLAY SPEED AND OFF-TRACK INFORMATION
        # --------------------------------------------

        speed_text = font.render(
            "Speed: " + str(int(speed * 10)),
            True, WHITE
        )

        screen.blit(speed_text, (20, 20))

        if outside_percentage > 50:
            warning = font.render("OFF TRACK!", True, WHITE)
            screen.blit(warning, (20, 60))

        pygame.display.update()

    clock.tick(60)
