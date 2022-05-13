import pygame
import pygame.gfxdraw

from control import WSADController, MouseController, AIController
from gui import GUI
from layout import generate_grid
from score import Score
from snake.algorithm import RandomEdgeAlgorithm, ShortestPathAlgorithm

GRID_WIDTH = 10
GRID_HEIGHT = 20
EDGE_LENGTH = 40

if __name__ == "__main__":

    graph, layout = generate_grid(GRID_WIDTH, GRID_HEIGHT, EDGE_LENGTH)
    gui = GUI(graph, layout)
    # controller = WSADController(graph, layout)
    # controller = MouseController(graph, layout)
    # controller = AIController(graph, RandomEdgeAlgorithm(graph))
    controller = AIController(graph, ShortestPathAlgorithm(graph))

    pygame.init()
    clock = pygame.time.Clock()
    done = False
    graph.generate_apple_if_missing()
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.VIDEORESIZE:
                gui.on_window_resize(event)
            controller.handle_event(event)
        controller.update()
        controller.move_snake()
        graph.generate_apple_if_missing()
        gui.draw()

        clock.tick(10)

    pygame.quit()
