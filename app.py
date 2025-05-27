from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from model import NicheModel
from tile import Tile
from organism import Organism
import mesa
from structure import Structure
import numpy as np
import matplotlib.pyplot as plt

print(mesa.__version__)

def plot_experiment_results(results, keys_to_plot=None, title="Experiment Metrics", ylabel="Value"):   
    example = results[0]
    all_keys = [k for k in example if k != "epoch"]
    keys = keys_to_plot if keys_to_plot else all_keys

    for key in keys:
        values = [float(r[key]) for r in results]
        plt.plot(values, label=key)

    plt.xlabel("Epoch")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

#TODO: Changed the fitness function so discuss this
def compute_fitness(organism: Organism):
    score = organism.n_steps_alive * 1.0
    score += organism.total_energy_gathered * 0.5  

    score += organism.dna["cooperation"] * 1.5
    score += organism.dna["builder"] * 1.0
    score -= organism.dna["metabolism"] * 2.0

    if organism.built:
        score += 5.0

    return score

def mutate_dna(dna_dict, rate=0.1, scale=0.02):
    values = np.array(list(dna_dict.values()))
    keys = list(dna_dict.keys())

    #Generate mutation mask over the genes
    mask = np.random.rand(len(values)) < rate
    mutations = np.random.normal(loc=0.0, scale=scale, size=len(values))

    #If the mask is true (we have to mutate that gene) apply mutation
    values[mask] += mutations[mask]

    #We do not want a gene to become 0 or negative so never drop it below a very low value
    values = np.clip(values, 0.001, None)

    #Normalize so all dna together sum to 1
    values /= np.sum(values)

    return dict(zip(keys, values))


def array_to_dna(array):
    keys = ["cooperation", "consumption", "metabolism", "builder"]
    total = np.sum(array)
    normalized = array / total

    return dict(zip(keys, normalized))

def k_point_crossover(parent1:Organism, parent2:Organism, k=2):
    dna1 = parent1.dna_to_array()
    dna2 = parent2.dna_to_array()

    if  len(dna1) != len(dna2):
        raise ValueError("Parents must have the same dna length")

    crossover_points = np.sort(np.random.choice(len(dna1), k, replace=False))
    crossover_points.sort()

    offspring = []
    start = 0
    for i, point in enumerate(crossover_points):
        if i % 2 == 0:
            offspring.extend(dna1[start:point])
        else:
            offspring.extend(dna2[start:point])
        start = point
    offspring.extend(dna1[start:] if len(crossover_points) % 2 == 0 else dna2[start:])
    return array_to_dna(np.array(offspring)) 

def run_experiment(n_epochs = 25, steps = 100, n_parents = 4, n_agents = 20, mutation_rate = 0.1, mutation_scale = 0.02):
    pop_hist = []
    model = NicheModel(n_agents=n_agents)
    model.init_organisms()
    for ep in range(n_epochs):
        print(f"Epoch {ep+1}/{n_epochs}")

        for step in range(steps):
            model.step()
        
        organisms = [a for a in model.agents if isinstance(a, Organism)]
        top_organisms = sorted(organisms, key=lambda o:compute_fitness(o), reverse=True)[:n_parents]

        pop_hist.append({
            "epoch": ep,
            "mean_energy": np.mean([a.energy for a in organisms]) if organisms else 0,
            "mean_cooperation": np.mean([a.dna["cooperation"] for a in organisms]) if organisms else 0,
            "mean_fitness": np.mean([compute_fitness(a) for a in organisms]) if organisms else 0,
        })

        # Create next generation
        offspring = []
        while len(offspring) < n_agents:
            parent1, parent2 = model.random.sample(top_organisms, 2)
            dna_child = k_point_crossover(parent1, parent2, k=2)
            dna_child = mutate_dna(dna_child, mutation_rate, mutation_scale)
            child = Organism(model, dna=dna_child)
            offspring.append(child)
            print(f"Child created {child.unique_id}")

        model = NicheModel(n_agents=n_agents)               
        for child in offspring:
            x, y = model.random.randrange(model.width), model.random.randrange(model.height)
            child.model = model
            model.space.place_agent(child, (x, y))
            model.agents.add(child)

    return pop_hist
    
pop_hist = run_experiment()
print(pop_hist)
plot_experiment_results(pop_hist)