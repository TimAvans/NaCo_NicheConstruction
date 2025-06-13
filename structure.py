import mesa

class Structure(mesa.Agent):
    '''
    This agent occupies a tile and makes sure there doesnt grow any resource in the tile
    '''
    def __init__(self, model, lifespan = 5):
        super().__init__(model)
        self.lifespan = lifespan
    
    def step(self):
        '''
        Reduce the lifespan of the structure each step
        This makes sure we dont oversaturate the grid with structures
        '''
        self.lifespan-=1
        if self.lifespan <= 0:
            self.model.space.remove_agent(self)
            self.model.agents.remove(self)