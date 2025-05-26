import mesa
import numpy as np

class Organism(mesa.Agent):
    def __init__(self, model, energy = 5, dna = None):
        super().__init__(model)
        self.energy = energy
        self.offspring_count = 0
        self.times_shared = 0
        self.age = 0
        dna_values = np.random.dirichlet([1, 1, 1, 1])  # Now 4 traits
        self.dna = dna or {
            "cooperation": dna_values[0],
            "consumption": dna_values[1],
            "metabolism": dna_values[2],
            "planting": dna_values[3],  # NEW
        } 

    def step(self):
        self.energy -= self.dna["metabolism"] # use metabolism trait
        if self.energy <= 0:
            self.die()
            return
        self.age += 1
        self.move()
        self.consume()
        self.cooperate()
        self.modify_environment()
        self.reproduce()

    def move(self):
        if self.pos is None:
            return
        possibilities = self.model.space.get_neighborhood(self.pos, moore=True, include_center=False)
        possibilities = list(possibilities)
        self.random.shuffle(possibilities)

        for new_pos in possibilities:
            contents = self.model.space.get_cell_list_contents(new_pos)
            if not any(isinstance(a, Organism) for a in contents):
                self.model.space.move_agent(self, new_pos)
                return 

    def die(self):
        if self.pos is not None:
            self.model.dead_ages.append(self.age)
            self.model.space.remove_agent(self)
        self.model.agents.discard(self)  # safer than remove
        print(f"Agent with id {self.unique_id} died at age {self.age}")


    def modify_environment(self):
        """Plant food based on planting trait."""
        if self.pos is None:
            return
        x, y = self.pos
        plant_amount = self.dna["planting"] * 0.5  # Max planting = 0.5
        self.model.environment[x][y] += plant_amount
        if self.model.environment[x][y] > self.model.max_resource:
            self.model.environment[x][y] = self.model.max_resource
        print(f"Agent {self.unique_id} planted {plant_amount:.2f} at ({x},{y})")


    def consume(self):
        if self.pos is None:
            return
        x, y = self.pos
        current_amount = self.model.environment[x][y]
        consumed_amount = min(current_amount, self.dna["consumption"])  # use trait (changed from 1.0)
        self.energy += consumed_amount
        self.model.environment[x][y] -= consumed_amount
        print(f"Agent with id {self.unique_id} consumed {consumed_amount:.2f} at location [{x}, {y}]")

    def cooperate(self):
        if self.pos is None:
            return
        if self.random.random() < self.dna["cooperation"]:
            cellmates = self.model.space.get_cell_list_contents([self.pos])
            others = [a for a in cellmates if isinstance(a, Organism) and a is not self]

            if others and self.energy > 1.0:
                recipient = self.random.choice(others)
                share_amount = 0.5
                self.energy -= share_amount
                recipient.energy += share_amount
                self.times_shared += 1
                print(f"Agent {self.unique_id} shared {share_amount:.2f} with {recipient.unique_id}")


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
                    self.offspring_count += 1  # for fitness function
                    return

    def fitness(self):
        fitness = self.energy + (self.offspring_count * 5) - (self.dna["metabolism"] * 2)
        return  fitness

