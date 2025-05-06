import mesa

class Organism(mesa.Agent):
    def __init__(self, model, strategy = "cooperator", energy = 5):
        super().__init__(model)
        self.strategy = strategy
        self.energy = energy
    
    def step(self):
        dead = self.move()
        if dead >= 0:
            self.consume()
            self.reproduce()

    def move(self):
        self.energy -= 0.5
        if  self.energy <= 0:
            self.die()
            return -1
        
        possibilities = self.model.space.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possibilities)
        self.model.space.move_agent(self, new_position)
        return 0
    
    def die(self):
        self.model.space.remove_agent(self)
        self.model.agents.remove(self)
        print(f"Agent with id {self.unique_id} died due to energy level")

    def modify_environment(self):
        return -1

    def consume(self):
        x, y = self.pos
        current_amount = self.model.environment[x][y]
        consumed_amount = min(current_amount, 1.0)
        self.energy += consumed_amount
        self.model.environment[x][y] -= consumed_amount
        print(f"Agent with id {self.unique_id} consumed at location [{x}, {y}]")

    def reproduce(self):
        if self.energy >= 10.0:
            self.energy /= 2
            if self.random.random() < self.model.mutation_rate:
                new_strategy = "freeloader" if self.strategy == "cooperator" else "cooperator"
            else:
                new_strategy = self.strategy
            child = Organism(self.model, strategy=new_strategy, energy=self.energy)
            self.model.space.place_agent(child, self.pos)
            self.model.agents.add(child)