import pygame
import random

# 初始化 Pygame
pygame.init()

# 颜色定义（移到最前面）
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# 定义方块形状
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

# 定义方块颜色
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# 游戏设置
BLOCK_SIZE = 30  # 每个方块的大小
GRID_WIDTH = 10  # 游戏区域宽度（以方块数计）
GRID_HEIGHT = 20  # 游戏区域高度（以方块数计）
SCORE_PER_LINE = [100, 300, 500, 800]  # 消除1/2/3/4行的分数
LEVEL_UP_SCORE = 1000  # 每1000分升一级
MIN_FALL_SPEED = 50  # 最快下落速度（毫秒）
GAME_START = 0
GAME_PLAYING = 1
GAME_PAUSED = 2
GAME_OVER = 3

# 设置游戏窗口
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)  # 游戏区域加上右侧信息区
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('俄罗斯方块')

class Tetromino:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = SHAPE_COLORS[self.shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    
    def rotate(self):
        # 矩阵转置后反转每一行，实现顺时针旋转
        self.shape = [[self.shape[y][x] for y in range(len(self.shape)-1, -1, -1)]
                     for x in range(len(self.shape[0]))]
        
    def copy(self):
        new_piece = Tetromino()
        new_piece.shape_idx = self.shape_idx
        new_piece.shape = self.shape
        new_piece.color = self.color
        new_piece.x = self.x
        new_piece.y = self.y
        return new_piece

def check_collision(piece, grid, dx=0, dy=0):
    future_x = piece.x + dx
    future_y = piece.y + dy
    
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                if (future_x + x < 0 or  # 检查左边界
                    future_x + x >= GRID_WIDTH or  # 检查右边界
                    future_y + y >= GRID_HEIGHT or  # 检查底边界
                    (future_y + y >= 0 and grid[future_y + y][future_x + x])):  # 检查碰撞
                    return True
    return False

def lock_piece(piece, grid):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                grid[piece.y + y][piece.x + x] = piece.color
    return check_full_lines(grid)

def check_full_lines(grid):
    lines_cleared = 0
    for i in range(len(grid)-1, -1, -1):
        if all(cell != 0 for cell in grid[i]):
            del grid[i]
            grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            lines_cleared += 1
    return lines_cleared

# 创建游戏网格
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_piece = None

# 游戏主循环
running = True
clock = pygame.time.Clock()
fall_time = 0
fall_speed = 200  # 初始下落速度
current_piece = Tetromino()

# 添加字体
pygame.font.init()
font = pygame.font.Font(None, 36)

# 在主循环前添加游戏状态变量
score = 0
level = 1
lines_cleared = 0
next_piece = Tetromino()
game_state = GAME_START

# 添加重置游戏函数
def reset_game():
    global grid, current_piece, next_piece, score, level, lines_cleared, fall_speed
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_piece = Tetromino()
    next_piece = Tetromino()
    score = 0
    level = 1
    lines_cleared = 0
    fall_speed = 200

while running:
    fall_time += clock.get_rawtime()
    clock.tick(60)
    
    if game_state == GAME_PLAYING:
        # 根据等级调整下落速度
        fall_speed = max(MIN_FALL_SPEED, 200 - (level - 1) * 20)

        # 自动下落
        if fall_time >= fall_speed:
            if not check_collision(current_piece, grid, dy=1):
                current_piece.move(0, 1)
            else:
                lines = lock_piece(current_piece, grid)
                if lines > 0:
                    score += SCORE_PER_LINE[lines - 1]
                    lines_cleared += lines
                    level = min(10, lines_cleared // 10 + 1)
                
                current_piece = next_piece
                next_piece = Tetromino()
                if check_collision(current_piece, grid):
                    game_state = GAME_OVER
            fall_time = 0

    # 事件处理部分
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == GAME_START:
                if event.key == pygame.K_SPACE:
                    game_state = GAME_PLAYING
                    reset_game()
            elif game_state == GAME_PLAYING:
                if event.key == pygame.K_p:  # 暂停
                    game_state = GAME_PAUSED
                    print("Game Paused")  # 添加调试输出
                elif event.key == pygame.K_LEFT:
                    if not check_collision(current_piece, grid, dx=-1):
                        current_piece.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    if not check_collision(current_piece, grid, dx=1):
                        current_piece.move(1, 0)
                elif event.key == pygame.K_DOWN:
                    if not check_collision(current_piece, grid, dy=1):
                        current_piece.move(0, 1)
                        score += 1
                elif event.key == pygame.K_UP:
                    original_shape = current_piece.shape
                    current_piece.rotate()
                    if check_collision(current_piece, grid):
                        current_piece.shape = original_shape
                elif event.key == pygame.K_SPACE:  # 快速下落
                    while not check_collision(current_piece, grid, dy=1):
                        current_piece.move(0, 1)
                        score += 2
            elif game_state == GAME_PAUSED:
                if event.key == pygame.K_p:  # 继续游戏
                    game_state = GAME_PLAYING
                    print("Game Resumed")  # 添加调试输出
            elif game_state == GAME_OVER:
                if event.key == pygame.K_SPACE:  # 重新开始
                    game_state = GAME_PLAYING
                    reset_game()

    screen.fill(BLACK)

    if game_state == GAME_START:
        # 绘制开始界面
        title = font.render('TETRIS', True, WHITE)
        start_text = font.render('Press SPACE to Start', True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2))

    elif game_state == GAME_PLAYING:
        # 游戏逻辑和绘制
        # 绘制网格线
        for i in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, WHITE, 
                           (i * BLOCK_SIZE, 0), 
                           (i * BLOCK_SIZE, SCREEN_HEIGHT))
        for i in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, WHITE,
                           (0, i * BLOCK_SIZE),
                           (GRID_WIDTH * BLOCK_SIZE, i * BLOCK_SIZE))

        # 绘制已固定的方块
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, cell,
                                   (x * BLOCK_SIZE,
                                    y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # 绘制当前方块
        for y, row in enumerate(current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, current_piece.color,
                                   (current_piece.x * BLOCK_SIZE + x * BLOCK_SIZE,
                                    current_piece.y * BLOCK_SIZE + y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # 绘制右侧信息区域
        info_x = (GRID_WIDTH + 1) * BLOCK_SIZE
        
        # 显示分数
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (info_x, 20))
        
        # 显示等级
        level_text = font.render(f'Level: {level}', True, WHITE)
        screen.blit(level_text, (info_x, 60))
        
        # 显示已消除行数
        lines_text = font.render(f'Lines: {lines_cleared}', True, WHITE)
        screen.blit(lines_text, (info_x, 100))
        
        # 显示下一个方块
        next_text = font.render('Next:', True, WHITE)
        screen.blit(next_text, (info_x, 160))
        
        # 绘制下一个方块预览
        for y, row in enumerate(next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, next_piece.color,
                                   (info_x + x * BLOCK_SIZE,
                                    220 + y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    elif game_state == GAME_PAUSED:
        # 绘制暂停界面
        pause_text = font.render('PAUSED', True, WHITE)
        continue_text = font.render('Press P to Continue', True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2))

    elif game_state == GAME_OVER:
        # 绘制游戏结束界面
        game_over_text = font.render('GAME OVER', True, WHITE)
        final_score = font.render(f'Final Score: {score}', True, WHITE)
        restart_text = font.render('Press SPACE to Restart', True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT*2//3))

    pygame.display.flip()

pygame.quit()
