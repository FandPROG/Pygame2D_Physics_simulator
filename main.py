import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Physics Engine")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

COLORS = [RED, BLUE, GREEN, YELLOW]
CC_idx = 0

GRAVITY = 0.5
FPS = 60
gravity_on = True

class Ball:
    def __init__(self, x, y, vx, vy, mass=1.0, color=RED):
        self.r = 20
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.color = color
        self.font = pygame.font.SysFont(None, 24)
        
    def update(self):
        if gravity_on:
            self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        
        # 벽에 튕기게 하기
        if self.x - self.r < 0 or self.x + self.r > WIDTH:
            self.vx *= -1
            if self.x - self.r < 0:
                self.x = self.r
            else:
                self.x = WIDTH - self.r
        
        if self.y - self.r < 0 or self.y + self.r > HEIGHT:
            self.vy *= -1
            if self.y - self.r < 0:
                self.y = self.r
            else:
                self.y = HEIGHT - self.r

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)
        # 질량 표시
        mass_text = self.font.render(f'{self.mass:.1f}', True, BLACK)
        text_rect = mass_text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(mass_text, text_rect)

    def check_collision(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.hypot(dx, dy)
        
        if distance < self.r + other.r:
            angle = math.atan2(dy, dx)
            
            # 속도 벡터 계산
            v1 = (self.vx * math.cos(angle) + self.vy * math.sin(angle))
            v2 = (other.vx * math.cos(angle) + other.vy * math.sin(angle))
            
            # 완전 탄성 충돌 = 운동량과 운동에너지 모두 보존 -> 연립한 식
            m1, m2 = self.mass, other.mass
            v1_final = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
            v2_final = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)

            # 다시 x, y 성분으로 나누기
            self.vx = v1_final * math.cos(angle) - v1 * math.sin(angle)
            self.vy = v1_final * math.sin(angle) + v1 * math.cos(angle)
            other.vx = v2_final * math.cos(angle) - v2 * math.sin(angle)
            other.vy = v2_final * math.sin(angle) + v2 * math.cos(angle)
            
            # 공 위치 조정 (충돌 후 겹침 방지)
            ov = (self.r + other.r - distance + 1) / 2
            self.x -= ov * math.cos(angle)
            self.y -= ov * math.sin(angle)
            other.x += ov * math.cos(angle)
            other.y += ov * math.sin(angle)

balls = []

initial_speed = 5
vx, vy = 0, 0
mass = 1.0
direction_text = "Stationary"

# 시뮬레이션
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 공 생성 로직
            x, y = pygame.mouse.get_pos()
            ball = Ball(x, y, vx, vy, mass, COLORS[CC_idx])
            balls.append(ball)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                vx = -10
                vy = 0
                direction_text = "Left"
            if event.key == pygame.K_RIGHT:
                vx = 10
                vy = 0
                direction_text = "Right"
            if event.key == pygame.K_UP:
                vy = -10
                vx = 0
                direction_text = "Up"
            if event.key == pygame.K_DOWN:
                vy = 10
                vx = 0
                direction_text = "Down"
            # M = 질량 증가, N = 질량 감소
            if event.key == pygame.K_m:
                mass += 0.1
            if event.key == pygame.K_n:
                mass = max(0.1, mass - 0.1)
            # G = 중력 켜고 끄기
            if event.key == pygame.K_g:
                gravity_on = not gravity_on
            # Space = 화면 중앙에 공 생성
            if event.key == pygame.K_SPACE:
                ball = Ball(WIDTH // 2, HEIGHT // 2, vx, vy, mass, COLORS[CC_idx])
                balls.append(ball)
            # C = 색상 변경
            if event.key == pygame.K_c:
                CC_idx = (CC_idx + 1) % len(COLORS)
            # E = 모든 공 제거
            if event.key == pygame.K_e:
                balls.clear()

    screen.fill(WHITE)

    for ball in balls:
        ball.update()
        ball.draw(screen)
    
    # 충돌 체크
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            balls[i].check_collision(balls[j])

    # 질량 표시
    font = pygame.font.SysFont(None, 36)
    mass_text = font.render(f'Mass: {mass:.1f}', True, BLACK)
    screen.blit(mass_text, (10, 10))

    # 방향 표시
    direction_font = pygame.font.SysFont(None, 36)
    direction_text_surf = direction_font.render(f'Direction: {direction_text}', True, BLACK)
    screen.blit(direction_text_surf, (WIDTH - 200, 10))

    # 중력 상태 표시
    G_stat = "Gravity On" if gravity_on else "Gravity Off"
    G_font = pygame.font.SysFont(None, 36)
    G_text_surf = G_font.render(f'Gravity: {G_stat}', True, BLACK)
    text_rect = G_text_surf.get_rect(center=(WIDTH // 2, 30))
    screen.blit(G_text_surf, text_rect)

    # 색상 표시
    color_name = COLORS[CC_idx]
    color_text_surf = font.render(f'Color: {color_name}', True, BLACK)
    screen.blit(color_text_surf, (10, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(FPS)
