<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Routing\Controller;
use Illuminate\Http\JsonResponse;

class ApiController extends Controller
{
    /**
     * Health check endpoint
     */
    public function health(): JsonResponse
    {
        return response()->json([
            'status' => 'healthy',
            'timestamp' => now()->toISOString(),
            'service' => 'laravel-datadog-apm',
            'version' => '1.0.0'
        ]);
    }

    /**
     * Simple echo endpoint
     */
    public function echo(Request $request): JsonResponse
    {
        return response()->json([
            'message' => 'Echo successful',
            'received_data' => $request->all(),
            'headers' => $request->headers->all(),
            'timestamp' => now()->toISOString()
        ]);
    }

    /**
     * Process data endpoint with custom span
     */
    public function processData(Request $request): JsonResponse
    {
        $data = $request->json()->all();
        
        // Simulate some processing time
        usleep(rand(100000, 500000)); // 100-500ms
        
        $result = $this->performDataProcessing($data);
        
        return response()->json([
            'status' => 'processed',
            'result' => $result,
            'processing_time_ms' => round((microtime(true) - LARAVEL_START) * 1000, 2),
            'timestamp' => now()->toISOString()
        ]);
    }

    /**
     * Generate error for testing error tracking
     */
    public function generateError(Request $request): JsonResponse
    {
        $errorType = $request->query('type', 'generic');
        
        switch ($errorType) {
            case 'validation':
                return response()->json(['error' => 'Validation failed'], 422);
            case 'not_found':
                return response()->json(['error' => 'Resource not found'], 404);
            case 'server':
                return response()->json(['error' => 'Internal server error'], 500);
            default:
                throw new \Exception('Test error for Datadog APM');
        }
    }

    /**
     * Database simulation endpoint
     */
    public function databaseQuery(Request $request): JsonResponse
    {
        $query = $request->query('q', 'SELECT * FROM users');
        
        // Simulate database query time
        usleep(rand(50000, 200000)); // 50-200ms
        
        return response()->json([
            'query' => $query,
            'results' => [
                ['id' => 1, 'name' => 'John Doe', 'email' => 'john@example.com'],
                ['id' => 2, 'name' => 'Jane Smith', 'email' => 'jane@example.com'],
            ],
            'execution_time_ms' => round((microtime(true) - LARAVEL_START) * 1000, 2),
            'timestamp' => now()->toISOString()
        ]);
    }

    /**
     * External API simulation
     */
    public function externalApi(Request $request): JsonResponse
    {
        $endpoint = $request->query('endpoint', 'users');
        
        // Simulate external API call
        usleep(rand(200000, 800000)); // 200-800ms
        
        return response()->json([
            'external_endpoint' => $endpoint,
            'response_data' => [
                'status' => 'success',
                'data' => "Data from external {$endpoint} API",
                'cached' => false
            ],
            'response_time_ms' => round((microtime(true) - LARAVEL_START) * 1000, 2),
            'timestamp' => now()->toISOString()
        ]);
    }

    /**
     * Perform data processing with custom span
     */
    private function performDataProcessing(array $data): array
    {
        // This method will be traced by DDTrace
        $processed = [];
        
        foreach ($data as $key => $value) {
            if (is_string($value)) {
                $processed[$key] = strtoupper($value);
            } elseif (is_numeric($value)) {
                $processed[$key] = $value * 2;
            } else {
                $processed[$key] = $value;
            }
        }
        
        return $processed;
    }
}