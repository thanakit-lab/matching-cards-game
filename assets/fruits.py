import pygame

def create_fruit_image(color, size):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    width, height = size
    
    if color == "red":  # Apple
        pygame.draw.circle(surface, (255, 0, 0), (width//2, height//2), width//2.5)
        # Stem
        pygame.draw.rect(surface, (101, 67, 33), (width//2-5, height//4, 10, 20))
        # Leaf
        pygame.draw.ellipse(surface, (34, 139, 34), (width//2+5, height//4, 20, 15))
    elif color == "yellow":  # Banana
        points = [(width//4, height//3), (width//2, height//4), (3*width//4, height//3),
                 (3*width//4, height//2), (width//2, 2*height//3), (width//4, height//2)]
        pygame.draw.polygon(surface, (255, 255, 0), points)
    elif color == "orange":  # Orange
        pygame.draw.circle(surface, (255, 165, 0), (width//2, height//2), width//2.5)
        pygame.draw.circle(surface, (200, 140, 0), (width//2, height//2), width//2.5, 3)
    elif color == "purple":  # Grapes
        for i in range(3):
            for j in range(3):
                pygame.draw.circle(surface, (128, 0, 128), 
                                (width//3 * i + width//4, height//3 * j + height//4), 
                                width//8)
    elif color == "green":  # Watermelon
        pygame.draw.circle(surface, (34, 139, 34), (width//2, height//2), width//2.5)
        smaller = pygame.Surface((width//2, height//2), pygame.SRCALPHA)
        pygame.draw.circle(smaller, (255, 100, 100), (width//4, height//4), width//4)
        surface.blit(smaller, (width//4, height//4))
    elif color == "pink":  # Strawberry
        pygame.draw.polygon(surface, (255, 0, 0), 
                          [(width//2, height//5), (3*width//4, 2*height//3), 
                           (width//4, 2*height//3)])
        # Add seeds
        for i in range(5):
            for j in range(5):
                pygame.draw.circle(surface, (255, 255, 0), 
                                (width//3 + i*10, height//3 + j*10), 2)
    elif color == "brown":  # Coconut
        pygame.draw.circle(surface, (150, 75, 0), (width//2, height//2), width//2.5)
        pygame.draw.circle(surface, (101, 67, 33), (width//2, height//2), width//2.5, 3)
    elif color == "white":  # Pear
        pygame.draw.ellipse(surface, (170, 220, 100), (width//4, height//4, width//2, 2*height//3))
        pygame.draw.rect(surface, (101, 67, 33), (width//2-5, height//4, 10, 20))
    
    return surface
