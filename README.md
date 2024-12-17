# Python Datadog APM with Custom Spans and Dynamic Instrumentation

This is a sample project to demonstrate Datadog APM instrumentation in a Python application using custom spans and dynamic instrumentation with Docker. The project illustrates setting up a Python application with Datadog APM, utilizing custom traces, and running the setup in Docker containers.

## Project Structure

```
.
├── .github/workflows
│   └── ci.yml
├── app
│   └── app.py
├── .gitattributes
├── Dockerfile
├── LICENSE
├── README.md
└── docker-compose.yaml
```

## Prerequisites

### Docker:
- Docker
- Docker Compose

### Self-Hosted
- Python
- Datadog Agent

## Setup Instructions - Docker

### 1. Clone the Repository

```sh
git clone https://github.com/bwsolucoes/python-datadog-apm.git
cd python-datadog-apm
```

### 2. Build and Run the Docker Containers

```sh
docker-compose up --build
```

## Setup Instructions - Self-Hosted

### 1. Install the Datadog Agent on Your Local Machine 

https://app.datadoghq.com/account/settings/agent/latest?platform=overview

### 2. Clone the Repository

```sh
git clone https://github.com/bwsolucoes/python-datadog-apm.git
cd python-datadog-apm
```

### 3. Install Dependencies

Install the required dependencies using pip:

```sh
pip install --upgrade pip
pip install dd-trace
```

### 4. Run the Application

Run the Python application:

```sh
python app/app.py
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements
This project uses the following open-source projects:
- Docker
- Docker-compose
- Datadog Python Tracer
- Python

Happy tracing!
