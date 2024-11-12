# Project Setup

## Setup Environment

This project requires certain dependencies to be installed for proper functioning. Follow the instructions below to set up your environment.

### Conda Environment

To create a conda environment with Python 3.12, use the following command:

conda create --name crewai-flows python=3.12

To activate the conda environment, use:

conda activate crewai-flows

### Virtualenv

If you prefer using virtualenv, first install it:

pip install virtualenv

Then create a virtual environment with Python 3.12:

virtualenv -p python3.12 crewai-dev

Activate the virtualenv environment with:

- On Windows: myenv\Scripts\activate
- On macOS/Linux: source myenv/bin/activate

### Installing Dependencies

To install the dependencies listed in the `requirements.txt` file, use:

pip install -r requirements.txt

## Create Flow with Crews

1. **Create a New Flow:**
   - Run the following command to create a new flow named `self_evaluation_loop_flow`:
     ```bash
     crewai create flow self_evaluation_loop_flow
     ```
   - Navigate into the newly created directory:
     ```bash
     cd self_evaluation_loop_flow
     ```

2. **Install Dependencies:**
   - Run the following command to install all necessary dependencies:
     ```bash
     crewai install
     ```

3. **Activate the Environment:**
   - **Mac:**
     ```bash
     source .venv/bin/activate
     ```
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```

4. **Set Python Instance for IDE:**
   - **Mac:**
     ```bash
     which python
     ```
   - **Windows:**
     ```bash
     where python
     ```
   - Use the output to set the Python instance in your IDE.

5. **Add Crews to the Flow:**
   - Create a crew named `shakespeare_crew` to generate X posts:
     ```bash
     crewai flow add-crew shakespeare_crew
     ```
   - Create a crew named `x_post_review_crew` to review the posts created by `shakespeare_crew`:
     ```bash
     crewai flow add-crew x_post_review_crew
     ```

