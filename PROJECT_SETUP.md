# CrewAI Flows Project Setup Guide

## Prerequisites
- Anaconda or Miniconda installed
- Python 3.12 recommended

## Step-by-Step Setup

### 1. Create a Conda Environment
```bash
conda create --name CONDA_ENV_NAME python=3.12
```
#### Environment Naming Recommendations
- Use a descriptive name that reflects your project's purpose
- Include the technology or framework (e.g., `crewai`)
- Add `_env` suffix to clearly indicate it's a conda environment
- Examples:
  - `marketing_crewai_env`
  - `sales_agent_flows_env`
  - `project_automation_env`

**Naming Convention:**
- Use snake_case (lowercase with underscores)
- Keep it concise but meaningful
- Avoid generic names like `base` or `default`


### 2. Activate the Conda Environment
```bash
conda activate CONDA_ENV_NAME
```

### 3. Install Project Dependencies
```bash
pip install -r requirements.txt
# This will install CrewAI and python-dotenv in this template
```

### 4. Verify Python Environment & Enter into Interpreter Path in IDE
```bash
which python
# Expected output: /opt/anaconda3/envs/CONDA_ENV_NAME/bin/python
```

### 5. Create a New CrewAI Flow Project
```bash
crewai create flow FLOW_NAME
# Snake case is required
```

### 6. Navigate to Project Directory
```bash
cd FLOW_NAME
```

### 7. Install Project-Specific Dependencies
```bash
crewai install
```

## Troubleshooting
- Ensure you have the latest version of CrewAI CLI
- Check that all dependencies are compatible with Python 3.12
- Verify internet connection during installation

## Additional Resources
- [CrewAI Documentation](https://github.com/joaomdmoura/CrewAI)
- [Conda Environment Management](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
