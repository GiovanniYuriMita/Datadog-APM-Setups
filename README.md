# PHP Datadog APM Instrumentation with Custom Spans and Docker

This is a sample project to test Datadog APM instrumentation in a PHP application using custom spans and Docker. The project demonstrates how to set up a PHP application with Datadog APM, using custom traces, and running the setup in Docker containers.

## Project Structure

.
├── agent
│ └── Dockerfile
├── app
│ ├── Dockerfile
│ └── trace-test.php
├── datadog-setup.php
├── docker-compose.yaml
├── my-apache2.conf
└── README.md


## Prerequisites

### Docker:
- Docker
- Docker Compose
- Datadog account with an API key

### Self-Hosted
- PHP
- Datadog account with an API key

## Setup Instructions - Docker

### 1. Clone the Repository

```sh
git clone https://github.com/bwsolucoes/php-datadog-apm.git
cd php-datadog-apm
```

### 2. Update Datadog API Key

Open docker-compose.yaml and replace <YOUR_DATADOG_API_KEY> with your actual Datadog API key.

### 3. Build and Run the Docker Containers

```sh
docker-compose -f docker-compose.yaml build
docker-compose -f docker-compose.yaml up -d
```

### 4. Access the Application

Open your web browser and navigate to:

http://localhost:8080/trace-test.php

This page will have a button to trigger custom spans in the PHP application, and you can monitor the traces in Datadog APM.

## Setup Instructions - Self-Hosted

### 1. Clone the Repository

```sh
git clone https://github.com/bwsolucoes/php-datadog-apm.git
cd php-datadog-apm
```

### 2. Install the Datadog PHP Tracing Client

```sh
php datadog-setup.php --php-bin=all
```

### 3. Serve the PHP Application:

Serve the trace-test.php file using your preferred method (e.g., built-in PHP server, Apache, Nginx).

Example using PHP built-in server:

```sh
php -S localhost:8080 trace-test.php
```

### 4. Access the Application

Open your web browser and navigate to:

http://localhost:8080/trace-test.php

# License
This project is licensed under the MIT License. See the LICENSE file for details.

# Acknowledgements
This project uses the following open-source projects:

Docker
Datadog APM
PHP


Happy tracing!