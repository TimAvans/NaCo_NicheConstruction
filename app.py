from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from model import NicheModel

niche_model = NicheModel()

def agent_portrayal(agent):
    if agent is None or agent.pos is None:
        return None
    return {
        "color": "green" if agent.strategy == "cooperator" else "red",
        "size": 8,
    }

model_params = {
    "n_agents": {"type": "SliderInt", "min": 10, "max": 100, "value": 50, "label": "Initial Population"},
    "width": {"type": "SliderInt", "min": 10, "max": 50, "value": 20, "label": "Grid Width"},
    "height": {"type": "SliderInt", "min": 10, "max": 50, "value": 20, "label": "Grid Height"},
    "mutation_rate": {"type": "SliderFloat", "min": 0.0, "max": 0.5, "value": 0.01, "step": 0.01, "label": "Mutation Rate"},
}

space_component = make_space_component(agent_portrayal)
plot_component = make_plot_component(["Cooperators", "Freeloaders"], backend="matplotlib")
resource_plot = make_plot_component("MeanResource", backend="matplotlib")
energy_plot = make_plot_component("MeanEnergy", backend="matplotlib")

page = SolaraViz(
    niche_model,
    components=[space_component, plot_component, resource_plot, energy_plot],
    model_params=model_params,
    name="Niche Construction Model"
)
page