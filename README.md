# BlindControl

**BlindControl** is an automated solar blinds control system developed for BUILD, Aalborg University (AAU). It optimizes indoor comfort by automatically adjusting solar blinds based on environmental conditions (solar radiation, room temperature, etc.).


## Installation

### Prerequisites

* Python 3.8+
* pip (Python package installer)
* UPPAAL tool

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/JuliusJensen02/BlindControl.git
   cd BlindControl
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv env
   source env/bin/activate  # macOS/Linux
   # Windows: env\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

* `main_*.py`: Main application entry points.
* `scripts/`: Utility scripts and tools.
* `data/`: Sample datasets for simulations.
* `requirements.txt`: Python dependencies.

## License

Licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See [LICENSE](LICENSE) for details.

## Acknowledgments
We would like to thank Marco Muñiz for his extensive help and guidance throughout the case study. We would also like to thank Rasmus Jensen and Simon Melgaard from BUILD, as well as CEDAR, for their help with providing data and understanding the thermal dynamics of the building.
