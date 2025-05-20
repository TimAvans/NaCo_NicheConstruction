from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from model import NicheModel
from tile import Tile
from organism import OrganismA, OrganismB
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
    
    if isinstance(agent, OrganismA):
        return {"color": (0.0, 0.0, 1.0), "size": 10} # RGB based on type (blue)

    if isinstance(agent, OrganismB):
        return {"color": (1.0, 0.0, 0.0), "size": 10} # RGB based on type (red)

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
# resource_plot = make_plot_component("MeanResource", backend="matplotlib")
# energy_plot = make_plot_component("MeanEnergy", backend="matplotlib")
# plot_dna_1 = make_plot_component("AvgCooperation", backend="matplotlib")
# plot_dna_2 = make_plot_component("AvgConsumption", backend="matplotlib")
# plot_dna_3 = make_plot_component("AvgMetabolism", backend="matplotlib")
# plot_dna_4 = make_plot_component("AvgPlanting", backend="matplotlib")  
plot_species_a = make_plot_component("PopulationA", backend="matplotlib")
plot_species_b = make_plot_component("PopulationB", backend="matplotlib")
plot_total = make_plot_component("TotalPopulation", backend="matplotlib")

# Interactive web app
page = SolaraViz(
    niche_model,
    components=[space_component, plot_species_a, plot_species_b, plot_total],
    model_params=model_params,
    name="Niche Construction Model: Third Experiment, Competing Species with Distinct Niche Strategies"
)

#page