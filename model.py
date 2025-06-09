import mesa
from organism import OrganismA, OrganismB, Organism
import numpy as np
from tile import Tile
from structure import Structure



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
        self.dead_ages = []
        self.init_tiles()
        self.init_organisms()

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "OrganismCountA": lambda m: sum(isinstance(a, OrganismA) for a in m.agents),
                "MeanEnergyA": lambda m: np.mean([a.energy for a in m.agents if isinstance(a, OrganismA)]) if any(isinstance(a, OrganismA) for a in m.agents) else 0,
                "MeanCooperationA": lambda m: np.mean([a.dna["cooperate"] for a in m.agents if isinstance(a, OrganismA)]) if any(isinstance(a, OrganismA) for a in m.agents) else 0,
                "MeanConsumptionA": lambda m: np.mean([a.dna["consume"] for a in m.agents if isinstance(a, OrganismA)]) if any(isinstance(a, OrganismA) for a in m.agents) else 0,
                "MeanBuilderA": lambda m: np.mean([a.dna["build"] for a in m.agents if isinstance(a, OrganismA)]) if any(isinstance(a, OrganismA) for a in m.agents) else 0,
                "MeanReproductionA": lambda m: np.mean([a.dna["reproduce"] for a in m.agents if isinstance(a, OrganismA)]) if any(isinstance(a, OrganismA) for a in m.agents) else 0,
                "MeanMovementA": lambda m: np.mean([a.dna["move"] for a in m.agents if isinstance(a, OrganismA)]) if any(isinstance(a, OrganismA) for a in m.agents) else 0,
                "MeanResourceA": lambda m: np.mean(m.environment),
                "AvgLifespanA": lambda m: np.mean(m.dead_ages) if m.dead_ages else 0,
                "StructureCountA": lambda m: sum(isinstance(a, Structure) for a in m.agents),
                "CooperatorsA": lambda m: sum(1 for a in m.agents if isinstance(a, OrganismA) and a.dna["cooperate"] >= 0.15),
                "NonCooperatorsA": lambda m: sum(1 for a in m.agents if isinstance(a, OrganismA) and a.dna["cooperate"] < 0.15),   

                "OrganismCountB": lambda m: sum(isinstance(a, OrganismB) for a in m.agents),
                "MeanEnergyB": lambda m: np.mean([a.energy for a in m.agents if isinstance(a, OrganismB)]) if any(isinstance(a, OrganismB) for a in m.agents) else 0,
                "MeanCooperationB": lambda m: np.mean([a.dna["cooperate"] for a in m.agents if isinstance(a, OrganismB)]) if any(isinstance(a, OrganismB) for a in m.agents) else 0,
                "MeanConsumptionB": lambda m: np.mean([a.dna["consume"] for a in m.agents if isinstance(a, OrganismB)]) if any(isinstance(a, OrganismB) for a in m.agents) else 0,
                "MeanBuilderB": lambda m: np.mean([a.dna["build"] for a in m.agents if isinstance(a, OrganismB)]) if any(isinstance(a, OrganismB) for a in m.agents) else 0,
                "MeanReproductionB": lambda m: np.mean([a.dna["reproduce"] for a in m.agents if isinstance(a, OrganismB)]) if any(isinstance(a, OrganismB) for a in m.agents) else 0,
                "MeanMovementB": lambda m: np.mean([a.dna["move"] for a in m.agents if isinstance(a, OrganismB)]) if any(isinstance(a, OrganismB) for a in m.agents) else 0,
                "MeanResourceB": lambda m: np.mean(m.environment),
                "AvgLifespanB": lambda m: np.mean(m.dead_ages) if m.dead_ages else 0,
                "StructureCountB": lambda m: sum(isinstance(a, Structure) for a in m.agents),
                "CooperatorsB": lambda m: sum(1 for a in m.agents if isinstance(a, OrganismB) and a.dna["cooperate"] >= 0.15),
                "NonCooperatorsB": lambda m: sum(1 for a in m.agents if isinstance(a, OrganismB) and a.dna["cooperate"] < 0.15),   

                "TotalPopulation": lambda m: sum(isinstance(a, (OrganismA, OrganismB)) for a in m.agents)         
            }
        )
    def init_organisms(self):
        for i in range(self.n_agents):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            agent_type = OrganismA if i < self.n_agents // 2 else OrganismB
            agent = agent_type(self)
            self.space.place_agent(agent, (x, y))
            self.agents.add(agent)    

    def init_organisms(self):
        for i in range(self.n_agents):
            agent_type = OrganismA if i < self.n_agents // 2 else OrganismB
            agent = agent_type(self)
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