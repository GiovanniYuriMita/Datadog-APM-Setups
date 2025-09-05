<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\Response;

class DatadogTracingMiddleware
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        // Start tracing if DDTrace is available
        if (function_exists('\DDTrace\trace_method')) {
            $this->startRequestTracing($request);
        }

        $response = $next($request);

        // Add response information to traces
        if (function_exists('\DDTrace\active_span')) {
            $this->addResponseTags($request, $response);
        }

        return $response;
    }

    /**
     * Start request tracing and add request payload tags
     */
    private function startRequestTracing(Request $request): void
    {
        try {
            // Get the active span
            $span = \DDTrace\active_span();
            
            if (!$span) {
                return;
            }

            // Set a clean resource name following Datadog best practices
            $this->setResourceName($request, $span);

            // Add request information
            $span->meta['http.method'] = $request->method();
            $span->meta['http.url'] = $request->fullUrl();
            $span->meta['http.route'] = $request->route()?->uri() ?? $request->path();
            $span->meta['http.user_agent'] = $request->userAgent();
            $span->meta['http.request_id'] = $request->header('X-Request-ID', uniqid());

            // Add request payload information
            $this->addRequestPayloadTags($request, $span);

            // Add custom tags based on route
            $this->addRouteSpecificTags($request, $span);

        } catch (\Exception $e) {
            Log::error('Datadog tracing error: ' . $e->getMessage());
        }
    }

    /**
     * Set a clean resource name following Datadog best practices
     */
    private function setResourceName(Request $request, $span): void
    {
        $method = $request->method();
        $path = $request->path();
        
        // Get route name if available, otherwise use the path
        $route = $request->route();
        $routeName = $route?->getName();
        
        if ($routeName && $routeName !== 'unnamed') {
            // Use named route: METHOD route_name
            $span->resource = "{$method} {$routeName}";
        } else {
            // Use path: METHOD /path
            $span->resource = "{$method} /{$path}";
        }
    }

    /**
     * Add request payload tags to the span
     */
    private function addRequestPayloadTags(Request $request, $span): void
    {
        $contentType = $request->header('Content-Type', '');
        
        // Get raw input
        $rawInput = $request->getContent();
        
        // Add raw body if it's text-based content
        if ($this->isTextContent($contentType) && !empty($rawInput)) {
            $maxLength = 4096;
            $span->meta['http.request.body_raw'] = substr($rawInput, 0, $maxLength);
            
            if (strlen($rawInput) > $maxLength) {
                $span->meta['http.request.body_raw_truncated'] = 'true';
            }
        }

        // Add JSON payload tags if applicable
        if (str_contains($contentType, 'application/json') && $request->isJson()) {
            $payload = $request->json()->all();
            $this->addPayloadTags($payload, $span);
        }

        // Add form data tags
        if ($request->isMethod('POST') && $request->hasAny(['id', 'content', 'message'])) {
            $this->addFormDataTags($request, $span);
        }
    }

    /**
     * Add payload tags from decoded data
     */
    private function addPayloadTags(array $payload, $span): void
    {
        foreach ($payload as $key => $value) {
            if (is_scalar($value)) {
                $span->meta["http.payload.{$key}"] = (string) $value;
            } elseif (is_array($value) && count($value) <= 10) {
                // Only add small arrays to avoid span bloat
                $span->meta["http.payload.{$key}"] = json_encode($value);
            }
        }
    }

    /**
     * Add form data tags
     */
    private function addFormDataTags(Request $request, $span): void
    {
        $formData = $request->only(['id', 'content', 'message']);
        foreach ($formData as $key => $value) {
            if (!empty($value)) {
                $span->meta["http.form.{$key}"] = (string) $value;
            }
        }
    }

    /**
     * Add route-specific tags
     */
    private function addRouteSpecificTags(Request $request, $span): void
    {
        $route = $request->route();
        if (!$route) {
            return;
        }

        $span->meta['laravel.route.name'] = $route->getName() ?? 'unnamed';
        $span->meta['laravel.route.action'] = $route->getActionName();
        
        // Add route parameters
        $parameters = $route->parameters();
        foreach ($parameters as $key => $value) {
            if (is_scalar($value)) {
                $span->meta["laravel.route.param.{$key}"] = (string) $value;
            }
        }
    }

    /**
     * Add response tags
     */
    private function addResponseTags(Request $request, Response $response): void
    {
        try {
            $span = \DDTrace\active_span();
            
            if (!$span) {
                return;
            }

            $span->meta['http.status_code'] = (string) $response->getStatusCode();
            $span->meta['http.response.size'] = (string) strlen($response->getContent());

            // Add response time
            $span->meta['http.response.time_ms'] = (string) round((microtime(true) - LARAVEL_START) * 1000, 2);

        } catch (\Exception $e) {
            Log::error('Datadog response tagging error: ' . $e->getMessage());
        }
    }

    /**
     * Check if content type is text-based
     */
    private function isTextContent(string $contentType): bool
    {
        $textTypes = [
            'text/',
            'application/json',
            'application/x-www-form-urlencoded',
            'application/xml',
            'application/javascript',
        ];

        foreach ($textTypes as $type) {
            if (str_starts_with($contentType, $type)) {
                return true;
            }
        }

        return false;
    }
}