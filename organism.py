import mesa
import numpy as np
from structure import Structure

class Organism(mesa.Agent):
    def __init__(self, model, energy = 5, dna = None):
        super().__init__(model)
        self.energy = energy
        self.n_steps_alive = 0
        self.total_energy_gathered = 0
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
        self.n_steps_alive += 1
        self.move()
        self.consume()
        self.modify_environment()

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
        self.total_energy_gathered += consumed_amount

        repair = self.dna["cooperation"] * self.model.cooperation_factor
        self.model.environment[x][y] = min(self.model.environment[x][y] + repair, self.model.max_resource)

    def dna_to_array(self):
        return np.array([self.dna["cooperation"], self.dna["consumption"], self.dna["metabolism"], self.dna["builder"]])

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