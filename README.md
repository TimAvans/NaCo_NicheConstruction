# Niche Construction Simulation in Evolutionary Algorithms

![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)

This repository accompanies the report *"Simulating Niche Construction and Environmental Feedback"*. It implements an agent-based model to study how organisms shape their evolutionary trajectories by modifying environments, using the [Mesa](https://mesa.readthedocs.io/) framework.

**Key Features**:
- 🧬 Agents with evolvable DNA (consumption, cooperation, metabolism).
- 🌱 Dynamic environment with resource regeneration.
- 📊 Real-time visualization of population dynamics and trait evolution.
- 🔍 Three experiments from the report (baseline, structure-building, species competition).

---

## 🔧 Setup

### Dependencies
```bash
pip install mesa solara numpy matplotlib
```

### Running Simulations
1. **Experiment 1** (Local Environmental Modification):
   ```bash
   solara run app.py  # Adjust parameters in `app.py` (e.g., `n_agents=5`)
   ```
2. **Experiment 2** (Structure-Building):
   Switch to branch `Experiment_2_merged`:
   ```bash
   git checkout Experiment_2_merged
   solara run app.py 
   ```
   or
   ```bash
   python batch_sim.py
   ```

---

**Key Classes**:
- `NicheModel` (`model.py`): Manages agents, environment, and data collection.
- `Organism` (`organism.py`): Implements DNA traits, reproduction, and niche-constructing behaviors.
- `Tile` (`tile.py`): Represents environmental cells with recharge logic.

---
