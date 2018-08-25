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
pygame.display.set_caption("Smudge")
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
del_col_cap = 10
del_num_cap = 5

# Init
pxAr = pygame.PixelArray(sep_screen)
px_list = []
color_inertia = []
move_inertia = []
del_inertia = []

def color_drift(present_col, current_col):
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

            pos_col_change = 0
            neg_col_change = 0

            color_dir = random.randint(-1, 2)
            if color_dir >= 2:
                color_dir = color_inertia[index][i]
                
            if color_dir == 0:
                pos_col_change = color_change
                neg_col_change = -color_change
                color_inertia[index][i] = 0
            elif color_dir == 1:
                pos_col_change = color_change
                color_inertia[index][i] = 1
            elif color_dir == -1:
                neg_col_change = -color_change
                color_inertia[index][i] = -1

            # Change color
            current_col[i] += random.randint(neg_col_change, pos_col_change)

    return(current_col)

def rm(removed):
    if not removed:
        px_list_cp.remove(current_pos)
        del color_inertia[index]
        del move_inertia[index]
        del del_inertia[index]
        return True
    return removed

def set_new_px(n, removed):
    new_pos = set_new_pos(n)

    current_col = sep_screen.get_at(current_pos)
    present_col = sep_screen.get_at(new_pos)

    pxAr[new_pos[0], new_pos[1]] = color_drift(present_col, current_col)

    # Check for magnitude of color change
    a = present_col[0] - current_col[0]
    b = present_col[1] - current_col[1]
    c = present_col[2] - current_col[2]
    mag_chg = math.sqrt(a * a + b * b + c * c)

    if mag_chg > del_col_cap:
        del_inertia[index] = 0

    px_list_cp.append(new_pos)
    color_inertia.append(color_inertia[index])
    move_inertia.append(move_inertia[index])
    del_inertia.append(del_inertia[index] + 1)

    removed = rm(removed)

    # Set removed flag
    return removed

def set_new_pos(n):
    if n == 0:
        return [current_pos[0] + 1, current_pos[1]]
    elif n == 1:
        return [current_pos[0] - 1, current_pos[1]]
    elif n == 2:
        return [current_pos[0], current_pos[1] + 1]
    elif n == 3:
        return [current_pos[0], current_pos[1] - 1]

# Init random pixels
for y in range(0, act_size[1]):
    for x in range(0, act_size[0]):
        if random.randint(0, emerge_chance_cap) > emerge_chance:
            pxAr[x, y] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            px_list.append([x, y])
            color_inertia.append([0, 0, 0])
            move_inertia.append(random.randint(0, 3))
            del_inertia.append(0)

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

        for index, current_pos in enumerate(px_list):
            # Pixel decides to move
            growth_flag = random.randint(0, growth_chance_cap) > growth_chance

            if growth_flag:

                # Pixel chooses random direction to move
                # Higher likelihood to move in same direction
                direction = random.randint(0, 5)
                if direction >= 4:
                    direction = move_inertia[index]

                # Set move_inertia
                move_inertia[index] = direction

                # Pixel must be able to move in the direction
                dir_flags = [current_pos[0] <= act_size[0] - 2,
                            current_pos[0] >= 1,
                            current_pos[1] <= act_size[1] - 2,
                            current_pos[1] >= 1]


                for i in range(0, 4):
                    if dir_flags[i] and direction == i:
                        removed = set_new_px(i, removed)

                # If no movement, remove
                removed = rm(removed)

                # If del_inertia exceeds del_num_cap, delete
                if del_inertia[index] > del_num_cap:
                    removed = rm(removed)

        px_list = px_list_cp[:]

    # Shuffle all paralell lists simultaneously and delete the same elements
    if len(px_list) > list_cap:
        shuffler = list(zip(px_list, color_inertia, move_inertia, del_inertia))
        random.shuffle(shuffler)
        px_list, color_inertia, move_inertia, del_inertia = zip(*shuffler)

        px_list = list(px_list)
        color_inertia = list(color_inertia)
        move_inertia = list(move_inertia)
        del_inertia = list(del_inertia)

        del color_inertia[1:len(px_list) - list_cap]
        del move_inertia[1:len(px_list) - list_cap]
        del del_inertia[1:len(px_list) - list_cap]
        del px_list[1:len(px_list) - list_cap]

    # To scale image up
    screen.blit(pygame.transform.scale(sep_screen, disp_size), (0, 0))

    pygame.display.flip()

    # just run as fast as possible
    # clock.tick(60)

# Clean up ar
del pxAr
pygame.quit()
