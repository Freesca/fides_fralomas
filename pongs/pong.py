import pygame
import sys

# Inizializzazione di pygame
pygame.init()

# Costanti del gioco
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BALL_SIZE = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_SPEED = 6
PADDLE_SPEED = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Configurazione dello schermo
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong")

# Posizioni iniziali
ball_x, ball_y = SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2
ball_dx, ball_dy = BALL_SPEED, 0
left_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
right_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2

# Loop del gioco
clock = pygame.time.Clock()

left_score = 0
right_score = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Tasti premuti
    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    # Movimento barra sinistra
    if keys[pygame.K_w] and left_paddle_y > 0:
        left_paddle_y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
        left_paddle_y += PADDLE_SPEED

    # Movimento barra destra
    if keys[pygame.K_UP] and right_paddle_y > 0:
        right_paddle_y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
        right_paddle_y += PADDLE_SPEED

    # Aggiornamento posizione pallina
    ball_x += ball_dx
    ball_y += ball_dy

    # Collisione con la parte superiore e inferiore
    if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
        ball_dy = -ball_dy

    # Collisione con le barre
    if ball_x <= PADDLE_WIDTH and left_paddle_y <= ball_y <= left_paddle_y + PADDLE_HEIGHT:
        ball_dx = -ball_dx
        # Calcola la variazione della direzione verticale
        offset = (ball_y - left_paddle_y) - PADDLE_HEIGHT // 2
        ball_dy = offset // (PADDLE_HEIGHT / (2 * BALL_SPEED))  # Normalizza la variazione

    if ball_x >= SCREEN_WIDTH - PADDLE_WIDTH - BALL_SIZE and right_paddle_y <= ball_y <= right_paddle_y + PADDLE_HEIGHT:
        ball_dx = -ball_dx
        # Calcola la variazione della direzione verticale
        offset = (ball_y - right_paddle_y) - PADDLE_HEIGHT // 2
        ball_dy = offset // (PADDLE_HEIGHT / (2 * BALL_SPEED))  # Normalizza la variazione


    # Ripristino posizione pallina se esce dai bordi
    if ball_x < 0 or ball_x > SCREEN_WIDTH:
        if ball_x < 0:
            right_score += 1
        else:
            left_score += 1
        ball_x, ball_y = SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2
        ball_dy = 0
        left_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        right_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        screen.fill(BLACK)
        #disegno punteggio
        font = pygame.font.Font(None, 74)
        text = font.render(str(left_score) + " - " + str(right_score), True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 50))
        pygame.draw.rect(screen, WHITE, (10, left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - PADDLE_WIDTH - 10, right_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.ellipse(screen, WHITE, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        pygame.display.flip()
        clock.tick(60)
        pygame.time.wait(1000)  # Aspetta 1 secondo
        continue

    # Disegno dello schermo
    screen.fill(BLACK)
    #disegno punteggio
    font = pygame.font.Font(None, 74)
    text = font.render(str(left_score) + " - " + str(right_score), True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 50))
    pygame.draw.rect(screen, WHITE, (10, left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - PADDLE_WIDTH - 10, right_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.ellipse(screen, WHITE, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

    pygame.display.flip()
    clock.tick(60)