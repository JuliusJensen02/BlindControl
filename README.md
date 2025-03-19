# BlindControl

**BlindControl** is a project developed at BUILD AAU aimed at automating and optimizing the control of window blinds. The system adjusts blinds based on environmental factors to enhance energy efficiency and indoor comfort.

## Features

- **Automated Blind Adjustment**: Blinds are controlled automatically in response to environmental conditions such as sunlight intensity and room temperature.
- **Manual Override**: Users can manually adjust blinds through a user-friendly interface.
- **Scheduling**: Set schedules for blinds to open or close at specific times.
- **Energy Efficiency**: Optimizes natural light usage to reduce reliance on artificial lighting and HVAC systems.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/JuliusJensen02/BlindControl.git
   cd BlindControl
   ```

2. **Set Up the Virtual Environment**:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows, use 'env\Scripts\activate'
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the System**:
   - Modify the `config.json` file to match your hardware setup and preferences.
   - Ensure all hardware components are connected as specified in the configuration.

5. **Run the Application**:
   ```bash
   python main.py
   ```

## Usage

- **Automated Mode**: The system will automatically adjust blinds based on sensor data.
- **Manual Control**: Access the manual control interface at `http://localhost:5000` to adjust blinds as needed.
- **Scheduling**: Use the scheduling feature in the interface to set specific times for blinds to open or close.

## Contributing

We welcome contributions from the community. To contribute:

1. **Fork the Repository**: Click the 'Fork' button at the top right corner of this page.
2. **Create a New Branch**: Use a descriptive name for your branch.
3. **Make Your Changes**: Ensure your code follows the project's coding standards.
4. **Submit a Pull Request**: Provide a clear description of your changes and the problem they solve.

Please refer to our [Code of Conduct](CODE_OF_CONDUCT.md) for guidelines on contributing.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- Thanks to the BUILD AAU community for their support and resources.
- Special mention to the developers of similar projects that inspired this work.

---

*Note: This project is under active development. Features and functionalities are subject to change.*

