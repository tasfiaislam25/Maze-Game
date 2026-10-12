from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import sin, cos, radians, sqrt
import math
import random
import time

# ------------------------------
# Game state / constants
# ------------------------------
player_pos = [0.0, 0.0, 0.0]   # world coords
player_angle = 0.0             # degrees, 0 = facing +Y
player_life = 5
score = 0
game_over = False
game_won = False
player_bullets = 15
maze2_won = False  # Track if player has won maze2 at least once

camera_height = 400.0
camera_angle = 0.0
follow_player = False   # first-person toggle

MAZE_SIZE = 20
CELL_SIZE = 60
maze = []
PLAYER_RADIUS = 18.0

enemies = []
enemy_pulse = 0.0
ENEMY_COUNT = 3
enemy_spawn_timer = 0
ENEMY_SPAWN_DELAY = 100

bullets = []
bullet_speed = 14.0

treasures = []
TREASURE_COUNT = 5
TREASURE_TYPES = ['sphere', 'cube', 'cylinder']

current_maze_index = 0   # 0 => maze1, 1 => maze2
show_maze_selection = False

# Rotation timing
ROTATE_INTERVAL = 20.0  # seconds
_last_rotate_time = time.time()
rotation_cooldown = 0
ROTATION_COOLDOWN_TIME = 60  # frames (about 1 second at 60fps)

# ------------------------------
# Maze definitions
# 0 empty, 1 wall, 2 treasure (spawned), 9 teleport-block in maze1
# ------------------------------
maze1 = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,1,0,1,0,1],
    [1,0,1,0,1,0,1,0,1,0,1,0,1,0,0,1,0,1,0,1],
    [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1],
    [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0,1,0,1],
    [1,0,1,0,1,0,1,0,9,0,1,0,1,0,1,0,1,1,0,1],  # 9 = red teleport block (maze1)
    [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0,1,0,1],
    [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1],
    [1,0,1,0,1,0,1,0,1,0,1,0,1,0,0,1,0,1,0,1],
    [1,0,1,0,1,0,1,0,1,0,1,0,1,1,1,1,0,1,0,1],
    [1,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,1,0,1],
    [1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,0,1],
    [1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1],
    [1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0]
]

maze2 = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1],
    [1,0,0,0,1,1,1,0,1,0,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,1,1,1,0,1],
    [1,0,1,0,1,0,1,0,0,0,0,0,0,1,0,0,0,1,0,1],
    [1,0,0,0,1,1,1,0,1,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,1,0,0,1,0,1,0,0,0,1,0,1],
    [1,0,1,1,1,0,1,1,1,1,0,1,0,1,0,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,1,1,1,1,1,0,0,0,1],
    [1,0,1,0,1,0,1,0,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,0,0,1,0,1,0,1,1,1,1,0,1,0,1,1,1,0,1],
    [1,0,0,0,1,0,1,0,0,0,0,0,0,1,0,0,0,0,0,1],
    [1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,1,0,1,0,0,0,0,1,0,1],
    [1,0,1,1,1,0,1,0,1,1,1,0,0,0,1,1,1,1,0,1],
    [1,0,1,0,0,0,1,0,1,0,1,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0]
]

mazes = [maze1, maze2]

# ------------------------------
# Coordinate helpers
# ------------------------------
def world_to_grid(x, y):
    half_size = (MAZE_SIZE * CELL_SIZE) / 2.0
    gx = int((x + half_size) // CELL_SIZE)
    gy = int((y + half_size) // CELL_SIZE)
    return gx, gy

def grid_to_world(gx, gy):
    half_size = (MAZE_SIZE * CELL_SIZE) / 2.0
    wx = (gx * CELL_SIZE) - half_size + CELL_SIZE/2.0
    wy = (gy * CELL_SIZE) - half_size + CELL_SIZE/2.0
    return wx, wy

def is_walkable_cell_val(val):
    return val in (0, 2, 9)

def is_valid_position(x, y):
    if show_maze_selection:
        return False
    half_size = (MAZE_SIZE * CELL_SIZE) / 2.0
    if abs(x) > half_size - PLAYER_RADIUS or abs(y) > half_size - PLAYER_RADIUS:
        return False
    gx, gy = world_to_grid(x, y)
    if not (0 <= gx < MAZE_SIZE and 0 <= gy < MAZE_SIZE):
        return False
    if maze[gx][gy] == 1:
        return False
    # avoid colliding with adjacent walls
    for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:
        nx, ny = gx + dx, gy + dy
        if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
            if maze[nx][ny] == 1:
                wx, wy = grid_to_world(nx, ny)
                if abs(x - wx) < (CELL_SIZE/2.0 + PLAYER_RADIUS) and abs(y - wy) < (CELL_SIZE/2.0 + PLAYER_RADIUS):
                    return False
    return True

# ------------------------------
# Maze generation / treasures / enemies spawn
# ------------------------------
def generate_maze():
    global maze, treasures, enemies, game_won
    maze = [row[:] for row in mazes[current_maze_index]]
    treasures.clear()
    enemies.clear()
    game_won = False
    # If in maze2 spawn treasures and enemies
    if current_maze_index == 1:
        for _ in range(TREASURE_COUNT):
            spawn_treasure()
        spawn_enemies()

def spawn_treasure():
    attempts = 0
    while attempts < 1000:
        x = random.randint(1, MAZE_SIZE-2)
        y = random.randint(1, MAZE_SIZE-2)
        if maze[x][y] == 0:
            maze[x][y] = 2
            treasures.append({
                'pos': (x, y),
                'type': random.choice(TREASURE_TYPES),
                'scale': random.uniform(0.8, 1.2),
                'pulse': random.uniform(0, 2*math.pi)
            })
            return
        attempts += 1

def spawn_enemy():
    for _ in range(400):
        gx = random.randint(1, MAZE_SIZE-2)
        gy = random.randint(1, MAZE_SIZE-2)
        if maze[gx][gy] == 0:
            wx, wy = grid_to_world(gx, gy)
            px, py, _ = player_pos
            if sqrt((wx-px)**2 + (wy-py)**2) > 180:
                return {
                    'pos': [wx, wy, 30.0],
                    'size': 30.0,
                    'pulse': random.random() * 2 * math.pi,
                    'path': [],
                    'target_pos': None
                }
    return None

def spawn_enemies():
    global enemies
    enemies = []
    for _ in range(ENEMY_COUNT):
        e = spawn_enemy()
        if e:
            enemies.append(e)

# ------------------------------
# Pathfinding (BFS)
# ------------------------------
def get_neighbors(x, y):
    neighbors = []
    for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE and is_walkable_cell_val(maze[nx][ny]):
            neighbors.append((nx, ny))
    return neighbors

def find_path(start_x, start_y, target_x, target_y):
    queue = [(start_x, start_y, [])]
    visited = set()
    while queue:
        x, y, path = queue.pop(0)
        if (x, y) == (target_x, target_y):
            return path
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for nx, ny in get_neighbors(x, y):
            if (nx, ny) not in visited:
                queue.append((nx, ny, path + [(nx, ny)]))
    return []

# ------------------------------
# Shooting, bullets
# ------------------------------
def fire_bullet():
    global bullets, player_bullets
    if player_bullets <= 0:
        return
    x, y, z = player_pos
    fire_angle = player_angle
    if follow_player:
        forward_offset = 35.0
        vertical_offset = 30.0
        bx = x + forward_offset * sin(radians(fire_angle))
        by = y + forward_offset * cos(radians(fire_angle))
        bz = z + vertical_offset
    else:
        bx = x + 5.0 * sin(radians(fire_angle))
        by = y + 5.0 * cos(radians(fire_angle))
        bz = z + 30.0
    bullets.append({
        'pos': [bx, by, bz],
        'angle': fire_angle,
        'distance': 0.0
    })
    player_bullets -= 1

def update_bullets():
    global bullets, score, enemies, enemy_spawn_timer
    new_bullets = []
    for b in bullets:
        angle_rad = radians(b['angle'])
        b['pos'][0] += bullet_speed * sin(angle_rad)
        b['pos'][1] += bullet_speed * cos(angle_rad)
        b['distance'] += bullet_speed
        # remove if hit wall or out of bounds
        if not is_valid_position(b['pos'][0], b['pos'][1]):
            continue
        hit = False
        for e in enemies[:]:
            ex, ey, ez = e['pos']
            bx, by, bz = b['pos']
            dx = ex - bx; dy = ey - by; dz = ez - bz
            if dx*dx + dy*dy + dz*dz < (e['size'] + 6)**2:
                try:
                    enemies.remove(e)
                except ValueError:
                    pass
                enemy_spawn_timer = 0
                score += 10
                hit = True
                break
        if not hit:
            new_bullets.append(b)
    bullets[:] = new_bullets

# ------------------------------
# Enemy updates
# ------------------------------
def update_enemies():
    global enemies, player_life, game_over, score, enemy_spawn_timer
    for e in enemies[:]:
        e['pulse'] += 0.05
        e['size'] = 25 + 5 * sin(e['pulse'])
        ex, ey, _ = e['pos']
        px, py, _ = player_pos
        gx, gy = world_to_grid(ex, ey)
        pgx, pgy = world_to_grid(px, py)
        if not e['path'] or e.get('target_pos') != (pgx, pgy):
            e['path'] = find_path(gx, gy, pgx, pgy)
            e['target_pos'] = (pgx, pgy)
        if e['path']:
            next_gx, next_gy = e['path'][0]
            tx, ty = grid_to_world(next_gx, next_gy)
            dx = tx - ex; dy = ty - ey
            dist = sqrt(dx*dx + dy*dy) if (dx != 0 or dy != 0) else 0
            if dist > 0:
                speed = 0.22 if not game_over else 0.0
                e['pos'][0] += (dx/dist) * speed
                e['pos'][1] += (dy/dist) * speed
                if dist < 4:
                    if e['path']:
                        e['path'].pop(0)
        # collision with player
        ex, ey, _ = e['pos']
        px, py, _ = player_pos
        distp = sqrt((px-ex)**2 + (py-ey)**2) if (px != ex or py != ey) else 0
        if distp < 36 and not game_over:
            player_life -= 1
            try:
                enemies.remove(e)
            except ValueError:
                pass
            enemy_spawn_timer = 0
            if player_life <= 0:
                game_over = True
    # respawn logic
    if current_maze_index == 1 and len(enemies) < ENEMY_COUNT:
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= ENEMY_SPAWN_DELAY:
            e = spawn_enemy()
            if e:
                enemies.append(e)
            enemy_spawn_timer = 0

# ------------------------------
# Drawing helpers
# ------------------------------
def draw_treasure(t):
    gx, gy = t['pos']
    wx, wy = grid_to_world(gx, gy)
    glPushMatrix()
    glTranslatef(wx, wy, 25)
    t['pulse'] += 0.05
    s = 1.0 + 0.1 * math.sin(t['pulse'])
    if t['type'] == 'sphere':
        glColor3f(0.2, 0.8, 0.8)
        gluSphere(gluNewQuadric(), 14 * s * t['scale'], 16, 16)
    elif t['type'] == 'cube':
        glColor3f(0.4, 0.2, 0.8)
        glutSolidCube(22 * s * t['scale'])
    else:
        glColor3f(0.8, 0.35, 0.5)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10 * s * t['scale'], 10 * s * t['scale'], 28 * s * t['scale'], 20, 4)
    glPopMatrix()

def draw_maze():
    half = (MAZE_SIZE * CELL_SIZE) / 2.0

    # ---- floor ----
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-half, -half, 0)
    glVertex3f(half, -half, 0)
    glVertex3f(half, half, 0)
    glVertex3f(-half, half, 0)
    glEnd()

    # ---- color-segmented walls & white traps ----
    SEGMENT_WIDTH = 6

    # Color cycle: red, blue, green, purple, pink
    palette = [
        (1.0, 0.0, 0.0),   # red
        (0.0, 0.0, 1.0),   # blue
        (0.0, 1.0, 0.0),   # green
        (0.5, 0.0, 0.5),   # purple
        (1.0, 0.4, 0.7),
        (1.0, 1.0, 0.0),  # yellow
    ]

    for i in range(MAZE_SIZE):
        # Pick the color for this entire column segment
        color_idx = (i // SEGMENT_WIDTH) % len(palette)
        col_r, col_g, col_b = palette[color_idx]

        for j in range(MAZE_SIZE):
            cell = maze[i][j]
            if cell == 1:  # wall: use the segment color
                wx, wy = grid_to_world(i, j)
                glColor3f(col_r, col_g, col_b)
                glPushMatrix()
                glTranslatef(wx, wy, CELL_SIZE/2.0)
                glutSolidCube(CELL_SIZE)
                glPopMatrix()

            elif cell == 9:  # trap/teleport: white
                wx, wy = grid_to_world(i, j)
                glColor3f(1.0, 1.0, 1.0)
                glPushMatrix()
                glTranslatef(wx, wy, CELL_SIZE/2.0)
                glutSolidCube(CELL_SIZE)
                glPopMatrix()

    # ---- treasures (maze2) ----
    for t in treasures:
        draw_treasure(t)

def draw_player_model():
    x, y, z = player_pos
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(-player_angle, 0, 0, 1)
    # torso
    glColor3f(0, 0.45, 0)
    glPushMatrix()
    glTranslatef(0, 0, 30)
    glScalef(24, 12, 36)
    glutSolidCube(1)
    glPopMatrix()
    # head
    glColor3f(0.95, 0.75, 0.6)
    glPushMatrix()
    glTranslatef(0, 0, 65)
    gluSphere(gluNewQuadric(), 9, 12, 12)
    glPopMatrix()
    # gun
    glPushMatrix()
    glTranslatef(0, 18, 40)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.25, 0.25, 0.25)
    gluCylinder(gluNewQuadric(), 3, 2, 32, 12, 4)
    glPopMatrix()
    glPopMatrix()

def draw_enemies():
    for e in enemies:
        ex, ey, ez = e['pos']
        size = e['size']
        glPushMatrix()
        glTranslatef(ex, ey, ez)
        glColor3f(1, 0, 0)
        gluSphere(gluNewQuadric(), size, 14, 14)
        glPushMatrix()
        glTranslatef(0, 0, size*0.6)
        glColor3f(0,0,0)
        gluSphere(gluNewQuadric(), size*0.4, 8, 8)
        glPopMatrix()
        glPopMatrix()

def draw_bullets():
    for b in bullets:
        x, y, z = b['pos']
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(0.06,0.06,0.06)
        gluSphere(gluNewQuadric(), 5, 8, 8)
        glPopMatrix()

# ------------------------------
# HUD / text
# ------------------------------
def draw_text(x, y, txt):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1,1,1)
    glRasterPos2f(x, y)
    for ch in txt:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_hud():
    view_mode = "First-Person" if follow_player else "Third-Person"
    maze2_status = "Completed" if maze2_won else "Not Completed"
    draw_text(10, 780, f"Score: {score}  Lives: {player_life}  Bullets: {player_bullets}  View: {view_mode}  Maze2: {maze2_status}")
    if game_over:
        draw_text(380, 400, "GAME OVER - Press R to restart")
    if game_won:
        if current_maze_index == 0:
            draw_text(350, 400, "GREAT! YOU WON MAZE 1 - Press R to restart")
        else:
            draw_text(320, 400, "YOU WON MAZE 2! Teleporting back to Maze 1...")

# ------------------------------
# Input handlers
# ------------------------------
def keyboard(key, x, y):
    global player_angle, player_pos, game_over, player_life, score, game_won, player_bullets
    global current_maze_index
    if key == b'r':
        reset_game()
        return
    if show_maze_selection:
        return
    if game_over:
        return
    move_speed = 10.0
    rotate_speed = 8.0
    if key == b'w':
        nx = player_pos[0] + move_speed * sin(radians(player_angle))
        ny = player_pos[1] + move_speed * cos(radians(player_angle))
        if is_valid_position(nx, ny):
            player_pos[0] = nx; player_pos[1] = ny
    elif key == b's':
        nx = player_pos[0] - move_speed * sin(radians(player_angle))
        ny = player_pos[1] - move_speed * cos(radians(player_angle))
        if is_valid_position(nx, ny):
            player_pos[0] = nx; player_pos[1] = ny
    elif key == b'a':
        # rotate left
        player_angle = (player_angle - rotate_speed) % 360.0
    elif key == b'd':
        # rotate right
        player_angle = (player_angle + rotate_speed) % 360.0
    glutPostRedisplay()

def special_keys(key, x, y):
    global camera_height, camera_angle, follow_player
    if follow_player:
        return
    if key == GLUT_KEY_UP:
        camera_height = min(camera_height + 10, 1500)
    elif key == GLUT_KEY_DOWN:
        camera_height = max(camera_height - 10, 150)
    elif key == GLUT_KEY_LEFT:
        camera_angle -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_angle += 5
    glutPostRedisplay()

def mouse(button, state, x, y):
    global follow_player
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        fire_bullet()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        follow_player = not follow_player
    glutPostRedisplay()

# ------------------------------
# Camera
# ------------------------------
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1000/800, 1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if follow_player:
        px, py, pz = player_pos
        back_offset = 12.0
        eye_x = px - back_offset * sin(radians(player_angle))
        eye_y = py - back_offset * cos(radians(player_angle))
        eye_z = pz + 40.0
        look_x = px + 300.0 * sin(radians(player_angle))
        look_y = py + 300.0 * cos(radians(player_angle))
        look_z = eye_z - 5.0
        gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        radius = 500.0
        eye_x = radius * sin(radians(camera_angle))
        eye_y = radius * cos(radians(camera_angle))
        gluLookAt(eye_x, eye_y, camera_height, 0, 0, 0, 0, 0, 1)

# ------------------------------
# Rotation: rotate everything 180 degrees around center
# ------------------------------
def rotate_world_180():
    global maze, treasures, enemies, bullets, player_pos, player_angle, rotation_cooldown
    # 1) rotate maze grid (180°)
    maze[:] = [row[::-1] for row in maze[::-1]]

    # 2) rotate treasures (they are stored as grid positions)
    new_treasures = []
    for t in treasures:
        gx, gy = t['pos']
        ngx = MAZE_SIZE - 1 - gx
        ngy = MAZE_SIZE - 1 - gy
        nt = dict(t)
        nt['pos'] = (ngx, ngy)
        new_treasures.append(nt)
    treasures[:] = new_treasures

    # 3) rotate enemies (world positions) and reset their path
    for e in enemies:
        ex, ey, ez = e['pos']
        e['pos'][0] = -ex
        e['pos'][1] = -ey
        e['path'] = []
        e['target_pos'] = None

    # 4) rotate bullets (world positions and angle)
    for b in bullets:
        bx, by, bz = b['pos']
        b['pos'][0] = -bx
        b['pos'][1] = -by
        b['angle'] = (b['angle'] + 180.0) % 360.0

    # 5) rotate player position and facing
    player_pos[0] = -player_pos[0]
    player_pos[1] = -player_pos[1]
    player_angle = (player_angle + 180.0) % 360.0
    
    # Set rotation cooldown to prevent immediate win condition
    rotation_cooldown = ROTATION_COOLDOWN_TIME

# ------------------------------
# Teleport & win handling
# ------------------------------
def clear_message(value):
    glutPostRedisplay()

def reset_win_state(value):
    global game_won
    game_won = False
    glutPostRedisplay()

def update_game():
    global score, game_won, game_over, player_bullets, _last_rotate_time, current_maze_index, maze2_won, rotation_cooldown
    
    # Decrement rotation cooldown if active
    if rotation_cooldown > 0:
        rotation_cooldown -= 1
        
    if show_maze_selection or game_over:
        return

    # rotate the whole world every ROTATE_INTERVAL seconds
    now = time.time()
    if now - _last_rotate_time >= ROTATE_INTERVAL:
        rotate_world_180()
        _last_rotate_time = now

    # check exit (bottom-right) - but not during rotation cooldown
    if rotation_cooldown == 0:
        half = (MAZE_SIZE * CELL_SIZE) / 2.0
        exit_x = half - CELL_SIZE
        exit_y = half - CELL_SIZE
        px, py, _ = player_pos
        if (px >= exit_x - PLAYER_RADIUS and py >= exit_y - PLAYER_RADIUS):
            # if in maze1 -> check if player has won maze2 first
            if current_maze_index == 0:
                if maze2_won:
                    game_won = True
                else:
                    # Show message that player needs to complete maze2 first
                    draw_text(300, 400, "Complete Maze 2 first to unlock this exit!")
                    glutPostRedisplay()
                    glutTimerFunc(2000, clear_message, 0)  # Clear message after 2 seconds
                return
            # if in maze2 -> win maze2 and teleport back to maze1
            elif current_maze_index == 1:
                maze2_won = True
                # Teleport back to maze1
                current_maze_index = 0
                generate_maze()
                # Place player at a random empty spot in maze1
                placed = False
                while not placed:
                    gx = random.randint(1, MAZE_SIZE-2)
                    gy = random.randint(1, MAZE_SIZE-2)
                    if maze[gx][gy] == 0:
                        wx, wy = grid_to_world(gx, gy)
                        player_pos[0], player_pos[1] = wx, wy
                        player_pos[2] = 0.0
                        placed = True
                # Show win message briefly
                game_won = True
                glutPostRedisplay()
                glutTimerFunc(3000, reset_win_state, 0)  # Reset win state after 3 seconds
                return

    # check teleport block when in maze1
    px, py, _ = player_pos
    gx, gy = world_to_grid(px, py)
    if 0 <= gx < MAZE_SIZE and 0 <= gy < MAZE_SIZE:
        if current_maze_index == 0 and maze[gx][gy] == 9:
            # teleport to maze2
            current_maze_index = 1
            generate_maze()
            # put player near maze2 start
            half = (MAZE_SIZE * CELL_SIZE) / 2.0
            player_pos[0] = -half + CELL_SIZE + PLAYER_RADIUS
            player_pos[1] = -half + CELL_SIZE + PLAYER_RADIUS
            player_pos[2] = 0.0
            return

    # Update bullets & enemies only in maze2
    if current_maze_index == 1:
        update_enemies()
        update_bullets()
    else:
        bullets.clear()
        enemies.clear()

    # treasure collection (maze2 only)
    px, py, _ = player_pos
    gx, gy = world_to_grid(px, py)
    if 0 <= gx < MAZE_SIZE and 0 <= gy < MAZE_SIZE and maze[gx][gy] == 2:
        collected = None
        for i, t in enumerate(treasures):
            if t['pos'] == (gx, gy):
                collected = t
                del treasures[i]
                break
        if collected:
            maze[gx][gy] = 0
            score += 50
            if collected['type'] == 'sphere':
                player_bullets += 5
            elif collected['type'] == 'cube':
                player_bullets += 10
            elif collected['type'] == 'cylinder':
                player_bullets += 15
            # spawn another treasure in maze2
            if current_maze_index == 1:
                spawn_treasure()

# ------------------------------
# Render / main loop
# ------------------------------
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    if show_maze_selection:
        # selection screen (unused)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        draw_text(400, 500, "Maze selection disabled - pressing 1/2 not required")
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    else:
        setup_camera()
        draw_maze()
        if not follow_player:
            draw_player_model()
        draw_enemies()
        draw_bullets()
        # HUD overlay
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        draw_hud()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    glutSwapBuffers()

def idle():
    update_game()
    glutPostRedisplay()

def init_opengl():
    glClearColor(0.08, 0.08, 0.08, 1.0)
    glEnable(GL_DEPTH_TEST)
    # Lighting is disabled (removed glEnable(GL_LIGHTING) and related lighting calls)

# ------------------------------
# Reset / start
# ------------------------------
def reset_game():
    global player_pos, player_angle, player_life, score, game_over, bullets, enemies, enemy_spawn_timer, game_won, player_bullets, _last_rotate_time, maze2_won, rotation_cooldown
    half = (MAZE_SIZE * CELL_SIZE) / 2.0
    player_pos = [-half + CELL_SIZE + PLAYER_RADIUS,
                  -half + CELL_SIZE + PLAYER_RADIUS,
                  0.0]
    player_angle = 0.0
    player_life = 5
    score = 0
    game_over = False
    game_won = False
    bullets.clear()
    enemies.clear()
    treasures.clear()
    player_bullets = 15
    enemy_spawn_timer = ENEMY_SPAWN_DELAY
    _last_rotate_time = time.time()
    maze2_won = False  # Reset the maze2 completion flag
    rotation_cooldown = 0  # Initialize rotation cooldown
    generate_maze()

# ------------------------------
# Main
# ------------------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"OpenGL Maze Game")
    init_opengl()

    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)

    reset_game()
    glutMainLoop()

if __name__ == "__main__":
    main()