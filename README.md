# Niche Construction Simulation

Repository for the course Natural Computing at Radboud University, Spring 2025. 

![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)
![Mesa](https://img.shields.io/badge/Mesa-1.2.1-green)

This repository contains the code base of the final project for the course Natural Computing at the Radboud University. The project was executed by Sjoerd de Langen, Behnaz Motavali, Tim Janssen. The course itself was tutored by Dr. IMN Wortel (Inge).

## Experiment and results
### 1. Evolving Agents with Local Environmental Modification

 We implement an agent-based model studying niche construction dynamics. The agents are equipped with behavior that allows them to modify their surroundings by planting food on local tiles, simulating a basic form of resource management. The simulation examines how organisms evolve when they can modify their local environments through different behaviors.

Objective: Assess how the ability to construct or modify niches influences long-term genetic diversity, speed of adaptation, and population stability.


## Key Features
- 🧬 Evolving agents with 4 DNA traits: `cooperate`, `consume`, `move`, `reproduce`
- 🌍 Dynamic 25x25 grid environment with resource regeneration
- 🤝 Cooperative behaviors with dual effects:
  - Energy sharing with low-energy neighbors
  - Local environment restoration (scaled by cooperation density)
- 📊 12 real-time metrics tracking:
  - Population dynamics (`OrganismCount`, `Cooperators`)
  - Genetic traits (`MeanCooperation`, `MeanConsumption`)
  - System health (`MeanResource`, `AvgLifespan`)

## Installation
```bash
pip install mesa solara numpy matplotlib
```

## Running the Simulation
```bash
python batch_sim.py
```

## For interactive simulation: 
```bash
solara run app.py 
```

**Key Parameters** (adjustable in UI):
- `Initial Population`: 5-100 agents (default: 20)
- `Mutation Rate`: 0.0-0.5 (default: 0.01)
- `Resource Recharge Rate`: 0.0-1.0 (default: 0.25)
- `Max Resource per Tile`: 1-10 units (default: 2)

## Scientific Foundation
### Methodology
The model implements:
1. **Agent Decision-Making** (`organism.py`):
   - Weighted action selection based on DNA traits
   - Energy-dependent actions with costs (e.g., `cooperate` costs 0.5 energy)
   - Local environmental modification through cooperative restoration

2. **Evolutionary Mechanisms**:
   - Reproduction with 5% mutation rate (Gaussian noise)
   - Trait normalization ensuring behavioral consistency

3. **Data Collection** (`model.py`):
   - 12 model-level metrics tracked via `mesa.DataCollector`
   - Detailed logging of agent actions to `experiment1.log`

## Results Interpretation
Key metrics to observe:
- **Cooperators vs Non-Cooperators**: Survival strategies under different recharge rates
- **MeanResource**: System-wide resource stability
- **AvgLifespan**: Population health indicator

Example findings:
```python
# Sample regression coefficients 
{
    "MeanCooperation": +37.60,  # Strong positive impact
    "MeanConsumption": -19.68,  # High consumption reduces fitness
    "RechargeRate": +34.66      # Environmental abundance matters
}
```

## Extending the Research
To build on this work:
1. **Add New Traits**:
   ```python
   # In organism.py
   self.dna["explore"] = np.random.uniform(0,1)  # Novel trait
   ```
2. **Modify Environmental Rules**:
   ```python
   # In model.py
   self.environment[x][y] += recharge_rate * (1 + coop_density * 0.3)  # Stronger cooperation bonus
   ```

## Documentation
- **Implementation Details**: See docstrings in `model.py` and `organism.py`
- **Visualization Guide**: `app.py` agent portrayal logic
- **Log Analysis**: `experiment1.log` tracks all agent decisions


