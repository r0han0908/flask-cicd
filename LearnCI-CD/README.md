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
```

### 2️⃣ Docker Image Build & Push Workflow

```yaml
# 👇 Name of the pipeline
name: Docker Image CI

# 👇 The triggers that start the workflow
on:
  push:
    branches: [ "main" ]     # Run when code is pushed to main
  pull_request:
    branches: [ "main" ]     # Run when a PR targets main

# 👇 The jobs section
jobs:
  build:
    runs-on: ubuntu-latest   # GitHub-hosted Ubuntu runner

    steps:
    - name: Checkout Code
      uses: actions/checkout@v4
      # Pulls repository code

    - name: Docker Login
      uses: docker/login-action@v3.6.0
      with: 
        username: ${{ secrets.DOCKER_HUB_USERNAME }} 
        password: ${{ secrets.DOCKER_HUB_TOKEN }}
      # Authenticates to Docker Hub using GitHub Secrets

    - name: Set image variables
      run: |
        echo "IMAGE_NAME=my-social-media" >> $GITHUB_ENV
        echo "TAG=v1" >> $GITHUB_ENV
      # Sets environment variables for image name and tag

    - name: Build the Docker image
      run: docker build . -t ${{ secrets.DOCKER_HUB_USERNAME }}/$IMAGE_NAME:$TAG
      # Builds the Docker image

    - name: Docker Push to Registry
      run: docker push ${{ secrets.DOCKER_HUB_USERNAME }}/$IMAGE_NAME:$TAG
      # Pushes the built image to Docker Hub

    - name: Notifying through slack (IF Successful)
      if: ${{ !failure() }}
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      run: |
        curl -X POST -H 'Content-type: application/json' \
        --data '{"text": "The Docker Workflow pipeline was successful!!"}' \
        $SLACK_WEBHOOK_URL
      # Sends a success notification to Slack

    - name: Notifying through slack (IF Failure!)
      if: ${{ failure() }}
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      run: |
        curl -X POST -H 'Content-type: application/json' \
        --data '{"text": "The Docker Workflow pipeline was not successful!!"}' \
        $SLACK_WEBHOOK_URL
      # Sends a failure notification to Slack
```




📅 Update Log

2025-09-25 → Initial pipeline created with:
Checkout, dependencies install, and test run.

2025-09-26 → Added Slack Notification Step:
Sends a message to the Slack workspace once the CI pipeline succeeds.
Uses GitHub Secrets for the webhook URL (SLACK_WEBHOOK_URL).
Includes repo name and branch in the message.

2025-09-30 → Added Docker Image CI Workflow:

Builds Docker images for the project.

Pushes images to Docker Hub.

Sends Slack notifications on success or failure.
