from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from model import NicheModel
from tile import Tile
from organism import Organism
import matplotlib.cm as cm
import solara
import mesa
from structure import Structure

print(mesa.__version__)

# Agent appearance logic
def agent_portrayal(agent):
    if isinstance(agent, Tile):
        x, y = agent.pos
        val = agent.model.environment[x][y]
        norm = min(val / agent.model.max_resource, 1.0)

        return {
            "color": (norm, norm, norm),
            "size": 40  # fill cell
        }

    if isinstance(agent, Structure):
        return {
            "color": (1, 1, 0),
            "size": 40  # fill cell
        }

    if isinstance(agent, Organism):
        c = float(agent.dna.get("cooperate", 0.0))
        scaled = min(max(c / 0.5, 0.0), 1.0)  # Maps [0.0, 0.5] → [0.0, 1.0]
        return {
            "color": (1 - scaled, scaled, 0.0),  # red to green
            "size": 10
        }


    return None

# User-configurable model parameters
model_params = {
    "n_agents": {"type": "SliderInt", "min": 5, "max": 100, "value": 20, "label": "Initial Population"},
    "mutation_rate": {"type": "SliderFloat", "min": 0.0, "max": 0.5, "value": 0.01, "step": 0.01, "label": "Mutation Rate"},
    "max_resource": {"type": "SliderInt", "min": 1, "max": 10, "value": 2, "label": "max resource per tile"},
    "recharge_rate": {"type": "SliderFloat", "min": 0.0, "max": 1.0, "value": 0.25, "step": 0.05, "label": "recharge rate of resource per tile"},
}

# Initialize model
niche_model = NicheModel(n_agents=20, max_resource=2, mutation_rate=0.01, recharge_rate=0.25)

# Plots
space_component = make_space_component(agent_portrayal)
resource_plot = make_plot_component("MeanResource", backend="matplotlib")
energy_plot = make_plot_component("MeanEnergy", backend="matplotlib")
plot_dna_1 = make_plot_component("MeanCooperation", backend="matplotlib")
plot_dna_2 = make_plot_component("MeanConsumption", backend="matplotlib")
plot_dna_3 = make_plot_component("MeanReproduction", backend="matplotlib")
plot_dna_4 = make_plot_component("MeanBuilder", backend="matplotlib")
plot_dna_5 = make_plot_component("MeanMovement", backend="matplotlib")
plot_population = make_plot_component("OrganismCount", backend="matplotlib")
plot_structures = make_plot_component("StructureCount", backend="matplotlib")
plot_age = make_plot_component("AvgLifespan", backend="matplotlib")

page = SolaraViz(
    niche_model,
    components=[space_component, resource_plot, energy_plot, plot_dna_1, plot_dna_2, plot_dna_3, 
                plot_dna_4, plot_dna_5, plot_population, plot_structures, plot_age],
    model_params=model_params,
    name="Niche Construction Model: First Experiment, Local Environmental Modification"
)