import random
from constants import SHAPES, COLORS

class Piece:
    def __init__(self, shape_name=None):
        if shape_name is None:
            shape_name = random.choice(list(SHAPES.keys()))
        self.shape_name = shape_name
        self.shape = SHAPES[shape_name]
        self.color = COLORS[shape_name]
        self.rotation = 0
        self.x = 3  # Starting x position (center of grid)
        self.y = 0  # Starting y position (top of grid)

    def get_positions(self):
        positions = []
        shape_matrix = self.shape[self.rotation]
        for i in range(4):
            for j in range(4):
                if shape_matrix[i][j]:
                    positions.append((self.x + j, self.y + i))
        return positions

    def rotate(self, clockwise=True):
        if clockwise:
            self.rotation = (self.rotation + 1) % len(self.shape)
        else:
            self.rotation = (self.rotation - 1) % len(self.shape)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy