# C-Datadog-APM
 A perfect and functional Datadog Tracer for C Language. 

# Datadog Tracer on C using dd-opentracing-cpp

This project demonstrates how to use the Datadog tracer in a C application with the `dd-opentracing-cpp` library. The setup includes a C++ wrapper to expose `dd-opentracing-cpp` features to C, along with Docker configuration to facilitate easy deployment and testing.

## Project Structure

- `src/trace_wrapper.cpp`: Wrapper to make the `dd-opentracing-cpp` features available in C.
- `src/main.c`: The main application written in C.
- `include/trace_wrapper.h`: Headers for `trace_wrapper`.
- `CMakeLists.txt`: Instructions for CMake to build the application's dependencies.
- `Dockerfile`: Contains all the steps to download the dependencies related to `dd-opentracing-cpp`.
- `index.html`: The HTML page for the web interface.
- `docker-compose.yaml`: Docker Compose configuration for the two containers: Datadog Agent and the C application with the required Datadog environment variables.

## Requirements

- Docker
- Docker Compose

## Setup Instructions

1. Clone the repository:
    ```sh
    git clone https://github.com/bwsolucoes/C-Datadog-APM.git
    cd <repository_directory>
    ```

2. Build and start the Docker containers:
    ```sh
    docker-compose up --build
    ```

3. After the containers are up and running, open your browser and go to:
    ```
    http://localhost:8888/
    ```

4. Click the "Run C Function" button to execute the C application function and see the traces in Datadog.

## Usage

Simply navigate to the provided URL after running the containers, and interact with the web interface to trigger the tracing function in the C application. The traces will be sent to Datadog, where you can view them in your Datadog dashboard.

## License

This project is licensed under the MIT License.

---

Happy Tracing!
