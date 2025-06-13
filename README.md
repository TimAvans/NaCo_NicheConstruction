# Niche Construction Simulation in Evolutionary Algorithms

![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)

This repository accompanies the report *"Simulating Niche Construction and Environmental Feedback"*. It implements an agent-based model to study how organisms shape their evolutionary trajectories by modifying environments, using the [Mesa](https://mesa.readthedocs.io/) framework.
A sample run of batch_sim.py is available in the folder run_sample, to see how the UI version works, after following the setup run.
```bash
   solara run app.py 
```

**Key Features**:
- 🧬 Agents with evolvable DNA (consumption, cooperation, metabolism).
- 🌱 Dynamic environment with resource regeneration.
- 📊 Real-time visualization of population dynamics and trait evolution, or batch simulations for comprehensive statistics.
- 🔍 Three experiments from the report (baseline, structure-building, species competition), in different branches.

---

## 🔧 Setup

### Dependencies
```bash
pip install mesa solara numpy matplotlib
```
or
```bash
pip install -r requirements.txt
```

### Running Simulations
1. **Experiment 1** (Local Environmental Modification):
   Switch to branch `Experiment_1_merged`:
   ```bash
   git checkout Experiment_1_merged
   solara run app.py 
   ```
   or to run batch experiments with different recharge rates
   ```bash
   python batch_sim.py
   ```
2. **Experiment 2** (Structure-Building):
   Switch to branch `Experiment_2_testing`:
   ```bash
   git checkout Experiment_2_testing
   solara run app.py 
   ```
   or to run batch experiments with different recharge rates
   ```bash
   python batch_sim.py
   ```
3. **Experiment 3** (Different cooperation organisms):
   Switch to branch `Experiment_3_merged`:
   ```bash
   git checkout Experiment_3_merged
   solara run app.py 
   ```
   or to run batch experiments with different recharge rates
   ```bash
   python batch_sim.py
   ```
---

**Key Classes**:
- `NicheModel` (`model.py`): Manages agents, environment, and data collection.
- `Organism` (`organism.py`): Implements DNA traits, reproduction, and niche-constructing behaviors.
- `Tile` (`tile.py`): Represents environmental cells with recharge logic.

---
