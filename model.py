import mesa
from organism import Organism
import numpy as np

'''

'''
class NicheModel(mesa.Model):    
    def __init__(self, n_agents = 50, width = 20, height = 20, mutation_rate= 0.01):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, torus=True)
        self.n_agents = n_agents
        self.space = self.grid
        self.mutation_rate = mutation_rate

        self.environment = np.full((width, height), 2.0)  # Initial resources
        for _ in range(self.n_agents):
            strategy = self.random.choice(["cooperator", "freeloader"])
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            agent = Organism(self, strategy=strategy)
            self.space.place_agent(agent, (x, y))
            self.agents.add(agent)
        
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Cooperators": lambda m: sum(1 for a in m.agents if a.strategy == "cooperator"),
                "Freeloaders": lambda m: sum(1 for a in m.agents if a.strategy == "freeloader"),
                "MeanEnergy": lambda m: np.mean([a.energy for a in m.agents]) if m.agents else 0,
                "MeanResource": lambda m: np.mean(m.environment) if m.environment.size > 0 else 0,
            }
        )

    def step(self):
        if len(self.agents) == 0:
            return
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)