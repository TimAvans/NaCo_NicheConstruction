# Experiment 2: Role of cooperation under resource constraints

This repository contains the code and configuration for Experiment 2 in the *Niche Construction Simulation* project.

## Installation

We need to install the required packages before being able to run this repository.
The required packages are mesa, matplotlib, solara, and numpy. Or just run pip install -r requirements.txt

## Simulation overview

Organisms exist in a two-dimensional grid world with finite, and sometimes regenerating resources. Each organism:

- Has a mutateable DNA determining its propensity to perform the following actions:
  - **Cooperate**: Share energy with neighbors and help regenerate local resources.
  - **Consume**: Consume energy from the local tile.
  - **Build**: Construct a structure necessary for reproduction.
  - **Move**
  - **Reproduce**: Create a child, sometimes mutated.

- Must manage limited energy. Agents die when energy is depleted.
- Reproduction requires proximity to a structure.

## Experimental design

- The experiment tests 11 recharge rate values in the range \[0.0, 1.0\] with a step size of 0.1.
- For each `recharge_rate` value, a simulation is run for 500 steps.
- Each run is uniquely identified using a random `run_id`, and results are stored in a separate folder.

## Collected metrics

At each step, the following are tracked:

- **Mean energy**
- **Mean resource**
- **Population size** (Organism count)
- **Structure count**
- **Mean DNA values** 
- **Number of cooperators**: agents with `cooperate` gene > 0.15
- **Number of non-cooperators**: agents with `cooperate` gene <= 0.15

## Outputs

Each run stores:

- **Plots**:
  - Mean energy and resource levels
  - Organism and structure counts
  - DNA expression trends
  - Cooperative vs non-cooperative population counts

- **Model settings**:
  - A `.txt` file summarizing simulation parameters and organism configuration for reproducibility.

Results from running batch simulation with batch_sim.py will be saved in subdirectories under `results/run_<id>/`.

