import mesa
import numpy as np
from structure import Structure

class Organism(mesa.Agent):
    def __init__(self, model, energy = 10, struct_radius = 2, coop_radius = 2, dna = None):
        super().__init__(model)
        self.energy = energy
        self.coop_radius = coop_radius
        self.struct_radius = struct_radius
        self.n_steps_alive = 0
        self.total_energy_gathered = 0
        dna_values = np.random.dirichlet([1]*5)

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
            "cooperate": 0.5,
            "build": 2.0,
            "reproduce": 5.0,
        }

        self.built = False

    '''
    TODO: Clearly define what each action the organism can take does (so we can state it clearly in the report)
    TODO: Implement cooperation since now it is just an energy sink
    '''
    def step(self):
        if self.pos is None:
            print(f"Warning: Agent {self.unique_id} has no position!")
            self.die()
            return
        
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
    
    '''
    '''
    def cooperate(self):
        if self.pos is None:
            return False  
        if self.energy < self.action_costs["cooperate"]:
            return False

        neighbors = self.model.space.get_neighbors(self.pos, moore=True, include_center=False, radius=self.coop_radius)
        low_energy_neighbors = [a for a in neighbors if isinstance(a, Organism) and a.energy < 2]

        shared = False
        if low_energy_neighbors:
            target = self.random.choice(low_energy_neighbors)
            amount = min(1.0, self.energy - self.action_costs["cooperate"])
            if amount > 0:
                target.energy += amount
                self.energy -= amount
                print(f"Agent {self.unique_id} shared {amount:.2f} energy with {target.unique_id}")
                shared = True

        # Environmental restoration scaled by cooperation density
        neighborhood = self.model.space.get_neighborhood(self.pos, moore=True, include_center=True, radius=self.coop_radius)
        coop_agents_nearby = sum(
            1 for pos in neighborhood
            for a in self.model.space.get_cell_list_contents(pos)
            if isinstance(a, Organism) and a.dna["cooperate"] > 0.15
        )

        for x, y in neighborhood:
            self.model.environment[x][y] = min(
                self.model.max_resource,
                self.model.environment[x][y] + self.model.recharge_rate * (1 + 0.2 * coop_agents_nearby)
            )

        self.energy -= self.action_costs["cooperate"]

        if shared:
            print(f"Agent {self.unique_id} also repaired the environment at {self.pos} with {coop_agents_nearby} allies")
        else:
            print(f"Agent {self.unique_id} repaired the environment at {self.pos} but found no one to help (density = {coop_agents_nearby})")

        return True
        
    def move(self):
        if self.pos is None:
            return False  
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
    
    def die(self):
        self.model.space.remove_agent(self)
        self.model.agents.remove(self)
        print(f"Agent with id {self.unique_id} died due to energy level")

    def modify_environment(self):
        if self.pos is None:
            return False         
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
        if consumed_amount <= 0:
            return False
        self.energy += consumed_amount
        self.model.environment[x][y] -= consumed_amount
        print(f"Agent with id {self.unique_id} consumed {consumed_amount} at location [{x}, {y}]")
        self.total_energy_gathered += consumed_amount
        return True
    
    def mutate_dna(self):
        new_dna = {
            k: max(0.001, v + self.random.gauss(0, self.model.mutation_scale)) for k, v in self.dna.items()
        }
        total = sum(new_dna.values())
        return {k: v / total for k, v in new_dna.items()}

    def reproduce(self):
        repro_cost = self.action_costs["reproduce"]

        # Check for nearby structure
        nearby = self.model.space.get_neighborhood(self.pos, moore=True, include_center=True, radius=self.struct_radius)
        structure_found = any(
            isinstance(a, Structure)
            for pos in nearby
            for a in self.model.space.get_cell_list_contents(pos)
        )
        if not structure_found:
            print(f"Agent {self.unique_id} found no nearby structure to reproduce")
            return False

        # Find free spot first
        if self.pos is None:
            print(f"Agent {self.unique_id} has no position during reproduction — skipping.")
            return False

        neighbors = list(self.model.space.get_neighborhood(self.pos, moore=True, include_center=False))
        self.random.shuffle(neighbors)
        for pos in neighbors:
            if not any(isinstance(a, Organism) for a in self.model.space.get_cell_list_contents(pos)):
                # Place child only if position is available
                if self.random.random() < self.model.mutation_rate:
                    print(f"Agent with id {self.unique_id} is reproducing and mutated its child")
                    child_dna = self.mutate_dna()
                else:
                    print(f"Agent with id {self.unique_id} is reproducing")
                    child_dna = dict(self.dna)

                child = Organism(self.model, dna=child_dna)
                self.model.space.place_agent(child, pos)
                self.model.agents.add(child)
                self.energy -= repro_cost
                return True

        print(f"Agent {self.unique_id} failed to place offspring")
        return False