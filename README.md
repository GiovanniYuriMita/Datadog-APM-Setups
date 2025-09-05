# Laravel Datadog APM Demo

A simple Laravel 11 application with PHP 8.3 that demonstrates Datadog APM integration using custom middleware for creating spans and capturing request payloads.

## Features

- **Laravel 11** with PHP 8.3
- **Datadog APM Integration** with custom middleware
- **Request/Response Tracing** with payload capture
- **Custom Spans** for specific functions
- **Error Tracking** and performance monitoring
- **Docker Support** with Datadog Agent
- **Test Scripts** for generating traces

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Datadog API Key (optional, for sending traces to Datadog)

### 1. Set up Datadog API Key (Optional)

If you want to send traces to Datadog, set your API key:

```bash
export DD_API_KEY=your-datadog-api-key-here
```

**⚠️ Security Note**: Never commit your actual API key to the repository. The `docker-compose.yaml` file uses environment variables to safely handle sensitive data.

### 2. Build and Run

```bash
# Build and start the application
docker-compose up -d

# Check if containers are running
docker-compose ps
```

### 3. Test the Application

```bash
# Run the test script to generate traces
./test-traces.sh

# Or test manually
curl http://localhost:8080/api/health
```

### 4. View Traces

- **Web Interface**: http://localhost:8080
- **API Health**: http://localhost:8080/api/health
- **Datadog Dashboard**: Check your Datadog APM dashboard for traces

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/echo` | Echo back request data |
| POST | `/api/process` | Process data with custom span |
| POST | `/api/custom-function` | Custom traced function |
| GET | `/api/database` | Simulate database query |
| GET | `/api/external` | Simulate external API call |
| GET | `/api/error` | Generate error for testing |

## Datadog APM Features

### Custom Middleware

The `DatadogTracingMiddleware` automatically:

- Captures HTTP request/response details
- Adds request payload as span tags
- Tracks performance metrics
- Handles error tracking
- Adds custom metadata

### Custom Spans

- **Custom Function Spans**: Traced functions with custom metadata
- **Request Spans**: Automatic HTTP request tracing
- **Error Spans**: Error tracking and stack traces

### Trace Tags

The middleware adds comprehensive tags:

- `http.method`, `http.url`, `http.status_code`
- `http.request.body_raw` (truncated for large payloads)
- `http.payload.*` (JSON payload fields)
- `laravel.route.name`, `laravel.route.action`
- Custom business logic tags

## Configuration

### Environment Variables

```bash
# Datadog APM Configuration
DD_AGENT_HOST=datadog-agent
DD_TRACE_AGENT_PORT=8126
DD_ENV=local
DD_SERVICE=laravel-datadog-apm
DD_VERSION=1.0.0
DD_TRACE_DEBUG=true
DD_TRACE_SAMPLE_RATE=1.0
DD_TRACE_ANALYTICS_ENABLED=true
DD_TRACE_AUTO_FLUSH_ENABLED=true
DD_TRACE_GENERATE_ROOT_SPAN=true
DD_TRACE_URL_AS_RESOURCE_NAMES_ENABLED=true
DD_TAGS=env:local,service:laravel-datadog-apm
DD_LOGS_ENABLED=true
DD_LOGS_INJECTION=true
DD_PROFILING_ENABLED=true
```

### Docker Services

- **laravel-app**: PHP 8.3 with Laravel 11 and Datadog extension
- **datadog-agent**: Datadog Agent for trace collection

## Development

### Adding Custom Traces

```php
// In your routes or controllers
\DDTrace\trace_function('myFunction', function (\DDTrace\SpanData $span, $args) {
    $span->name = 'CustomSpan.myFunction';
    $span->resource = 'my_resource';
    $span->meta['custom.tag'] = 'value';
});
```

### Custom Middleware

The `DatadogTracingMiddleware` is automatically registered as global middleware in `bootstrap/app.php`.

## Troubleshooting

### Check Container Logs

```bash
# Laravel application logs
docker-compose logs laravel-app

# Datadog agent logs
docker-compose logs datadog-agent
```

### Verify Datadog Extension

```bash
# Check if DDTrace extension is loaded
docker exec -it datadog-apm-setups-laravel-app-1 php -m | grep ddtrace
```

### Test Trace Generation

```bash
# Run the test script
./test-traces.sh

# Check for trace output in logs
docker-compose logs laravel-app | grep "ddtrace"
```

## File Structure

```
├── app/
│   └── Http/
│       ├── Controllers/
│       │   └── ApiController.php
│       └── Middleware/
│           └── DatadogTracingMiddleware.php
├── bootstrap/
│   └── app.php
├── public/
│   └── index.php
├── resources/
│   └── views/
│       └── welcome.blade.php
├── routes/
│   ├── api.php
│   ├── web.php
│   └── console.php
├── composer.json
├── Dockerfile
├── docker-compose.yaml
├── test-traces.sh
└── README.md
```

## License

This project is open-sourced software licensed under the [MIT license](LICENSE).