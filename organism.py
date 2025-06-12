import mesa
import numpy as np
from structure import Structure
import logging

# Set up logging configuration at the beginning 
logging.basicConfig(
    filename='experiment3.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'  # 'w' to overwrite, 'a' to append
)

class Organism(mesa.Agent):
    def __init__(self, model, energy = 5, struct_radius = 2, coop_radius = 2, dna = None):
        super().__init__(model)
        self.energy = energy
        self.coop_radius = coop_radius
        self.struct_radius = struct_radius
        self.n_steps_alive = 0
        self.total_energy_gathered = 0
        self.age = 0
        self.consume_rate = 1

        self.action_map = {
            "cooperate": self.cooperate,
            "consume": self.consume,
            "move": self.move,
            "reproduce": self.reproduce,
        }

        self.action_costs = {
            "move": 0.5,
            "consume": 0.2,
            "cooperate": 0.5,
            "reproduce": 6.0,
        }

        self.built = False

    def step(self):
        if self.pos is None:
            print(f"Warning: Agent {self.unique_id} has no position!")
            logging.warning(f"Agent {self.unique_id} has no position!")
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
        self.age += 1
        print(f"Agent with id {self.unique_id} choose the following action: {selected_action} and succeeded => {succes}")
        logging.info(f"Agent with id {self.unique_id} choose the following action: {selected_action} and succeeded => {succes}")
    
    def cooperate(self):
        if self.pos is None:
            return False  
        if self.energy < self.action_costs["cooperate"]:
            return False

        self.energy -= self.action_costs["cooperate"]

        print(f"Agent {self.unique_id} base cooperate function")
        logging.info(f"Agent {self.unique_id} base cooperate function")

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
        if self.pos is not None:
            self.model.dead_ages.append(self.age)
            self.model.space.remove_agent(self)
        self.model.agents.discard(self)  # safer than remove
        print(f"Agent with id {self.unique_id} died at age {self.age}")
        logging.info(f"Agent with id {self.unique_id} died at age {self.age}")
    
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
        logging.info(f"Agent with id {self.unique_id} consumed {consumed_amount} at location [{x}, {y}]")
        self.total_energy_gathered += consumed_amount
        return True
    def reproduce(self):
        print(f"Agent {self.unique_id} base reproduce function")
        return False
    


class OrganismA(Organism):  # Environmental Enricher
    def __init__(self, model, energy = 9, struct_radius = 2, coop_radius = 2, dna = None):
        super().__init__(model, energy)
        self.dna = dna or {
            "cooperate": 0.25,
            "consume": 0.25,
            "move": 0.25,
            "reproduce": 0.25,
        }

    def reproduce(self):
            repro_cost = self.action_costs["reproduce"]
            if self.energy < repro_cost:
                return False

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
                        if isinstance(self, OrganismA):
                            child_dna = self.mutate_dna()
                    else:
                        print(f"Agent with id {self.unique_id} is reproducing")
                        child_dna = dict(self.dna)

                    child = OrganismA(self.model, dna=child_dna)
                    self.model.space.place_agent(child, pos)
                    self.model.agents.add(child)
                    self.energy -= repro_cost
                    return True

            print(f"Agent {self.unique_id} failed to place offspring")
            return False
    
    def mutate_dna(self):
        new_dna = {
            k: max(0.001, v + self.random.gauss(0, self.model.mutation_scale)) for k, v in self.dna.items()
        }
        total = sum(new_dna.values())
        return {k: float(v / total) for k, v in new_dna.items()} # to be safe
  
    def cooperate(self):
        if self.pos is None:
            return False  
        if self.energy < self.action_costs["cooperate"]:
            return False

        neighbors = self.model.space.get_neighbors(self.pos, moore=True, include_center=False, radius=self.coop_radius)
        low_energy_neighbors = [a for a in neighbors if isinstance(a, OrganismA) and a.energy < 2]

        shared = False
        if low_energy_neighbors:
            target = self.random.choice(low_energy_neighbors)
            amount = min(1.0, self.energy - self.action_costs["cooperate"])
            if amount > 0:
                target.energy += amount
                self.energy -= amount
                print(f"Agent {self.unique_id} shared {amount:.2f} energy with {target.unique_id}")
                logging.info(f"Agent {self.unique_id} shared {amount:.2f} energy with {target.unique_id}")
                shared = True

        # Environmental restoration scaled by cooperation density
        neighborhood = self.model.space.get_neighborhood(self.pos, moore=True, include_center=True, radius=self.coop_radius)
        coop_agents_nearby = sum(
            1 for pos in neighborhood
            for a in self.model.space.get_cell_list_contents(pos)
            if isinstance(a, OrganismA) and a.dna["cooperate"] > 0.01
        )
        
        for x, y in neighborhood:
            self.model.environment[x][y] = min(
                self.model.max_resource,
                self.model.environment[x][y] + (self.model.recharge_rate + 0.2) * (1 + 0.2 * coop_agents_nearby)
            )

        self.energy -= self.action_costs["cooperate"]

        if shared:
            print(f"Agent {self.unique_id} also repaired the environment at {self.pos} with {coop_agents_nearby} allies")
            logging.info(f"Agent {self.unique_id} also repaired the environment at {self.pos} with {coop_agents_nearby} allies")
        else:
            print(f"Agent {self.unique_id} repaired the environment at {self.pos} but found no one to help (density = {coop_agents_nearby})")
            logging.info(f"Agent {self.unique_id} repaired the environment at {self.pos} but found no one to help (density = {coop_agents_nearby})")

        return True    

class OrganismB(Organism):  # Aggressive Consumer
    def __init__(self, model, energy = 9, struct_radius = 2, coop_radius = 2, dna = None):
        super().__init__(model, energy)
        self.dna = dna or {
            "cooperate": 0.0,
            "consume": 0.50,
            "move": 0.25,
            "reproduce": 0.25,
        }
    def reproduce(self):
            repro_cost = self.action_costs["reproduce"]
            if self.energy < repro_cost:
                return False

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
                        if isinstance(self, OrganismB):
                            child_dna = self.mutate_dna()
                    else:
                        print(f"Agent with id {self.unique_id} is reproducing")
                        child_dna = dict(self.dna)

                    child = OrganismB(self.model, dna=child_dna)
                    self.model.space.place_agent(child, pos)
                    self.model.agents.add(child)
                    self.energy -= repro_cost
                    return True

            print(f"Agent {self.unique_id} failed to place offspring")
            return False
    
    def mutate_dna(self):
        fixed_cooperate = self.dna["cooperate"]
        mutable_keys = [k for k in self.dna if k != "cooperate"]

        # Mutate only non-cooperate genes
        new_dna_mutable = {
            k: max(0.001, self.dna[k] + self.random.gauss(0, self.model.mutation_scale))
            for k in mutable_keys
        }

        total_mutable = sum(new_dna_mutable.values())
        scale = 1.0 - fixed_cooperate 

        normalized_mutable = {
            k: (v / total_mutable) * scale
            for k, v in new_dna_mutable.items()
        }

        return {"cooperate": fixed_cooperate, **normalized_mutable}
    
    #!IDK we might want to make it actually an agressive consumer instead of just doing nothing in cooperate?
    def cooperate(self):
        if self.pos is None:
            return False  
        if self.energy < self.action_costs["cooperate"]:
            return False
        self.energy -= self.action_costs["cooperate"]
        # # Removed sharing for individualistic agent
        # # Environmental degradation scaled by cooperation density
        # neighborhood = self.model.space.get_neighborhood(self.pos, moore=True, include_center=True, radius=self.coop_radius)
        # coop_agents_nearby = sum(
        #     1 for pos in neighborhood
        #     for a in self.model.space.get_cell_list_contents(pos)
        #     if isinstance(a, Organism) and a.dna["cooperate"] < 0.7
        # )
        
        # for x, y in neighborhood:
        #     self.model.environment[x][y] = min(
        #         self.model.max_resource,
        #         self.model.environment[x][y] + self.model.recharge_rate * (1 + 0.2 * coop_agents_nearby)
        #     )

        # self.energy -= self.action_costs["cooperate"]

        print(f"Agent {self.unique_id} of type OrganismB at position {self.pos} went into the cooperate function")
        logging.info(f"Agent {self.unique_id} of type OrganismB at position {self.pos} went into the cooperate function")

        return True
