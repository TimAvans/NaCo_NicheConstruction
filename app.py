from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from model import NicheModel
from tile import Tile
from organism import Organism
import matplotlib.cm as cm
import solara
import mesa

print("Mesa version:", mesa.__version__)

# Initialize model
niche_model = NicheModel(max_resource=2)

# Agent appearance logic
def agent_portrayal(agent):
    if isinstance(agent, Tile):
        x, y = agent.pos
        val = agent.model.environment[x][y]
        norm = min(val / agent.model.max_resource, 1.0)

        # r, g, b, _ = cm.plasma(norm)
        return {
            "color": (norm, norm, norm),  # grayscale for environment level
            "size": 40 # fill cell
        }

    if isinstance(agent, Organism):
        c = float(agent.dna.get("cooperation", 0.0))
        p = float(agent.dna.get("planting", 0.0))  # NEW: use planting for color variation
        return {
            "color": (1 - c, c, p),  # red to green # RGB based on cooperation (green) and planting (blue)
            "size": 10
        }

    return None

# User-configurable model parameters
model_params = {
    "n_agents": {"type": "SliderInt", "min": 10, "max": 100, "value": 50, "label": "Initial Population"},
    "width": {"type": "SliderInt", "min": 10, "max": 50, "value": 20, "label": "Grid Width"},
    "height": {"type": "SliderInt", "min": 10, "max": 50, "value": 20, "label": "Grid Height"},
    "mutation_rate": {"type": "SliderFloat", "min": 0.0, "max": 0.5, "value": 0.01, "step": 0.01, "label": "Mutation Rate"},
}

# Space and plots
space_component = make_space_component(agent_portrayal)
resource_plot = make_plot_component("MeanResource", backend="matplotlib")
energy_plot = make_plot_component("MeanEnergy", backend="matplotlib")
plot_dna_1 = make_plot_component("AvgCooperation", backend="matplotlib")
plot_dna_2 = make_plot_component("AvgConsumption", backend="matplotlib")
plot_dna_3 = make_plot_component("AvgMetabolism", backend="matplotlib")
plot_dna_4 = make_plot_component("AvgPlanting", backend="matplotlib")  # NEW plot
plot_fitness = make_plot_component("AvgFitness", backend="matplotlib")
plot_population = make_plot_component("OrganismCount", backend="matplotlib")

# Interactive web app
page = SolaraViz(
    niche_model,
    components=[space_component, resource_plot, energy_plot, plot_dna_1, plot_dna_2, plot_dna_3, plot_dna_4, plot_fitness, plot_population],
    model_params=model_params,
    name="Niche Construction Model: First Experiment, Local Environmental Modification"
)

#page

