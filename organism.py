import mesa
import numpy as np

class Organism(mesa.Agent):
    def __init__(self, model, energy = 5, dna = None):
        super().__init__(model)
        self.energy = energy
        dna_values = np.random.dirichlet([1, 1, 1])
        self.dna = dna or {
            "cooperation": dna_values[0],
            "consumption": dna_values[1],
            "metabolism": dna_values[2],
        }
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

    def mutate_dna(self):
        new_dna = {
            k: max(0.001, v + self.random.gauss(0, 0.02)) for k, v in self.dna.items()
        }
        total = sum(new_dna.values())
        return {k: v / total for k, v in new_dna.items()}


    def reproduce(self):
        if self.energy >= 10.0:
            self.energy /= 2
            if self.random.random() < self.model.mutation_rate:
                child_dna = self.mutate_dna()
            else:
                child_dna = dict(self.dna)

            child = Organism(self.model, energy=self.energy, dna=child_dna)
            self.model.space.place_agent(child, self.pos)
            self.model.agents.add(child)