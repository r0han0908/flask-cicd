# 🚀 CI/CD Pipeline – First Steps

This project uses **GitHub Actions** for its CI/CD pipeline.  
The pipeline ensures code quality, runs tests, and notifies the team via Slack when builds succeed.  
We’ll continue to extend this as the project grows.  

---

## 📄 Current Workflow File (with explanations)

```yaml
# 👇 Name of the pipeline
name: start-ci
# This gives the workflow a name. You’ll see it in the GitHub Actions tab.

# 👇 The triggers that start the workflow
on:
  push:
    branches:
      - main       # Run when code is pushed to the main branch
  pull_request:
    branches: [main]  # Run when a pull request targets main

  workflow_dispatch:  # Allows manual runs from the GitHub Actions UI

# 👇 The jobs section (defines what tasks the workflow will do)
jobs:
  build-test:          # Job name
    runs-on: ubuntu-latest   # The environment (GitHub provides an Ubuntu VM)

    # 👇 Steps inside the job
    steps:
      - name: Checkout Code
        uses: actions/checkout@v5.0.0
        # This pulls the repository code into the runner so we can use it.

      - name: Setting up Python Dependencies
        uses: actions/setup-python@v6.0.0
        # This sets up a Python environment in the runner.

      - name: Install Dependencies For the application
        run: pip install -r requirements.txt
        # Installs all required packages from requirements.txt

      - name: Run the test
        run: python3 -m pytest tests/ -v
        # Runs all tests in the tests/ folder with verbose output

      - name: Notifying through slack
        env:
          SLACK_WEBHOOK_URL : {{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          curl -X POST -H 'Content-type: applicaiton/json' \
          --data '{"text": "The CI pipeline was successful!!"}' \
          $$SLACK_WEBHOOK_URL
        # Sends a notification to Slack when the pipeline completes successfully

📅 Update Log

2025-09-25 → Initial pipeline created with:

Checkout, dependencies install, and test run.

2025-09-26 → Added Slack Notification Step:

Sends a message to the Slack workspace once the CI pipeline succeeds.

Uses GitHub Secrets for the webhook URL (SLACK_WEBHOOK_URL).

Includes repo name and branch in the message.