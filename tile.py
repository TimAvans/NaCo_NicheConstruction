import mesa

class Tile(mesa.Agent):
    def __init__(self, pos, model):
        super().__init__(model)
        self.pos = pos

    def step(self):
        pass