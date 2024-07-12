# SpeciAL 

This repository contains ...

## Features

- Interactive data visualization
- Real-time data analysis
- User-friendly interface
- Responsive design
- PDF-Export

## Requirements

To run this application, you need the following software and libraries:

- Python 3.x
- Shiny for Python
- Pandas
- Matplotlib
- Plotly

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/MartinKabierski/SpeciAL
    cd SpeciAL
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```

3. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To start the application, run the following command:
```sh
python app.py

## Deployment
Replace `/path/to/project/root` with the path to the project root directory, where the app.py is located.
```sh
rsconnect deploy shiny /path/to/project/root
```