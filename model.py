import mesa
from organism import Organism
import numpy as np
from tile import Tile
from structure import Structure


'''

'''
class NicheModel(mesa.Model):    
    def __init__(self, n_agents = 5, width = 25, height = 25, max_resource = 5.0, recharge_rate = 0.25, mutation_rate= 0.05, mutation_scale = 0.02, ):
        super().__init__()
        self.step_count = 0
        self.grid = mesa.space.MultiGrid(width, height, torus=True)
        self.width = width
        self.height = height
        self.n_agents = n_agents
        self.space = self.grid
        self.mutation_rate = mutation_rate
        self.mutation_scale = mutation_scale
        self.max_resource = max_resource
        self.recharge_rate = recharge_rate
        self.environment = np.full((width, height), max_resource)  
        self.init_tiles()
        self.init_organisms()

        self.datacollector = mesa.DataCollector(
            model_reporters={
            "OrganismCount": lambda m: sum(isinstance(a, Organism) for a in m.agents),
            "MeanEnergy": lambda m: np.mean([a.energy for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanCooperation": lambda m: np.mean([a.dna["cooperate"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanConsumption": lambda m: np.mean([a.dna["consume"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanBuilder": lambda m: np.mean([a.dna["build"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanReproduction": lambda m: np.mean([a.dna["reproduce"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanMovement": lambda m: np.mean([a.dna["move"] for a in m.agents if isinstance(a, Organism)]) if any(isinstance(a, Organism) for a in m.agents) else 0,
            "MeanResource": lambda m: np.mean(m.environment),
            "StructureCount": lambda m: sum(isinstance(a, Structure) for a in m.agents),
            "Cooperators": lambda m: sum(1 for a in m.agents if isinstance(a, Organism) and a.dna["cooperate"] >= 0.15),
            "NonCooperators": lambda m: sum(1 for a in m.agents if isinstance(a, Organism) and a.dna["cooperate"] < 0.15),            
            }
        )

    def init_organisms(self):
        for _ in range(self.n_agents):
            agent = Organism(self)
            while True:
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                if not any(isinstance(a, Organism) for a in self.space.get_cell_list_contents((x, y))):
                    self.space.place_agent(agent, (x, y))
                    break
            self.agents.add(agent)

    def init_tiles(self):
        for x in range(self.width):
            for y in range(self.height):
                contents = self.space.get_cell_list_contents((x, y))
                if not any(isinstance(a, Tile) for a in contents):
                    tile = Tile(self)
                    self.space.place_agent(tile, (x, y))
                    self.agents.add(tile)

    '''
    TODO: Make a function which mixes the agents (location wise) as to show how much local environment matters
    '''
    def mix_organisms(self):
        #Get all organisms
        organisms = [agent for agent in self.agents if isinstance(agent, Organism)]
        #Get all possible positions on the grid
        all_positions = [(x, y) for x in range(self.space.width) for y in range(self.space.height)]
        #Shuffle and assign new positions to each organism
        self.random.shuffle(all_positions)
        for agent, new_pos in zip(organisms, all_positions):
            self.space.move_agent(agent, new_pos)
        print("Mix all organism positions")

    def step(self):
        #TODO: Extremely low as to not trigger until we want to make a baseline
        if self.step_count == -1:
            self.mix_organisms()

        self.step_count+=1

        #TODO: Increase regen of adjacent tiles to structures?
        for x in range(self.space.width):
            for y in range(self.space.height):
                if not any(isinstance(a, Structure) for a in self.space.get_cell_list_contents((x, y))):
                    self.environment[x][y] = min(self.environment[x][y] + self.recharge_rate, self.max_resource)

        if len(self.agents) == 0:
            return
        
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)