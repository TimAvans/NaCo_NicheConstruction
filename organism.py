import mesa
import numpy as np
from structure import Structure

class Organism(mesa.Agent):
    def __init__(self, model, energy = 10, dna = None):
        super().__init__(model)
        self.energy = energy
        self.n_steps_alive = 0
        self.total_energy_gathered = 0
        dna_values = np.random.dirichlet([1, 1, 1, 1, 1])
        self.consume_rate = 1
        self.dna = dna or {
            "cooperate": dna_values[0],
            "consume": dna_values[1],
            "build": dna_values[2],
            "move": dna_values[3],
            "reproduce": dna_values[4],
        }

        self.action_map = {
            "cooperate": self.cooperate,
            "consume": self.consume,
            "build": self.modify_environment,
            "move": self.move,
            "reproduce": self.reproduce,
        }

        self.action_costs = {
            "move": 0.5,
            "consume": 0.2,
            "cooperate": 0.6,
            "build": 2.0,
            "reproduce": 3.0,
        }

        self.built = False

    '''
    TODO: Clearly define what each action the organism can take does (so we can state it clearly in the report)
    '''
    def step(self):
        #Check if organism has 0 energy if it does it dies.
        if self.energy <= 0:
            self.die()
            return
        #Check if an organism can do any action if not it should die
        if all(self.energy < self.action_costs[action] for action in self.action_map):
            self.die()
            return
        
        self.n_steps_alive += 1

        #Do 1 action based on the DNA, we let the organisms fail gracefully if they choose an option they do not have enough energy for
        actions = list(self.action_map.keys())
        weights = [self.dna.get(key, 1.0) for key in actions]
        total = sum(weights)
        probs = [w / total for w in weights]
        # Select action based on normalized DNA weights
        selected_action = self.random.choices(population=actions, weights=probs)[0]
        succes = self.action_map[selected_action]()
        print(f"Agent with id {self.unique_id} choose the following action: {selected_action} and succeeded => {succes}")
    
    def cooperate(self):
        if self.energy < self.action_costs["cooperate"]:
            return False
        self.energy -= self.action_costs["cooperate"]
        return True
    
    #TODO: Cannot move away from structure
    def move(self):
        if self.energy < self.action_costs["move"]:
            return False
        self.energy -= self.action_costs["move"]

        possibilities = self.model.space.get_neighborhood(self.pos, moore=True, include_center=False)
        possibilities = list(possibilities)
        self.random.shuffle(possibilities)

        for new_pos in possibilities:
            contents = self.model.space.get_cell_list_contents(new_pos)
            if not any(isinstance(a, Organism) for a in contents):
                self.model.space.move_agent(self, new_pos)
                return True
        return False
    
    #TODO: Organism needs a structure to survive
    def die(self):
        self.model.space.remove_agent(self)
        self.model.agents.remove(self)
        print(f"Agent with id {self.unique_id} died due to energy level")

    def modify_environment(self):
        if self.energy < self.action_costs["build"]:
            return False
        
        x, y = self.pos
        contents = self.model.space.get_cell_list_contents((x, y))
        if not any(isinstance(a, Structure) for a in contents):
            self.energy -= self.action_costs["build"]
            struct = Structure(self.model)
            self.model.space.place_agent(struct, (x, y))
            self.model.agents.add(struct)
            self.built = True
            print(f"Agent with id {self.unique_id} build a structure at [{x}, {y}]")
        return True
    
    def consume(self):
        if self.pos is None:
            return False
        if self.energy < self.action_costs["consume"]:
            return False
        self.energy -= self.action_costs["consume"]

        x, y = self.pos
        current_amount = self.model.environment[x][y]
        consumption_capacity = self.consume_rate
        consumed_amount = min(current_amount, consumption_capacity)
        self.energy += consumed_amount
        self.model.environment[x][y] -= consumed_amount
        print(f"Agent with id {self.unique_id} consumed {consumed_amount} at location [{x}, {y}]")
        self.total_energy_gathered += consumed_amount
        return True
    
        #Removed cooperation here since this sim is mostly about buildings and reproduction, fix the base first
        # repair = self.dna["cooperation"] * self.model.cooperation_factor
        # self.model.environment[x][y] = min(self.model.environment[x][y] + repair, self.model.max_resource)

    def mutate_dna(self):
        new_dna = {
            k: max(0.001, v + self.random.gauss(0, 0.02)) for k, v in self.dna.items()
        }
        total = sum(new_dna.values())
        return {k: v / total for k, v in new_dna.items()}

    def reproduce(self):
        if self.energy < self.action_costs["reproduce"]:
            return False
        self.energy -= self.action_costs["reproduce"]
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
                return True
        return False