# Gallery Wall Planner Tool

---

## Overview
The **Gallery Wall Planner Tool** is a software application designed to streamline the process of planning and installing art pieces in gallery spaces. It allows users to customize wall measurements, input art piece details, and visualize the layout of art pieces on a wall. The tool also calculates precise nail placement instructions for hanging art pieces, reducing the need for readjustments during installation.

This project was inspired by Yingxin's experience working at Roberta's Art Gallery, where inefficiencies in the installation process led to wasted time and effort. The goal is to create a visual tool that simplifies the planning process and improves workflow for gallery installations.

---

# Gallery Wall Planner

The Gallery Wall Planner is a Python-based application that helps users visualize and plan artwork arrangements on walls. It provides a virtual canvas to position artworks, create snap lines for alignment, and save layouts for future reference.

## Features

- **Virtual Wall Visualization**: Create a scaled representation of your wall space
- **Artwork Management**: 
  - Add artworks manually or import from Excel files
  - View artwork details (name, dimensions, medium, price)
- **Interactive Placement**:
  - Drag-and-drop artworks on the virtual wall
  - Snap-to-grid functionality for precise alignment
- **Snap Lines**:
  - Create horizontal and vertical guide lines
  - Customize line positions and alignment options
  - Visual feedback when artworks snap to lines
- **Layout Saving**: Export your wall layout with artwork positions
- **Collision Detection**: Visual indication when artworks overlap

## Installation

1. **Prerequisites**:
   - Python 3.7 or later
   - tkinter (usually included with Python)

2. **Install dependencies**:
   ```bash
   pip install openpyxl  # For Excel file support
