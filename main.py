import math
import pygame
import random

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY  = (205, 205, 205)

# System
pygame.init()
act_size = (80, 80)
disp_size = (800, 800)
screen = pygame.display.set_mode(disp_size)
sep_screen = pygame.Surface(act_size)
pygame.display.set_caption("Growth Art")
clock = pygame.time.Clock()
done = False
start = False

# Consts
growth_chance = 25
growth_chance_cap = 100
emerge_chance = 998
emerge_chance_cap = 1000
list_cap = 3000
color_change = 20

def color_drift(current_col, present_col):
    if present_col != BLACK and present_col != current_col:
        # Blend colors if collision
        for i in range(0, 3):
            col = present_col[i] - current_col[i]
            if col > 0:
                current_col[i] += random.randint(0, col)
            else:
                current_col[i] += random.randint(col, 0)
    else:
        # For each color (r, g, b)
        for i in range(0, 3):
            # Ensures color can be randomized
            if current_col[i] > 255 - color_change:
                current_col[i] = 255 - color_change
            if current_col[i] < color_change:
                current_col[i] = color_change

            current_col[i] += random.randint(-color_change, color_change)

    return(current_col)

def rm(removed, px_list_cp, current_pos):
    if not removed:
        px_list_cp.remove(current_pos)
        return True
    return removed

def set_new_px(n, removed, px_list_cp, current_pos):
    new_pos = set_new_pos(n)
    present_col = sep_screen.get_at(new_pos)
    pxAr[new_pos[0], new_pos[1]] = color_drift(current_col, present_col)
    px_list_cp.append(new_pos)
    removed = rm(removed, px_list_cp, current_pos)
    # Set not_used and removed flags
    return False, removed

def set_new_pos(n):
    if n == 0:
        return [current_pos[0] + 1, current_pos[1]]
    elif n == 1:
        return [current_pos[0] - 1, current_pos[1]]
    elif n == 2:
        return [current_pos[0], current_pos[1] + 1]
    elif n == 3:
        return [current_pos[0], current_pos[1] - 1]

# Init
pxAr = pygame.PixelArray(sep_screen)
px_list = []

# Init random pixels
for y in range(0, act_size[1]):
    for x in range(0, act_size[0]):
        if random.randint(0, emerge_chance_cap) > emerge_chance:
            pxAr[x, y] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            px_list.append([x, y])

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    pressed = pygame.key.get_pressed()

    if pressed[pygame.K_SPACE]:
        start = True

    if start:
        # For keeping track of changes
        px_list_cp = px_list[:]
        removed = False
        not_used = True

        for current_pos in px_list:
            current_col = sep_screen.get_at(current_pos)

            # Pixel decides to move
            growth_flag = random.randint(0, growth_chance_cap) > growth_chance

            if growth_flag:

                # Pixel chooses random direction to move
                direction = random.randint(0, 3)

                # Pixel must be able to move in the direction
                dir_flags = [current_pos[0] <= act_size[0] - 2,
                            current_pos[0] >= 1,
                            current_pos[1] <= act_size[1] - 2,
                            current_pos[1] >= 1]


                for i in range(0, 4):
                    if dir_flags[i] and direction == i:
                        not_used, removed = set_new_px(i, removed, px_list_cp, current_pos)

                # If no movement, just remove
                removed = rm(removed, px_list_cp, current_pos)

            if not_used and not removed:
                px_list_cp.remove(current_pos)

        px_list = px_list_cp[:]

    if len(px_list) > list_cap:
        random.shuffle(px_list)
        del px_list[1:len(px_list) - list_cap]

    # To scale image up
    screen.blit(pygame.transform.scale(sep_screen, disp_size), (0, 0))

    pygame.display.flip()

    # just run as fast as possible
    # clock.tick(60)

# Clean up ar
del pxAr
pygame.quit()
