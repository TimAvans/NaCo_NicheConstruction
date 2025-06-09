from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from model import NicheModel
from tile import Tile
from organism import OrganismA, OrganismB
import matplotlib.cm as cm
import solara
import mesa
from structure import Structure


print(mesa.__version__)

# Agent appearance logic
def agent_portrayal(agent):
    # Default portrayal for unknown agents
    portrayal = {
        "color": (0.5, 0.5, 0.5),  # Gray color
        "size": 5  # Small size
    }

    if isinstance(agent, Tile):
        x, y = agent.pos
        val = agent.model.environment[x][y]
        norm = min(val / agent.model.max_resource, 1.0)
        portrayal.update({
            "color": (norm, norm, norm),
            "size": 40  # fill cell
        })
    elif isinstance(agent, Structure):
        portrayal.update({
            "color": (1, 1, 0),  # Yellow
            "size": 40  # fill cell
        })
    elif isinstance(agent, OrganismA):
        portrayal.update({
            "color": (0.0, 0.0, 1.0),  # Blue
            "size": 10
        })
    elif isinstance(agent, OrganismB):
        portrayal.update({
            "color": (1.0, 0.0, 0.0),  # Red
            "size": 10
        })
    
    return portrayal

# User-configurable model parameters
model_params = {
    "n_agents": {"type": "SliderInt", "min": 5, "max": 100, "value": 20, "label": "Initial Population"},
    "mutation_rate": {"type": "SliderFloat", "min": 0.0, "max": 0.5, "value": 0.01, "step": 0.01, "label": "Mutation Rate"},
    "max_resource": {"type": "SliderInt", "min": 1, "max": 10, "value": 2, "label": "max resource per tile"},
    "recharge_rate": {"type": "SliderFloat", "min": 0.0, "max": 1.0, "value": 0.25, "step": 0.05, "label": "recharge rate of resource per tile"},
}

# Initialize model
niche_model = NicheModel(n_agents=20, max_resource=2, mutation_rate=0.01, recharge_rate=0.25)

# Space and plots
space_component = make_space_component(agent_portrayal)
resource_plot_a = make_plot_component("MeanResourceA", backend="matplotlib")
energy_plot_a = make_plot_component("MeanEnergyA", backend="matplotlib")
plot_dna_1_a = make_plot_component("MeanCooperationA", backend="matplotlib")
plot_dna_2_a = make_plot_component("MeanConsumptionA", backend="matplotlib")
plot_dna_3_a = make_plot_component("MeanReproductionA", backend="matplotlib")
plot_dna_4_a = make_plot_component("MeanBuilderA", backend="matplotlib")
plot_dna_5_a = make_plot_component("MeanMovementA", backend="matplotlib")
plot_population_a = make_plot_component("OrganismCountA", backend="matplotlib")
plot_structures_a = make_plot_component("StructureCountA", backend="matplotlib")
plot_age_a = make_plot_component("AvgLifespanA", backend="matplotlib")

resource_plot = make_plot_component("MeanResourceB", backend="matplotlib")
energy_plot = make_plot_component("MeanEnergyB", backend="matplotlib")
plot_dna_1 = make_plot_component("MeanCooperationB", backend="matplotlib")
plot_dna_2 = make_plot_component("MeanConsumptionB", backend="matplotlib")
plot_dna_3 = make_plot_component("MeanReproductionB", backend="matplotlib")
plot_dna_4 = make_plot_component("MeanBuilderB", backend="matplotlib")
plot_dna_5 = make_plot_component("MeanMovementB", backend="matplotlib")
plot_population = make_plot_component("OrganismCountB", backend="matplotlib")
plot_structures = make_plot_component("StructureCountB", backend="matplotlib")
plot_age = make_plot_component("AvgLifespanB", backend="matplotlib")

plot_cooperators = make_plot_component("Cooperators", backend="matplotlib")
plot_noncooperatores = make_plot_component("NonCooperators", backend="matplotlib")

plot_total = make_plot_component("TotalPopulation", backend="matplotlib")


# Interactive web app
page = SolaraViz(
    niche_model,
    components=[space_component, resource_plot_a, energy_plot_a, plot_dna_1_a, plot_dna_2_a, plot_dna_3_a, 
                plot_dna_4_a, plot_dna_5_a, plot_population_a, plot_structures_a, plot_age_a,  
                resource_plot, energy_plot, plot_dna_1, plot_dna_2, plot_dna_3, 
                plot_dna_4, plot_dna_5, plot_population, plot_structures, plot_age, plot_total, 
                plot_cooperators, plot_noncooperatores, plot_structures],
    model_params=model_params,
    name="Niche Construction Model: Third Experiment, Competing Species with Distinct Niche Strategies"
)
#page

