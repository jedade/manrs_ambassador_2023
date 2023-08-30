# MANRS Mentors and Ambassadors Program 2023 (MANRS+tool)

[![Project Logo](logo.png)](https://www.manrs.org/wp-content/themes/manrs/assets/images/logo-black.svg)

The aim of this tool is to be able to have the supply chain of an ASN
belonging to a category and a country and to check the routing security
status of each of the ASNs.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Project Overview

The aim of this tool is to be able to have the supply chain of an ASN
belonging to a category and a country and to check the routing security
status of each of the ASNs. This development will take place in
two phases:
● Creation of a script with these different functions:
Input: country, output: list ofASNs
Input: country, output: list of categories
Input: ASN, output:list of
siblings
input: ASN, output: list of providers/peers
input: ASN, output: MANRS metrics
● Presentation by a platform of
the information processed by the script on a web page with
graphics.
## Features

List the key features or functionalities of your project.
- SCRIPT with Pandas: This script 
- API with FASTAPI: 
- Platform web (TO-DO): Description
- ...

## Getting Started

Provide instructions on how to set up the project locally. This section should include prerequisites and installation steps.

### Prerequisites

List the software, libraries, and tools that need to be installed before setting up your project.

- Prerequisite 1 : python 3.10+
- Prerequisite 2: install virtualenv for ubuntu `apt-get install virtualenv`
- ...

### Installation

1. Clone the repository: `git clone https://github.com/jedade/manrs_ambassador_2023.git`
2. Create virtualenv `python3 -m venv {{env}}` and activate your env
2. Navigate to the project directory: `cd manrs_ambassador_2023.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Generate Database: run notebook script `new_script.ipynb`
5. Move newdatabase.db: `cp script/newdatabase.db manrs_2023-08/newdatabase.db`
5. Run api: `python run.py`
## Usage

Go to the documentation at url: `http://127.0.0.1:8000/docs`

## Contributing

Explain how others can contribute to your project. Include guidelines for submitting issues, pull requests, and any coding standards you'd like contributors to follow.

## License

Indicate the license under which your project is distributed. For example:

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

Give credit to libraries, articles, or resources that inspired or helped you in creating your project.

---

**Note:** Replace the placeholders (`jedade`, `manrs_ambassador_2023`, etc.) with actual information related to your project. Add or remove sections as needed to suit your project's requirements.
