import mesa
from organism import Organism
import numpy as np
from tile import Tile
from structure import Structure

'''

'''
class NicheModel(mesa.Model):    
    def __init__(self, n_agents = 5, width = 25, height = 25, max_resource = 5.0, recharge_rate = 0.25, mutation_rate= 0.01, cooperation_factor=0.05):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, torus=True)
        self.width = width
        self.height = height
        self.n_agents = n_agents
        self.space = self.grid
        self.mutation_rate = mutation_rate
        self.max_resource = max_resource
        self.recharge_rate = recharge_rate
        self.cooperation_factor = cooperation_factor
        self.environment = np.full((width, height), max_resource)  
        #self.init_tiles()
        
        self.datacollector = mesa.DataCollector(
            model_reporters={
            "OrganismCount": lambda m: sum(isinstance(a, Organism) for a in m.agents),
            "MeanEnergy": lambda m: np.mean([a.energy for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanCooperation": lambda m: np.mean([a.dna["cooperation"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanConsumption": lambda m: np.mean([a.dna["consumption"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanMetabolism": lambda m: np.mean([a.dna["metabolism"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanBuilder": lambda m: np.mean([a.dna["builder"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanResource": lambda m: np.mean(m.environment),
            "StructureCount": lambda m: sum(isinstance(a, Structure) for a in m.agents),
            }
        )

    def init_organisms(self):
        for _ in range(self.n_agents):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            agent = Organism(self)
            self.space.place_agent(agent, (x, y))
            self.agents.add(agent)

    def init_tiles(self):
        for x in range(self.width):
            for y in range(self.height):
                contents = self.space.get_cell_list_contents((x, y))
                if any(isinstance(a, Tile) for a in contents):
                    continue 
                tile = Tile((x, y), self)
                self.space.remove_agent(tile)
                self.space.place_agent(tile, (x, y))
                self.agents.add(tile)

    def step(self):
        #TODO: Remove regen of adjacent tiles to structures
        for x in range(self.space.width):
            for y in range(self.space.height):
                if not any(isinstance(a, Structure) for a in self.space.get_cell_list_contents((x, y))):
                    self.environment[x][y] = min(self.environment[x][y] + self.recharge_rate, self.max_resource)

        if len(self.agents) == 0:
            return
        
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)