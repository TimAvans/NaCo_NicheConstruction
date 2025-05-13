import mesa
from organism import Organism
import numpy as np
from tile import Tile

'''

'''
class NicheModel(mesa.Model):    
    def __init__(self, n_agents = 5, width = 25, height = 25, max_resource = 5.0, mutation_rate= 0.01):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, torus=True)
        self.width = width
        self.height = height
        self.n_agents = n_agents
        self.space = self.grid
        self.mutation_rate = mutation_rate
        self.max_resource = max_resource
        self.environment = np.full((width, height), 2.0)  
        self.init_tiles()
        self.init_organisms()
        
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "MeanEnergy": lambda m: np.mean([a.energy for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
                "MeanResource": lambda m: np.mean(m.environment) if m.environment.size > 0 else 0,
                "AvgCooperation": lambda m: np.mean([a.dna["cooperation"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
                "AvgMetabolism": lambda m: np.mean([a.dna["metabolism"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
                "AvgConsumption": lambda m: np.mean([a.dna["consumption"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
                "OrganismCount": lambda m: sum(isinstance(a, Organism) for a in m.agents),
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
                self.space.place_agent(tile, (x, y))
                self.agents.add(tile)

    def step(self):
        if len(self.agents) == 0:
            return
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)