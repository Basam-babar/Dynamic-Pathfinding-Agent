# Dynamic Pathfinding Agent

This project implements a grid-based Dynamic Pathfinding Agent using Informed Search Algorithms (A* and Greedy Best-First Search) in Python using Pygame.

## Features
* **Algorithms:** A* Search and Greedy Best-First Search (GBFS).
* **Heuristics:** Manhattan Distance and Euclidean Distance.
* **Interactive Grid:** Click to draw (left-click) or erase (right-click) walls.
* **Dynamic Mode:** Simulates an agent moving along the path. While moving, obstacles may randomly spawn. If an obstacle blocks the active path, the agent immediately recalculates a new route from its current position.
* **Real-time Metrics:** Displays nodes expanded, total path cost, and execution time in ms.

## Requirements
* Python 3.x
* Pygame

## Installation & Execution
1. Install the required dependency:
   ```bash
   pip install pygame
