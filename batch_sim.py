import matplotlib.pyplot as plt
from model import NicheModel
import os
import uuid
from organism import Organism

RECHARGE_VALUES = [round(0.1 * i, 2) for i in range(1, 11)]  # 0.1 to 1.0
N_STEPS = 500
RUNID = f"run_{uuid.uuid4().hex[:8]}"
os.makedirs(RUNID, exist_ok=True)

for rate in RECHARGE_VALUES:
    print(f"Running simulation with recharge_rate={rate}")
    model = NicheModel(n_agents=20, max_resource=2, mutation_rate=0.01, recharge_rate=rate)
    organism_settings = None
    for agent in model.agents:
        if isinstance(agent, Organism):
            organism_settings = agent
            break
    
    os.mkdir(RUNID + f"/recharge_rate_{rate}")
    with open(RUNID + f"/recharge_rate_{rate}/simulation_recharge_{rate:.2f}_params.txt", "w") as f:
        f.write("Simulation Parameters:\n")
        f.write(f"Recharge rate: {rate:.2f}\n")
        f.write(f"Mutation rate: {model.mutation_rate}\n")
        f.write(f"Mutation scale: {model.mutation_scale}\n")
        f.write(f"Max resource: {model.max_resource}\n")
        f.write(f"Initial population: {model.n_agents}\n")
        
        if organism_settings:
            f.write("\nOrganism Parameters:\n")
            f.write(f"Initial energy: {organism_settings.energy}\n")
            f.write(f"Cooperation radius: {organism_settings.coop_radius}\n")
            f.write(f"Structure radius: {organism_settings.struct_radius}\n")
            f.write(f"Consume rate: {organism_settings.consume_rate}\n")
            f.write("Action costs:\n")
            for k, v in organism_settings.action_costs.items():
                f.write(f"  {k}: {v}\n")

    # Run simulation
    for _ in range(N_STEPS):
        model.step()

    # Collect data
    data = model.datacollector.get_model_vars_dataframe()

    # Plot DNA trends
    fig, axes = plt.subplots(3, 2, figsize=(12, 10))
    axes = axes.flatten()

    for key, values in data.items():
        plt.figure()
        plt.plot(values)
        plt.title(key)
        plt.xlabel("Step")
        plt.ylabel(key)
        plt.tight_layout()
        plt.savefig(f"{RUNID}/recharge_rate_{rate}/{key}.png")
        plt.close()


