import mesa
import numpy as np
from structure import Structure
'''
TODO: Need building to reproduce?!
'''
class Organism(mesa.Agent):
    def __init__(self, model, energy = 5, dna = None):
        super().__init__(model)
        self.energy = energy
        dna_values = np.random.dirichlet([1, 1, 1, 1])
        self.dna = dna or {
            "cooperation": dna_values[0],
            "consumption": dna_values[1],
            "metabolism": dna_values[2],
            "builder": dna_values[3],
        }
        self.built = False

    def step(self):
        self.energy -= self.dna["metabolism"]
        if self.energy <= 0:
            self.die()
            return

        self.move()
        self.consume()
        self.modify_environment()
        #TODO: Remove repoduction because we reproduce only the best x amount of organisms
        if self.built:
            self.reproduce()

    #TODO: Cannot move away from structure
    def move(self):
        possibilities = self.model.space.get_neighborhood(self.pos, moore=True, include_center=False)
        possibilities = list(possibilities)
        self.random.shuffle(possibilities)

        for new_pos in possibilities:
            contents = self.model.space.get_cell_list_contents(new_pos)
            if not any(isinstance(a, Organism) for a in contents):
                self.model.space.move_agent(self, new_pos)
                return 
    
    #TODO: Organism needs a structure to survive
    def die(self):
        self.model.space.remove_agent(self)
        self.model.agents.remove(self)
        print(f"Agent with id {self.unique_id} died due to energy level")

    def modify_environment(self):
        if self.built or self.energy <= 6:
            return
        
        chance = self.dna["builder"]
        if self.random.random() < chance:
            x, y = self.pos
            contents = self.model.space.get_cell_list_contents((x, y))
            if not any(isinstance(a, Structure) for a in contents):
                self.energy -= 3
                struct = Structure(self.model, (x,y))
                self.model.space.place_agent(struct, (x, y))
                self.model.agents.add(struct)
                self.built = True
                print(f"Agent with id {self.unique_id} build a structure at [{x}, {y}]")

    def consume(self):
        x, y = self.pos
        current_amount = self.model.environment[x][y]
        consumption_capacity = self.dna["consumption"] * self.model.max_resource
        consumed_amount = min(current_amount, consumption_capacity)
        self.energy += consumed_amount
        self.model.environment[x][y] -= consumed_amount
        print(f"Agent with id {self.unique_id} consumed at location [{x}, {y}]")

        repair = self.dna["cooperation"] * self.model.cooperation_factor
        self.model.environment[x][y] = min(self.model.environment[x][y] + repair, self.model.max_resource)

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
            neighbors = self.model.space.get_neighborhood(self.pos, moore=True, include_center=False)
            neighbors = list(neighbors)
            self.random.shuffle(neighbors)
            for pos in neighbors:
                if not any(isinstance(a, Organism) for a in self.model.space.get_cell_list_contents(pos)):
                    self.model.space.place_agent(child, pos)
                    self.model.agents.add(child)
                    return