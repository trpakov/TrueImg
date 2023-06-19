# TrueImg - Image Watermarking Made Easy

## Setup

All of the following commands assume that you are located in the project root directory.

### Running locally

1. Create a virtual Python environment using your preferred tool (venv, virtualenv, conda) to avoid conflicts:
```
python -m venv .venv
```

2. Install requirements from ```requirements.txt```:
```
python -m pip install -r requirements.txt
```

3. Start the server by running ```main.py``` or issuing the following command:
```
uvicorn main:app --host 0.0.0.0 --port 8000
```
The frontend should be accessible from [http://localhost:8000/](http://localhost:8000/).

### Running with Docker Compose

1. Ensure that you have the following installed on your system: 
   - Docker: https://www.docker.com/get-started
   - Docker Compose: https://docs.docker.com/compose/install/

2. Modify the Docker Compose configuration (optional):

    If needed, you can modify the docker-compose.yml file to customize the project configuration. This file defines the services and their configurations. Make sure to review and adjust any environment variables, ports, volumes, or other settings according to your requirements.

3. Build the Docker containers:
    ```
    docker-compose build
    ```
    This command builds the Docker images defined in the docker-compose.yml file. It ensures that all the necessary dependencies are available in the containers.

4. Start the project:
    ```
    docker-compose up
    ```
    This command starts the project containers in the foreground and displays their logs. You should see the output of each service in the terminal. If everything is set up correctly, you can access the running application using the appropriate URL or port.

    If you prefer to run the containers in the background, you can use the `-d` flag:
    ```
    docker-compose up -d
    ```

    Again, the frontend should be accessible from [http://localhost:8000/](http://localhost:8000/).

5. Stop the project:

    To stop the running project and remove the containers, use the following command:
    ```
    docker-compose down
    ```
    This command stops and removes the project containers.