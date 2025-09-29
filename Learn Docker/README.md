## 🐳 Containerizing the Application

This is a simple example of how you can containerize the Flask Social Connect application using Docker. Docker allows you to package your application with all its dependencies into a lightweight, portable container.

### Our Dockerfile

The project includes a [`Dockerfile`](../Dockerfile) in the root directory.

**What each line does:**

- **`FROM python:3.9-slim`**: Uses a lightweight Python 3.9 image as the foundation (~45MB vs 900MB+ for full Python)
- **`WORKDIR /app`**: Sets `/app` as the working directory inside the container
- **`COPY . .`**: Copies all files from your project directory to `/app` in the container
- **`RUN apt-get update`**: Updates the package manager inside the container
- **`RUN pip install -r requirements.txt`**: Installs all Python dependencies from [`requirements.txt`](../requirements.txt)
- **`EXPOSE 5000`**: Documents that the app uses port 5000 (Flask's default port)
- **`CMD ["python", "run.py"]`**: Starts the Flask application using our [`run.py`](../run.py) file


### Building and Running the Docker Image

#### 1. Build the Docker Image
```bash
# Build the image and tag it as 'flask-socialconnect'
docker build -t flask-socialconnect .
```

#### 2. Run the Container
```bash
# Run the container and map port 5000 to your local machine
docker run -p 5000:5000 flask-socialconnect
```

#### 3. Test Your Docker Image

**Step 1:** Check if the container is running
```bash
docker ps
```
You should see your container listed with status "Up".

**Step 2:** Test the application
Open your web browser and navigate to:
```
http://localhost:5000
```
You should see the Flask Social Connect application homepage.

**Step 3:** Check container logs (if something goes wrong)
```bash
# Replace <container-id> with the actual ID from 'docker ps'
docker logs <container-id>
```

**Step 4:** Stop the container when done
```bash
# Find the container ID
docker ps

# Stop the container
docker stop <container-id>
```

### Troubleshooting

If you can't access the application:

1. **Verify the build completed successfully**: Check for any errors during `docker build`
2. **Check port mapping**: Ensure you're using `-p 5000:5000` when running the container
3. **Verify Flask configuration**: The app should show `Running on all addresses (0.0.0.0)` in the logs
4. **Check container logs**: Use `docker logs <container-id>` to see any error messages
5. **Test inside container**: 
   ```bash
   docker exec -it <container-id> curl http://localhost:5000
   ```

### Docker Commands Cheat Sheet

```bash
# Build image
docker build -t flask-socialconnect .

# Run container in background
docker run -d -p 5000:5000 --name my-flask-app flask-socialconnect

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Stop container
docker stop my-flask-app

# Remove container
docker rm my-flask-app

# Remove image
docker rmi flask-socialconnect

# View container logs
docker logs my-flask-app

# Access container shell
docker exec -it my-flask-app /bin/bash
```

🎉 **Success!** If you can access `http://localhost:5000` and see your Flask application, your Docker containerization is working perfectly!
