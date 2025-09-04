<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Autoloading: A simple spl_autoload_register for this example
spl_autoload_register(function ($class) {
    $file = __DIR__ . '/' . str_replace('\\', '/', $class) . '.php';
    if (file_exists($file)) {
        require_once $file;
    }
});

// ----------------- Datadog Traces Definitions -----------------
require_once __DIR__ . '/DatadogTraces.php';

// ----------------- Core API Logic -----------------

// Set content type header for JSON responses
header('Content-Type: application/json');

$method = $_SERVER['REQUEST_METHOD'];

$rawInput = file_get_contents('php://input'); // Read raw input once
$contentType = $_SERVER['CONTENT_TYPE'] ?? ''; // Get Content-Type header

$payload = null;

// Attempt to decode payload based on Content-Type
if (str_starts_with($contentType, 'application/json')) {
    $payload = json_decode($rawInput, true);
    if (json_last_error() !== JSON_ERROR_NONE && !empty($rawInput)) {
        error_log("JSON decoding error: " . json_last_error_msg());
    }
} 

// ----------------- Datadog Middleware Integration -----------------
// Call the isolated middleware
\App\Middleware\DatadogMiddleware::addRequestPayloadTags($rawInput, $payload, $contentType);
// ----------------- END Datadog Middleware Integration -----------------


$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path_segments = explode('/', trim($path, '/'));

switch ($path) {
    case '/api/call_function':
        if ($method === 'POST') {
            if (isset($payload['id']) && isset($payload['content'])) {
                chofs($payload['id'], $payload['content']);
                echo json_encode(['status' => 'success', 'message' => 'chofs function called']);
            } else {
                http_response_code(400); // Bad Request
                echo json_encode(['status' => 'error', 'message' => 'Missing "id" or "content" in payload']);
            }
        } else {
            http_response_code(405); // Method Not Allowed
            echo json_encode(['status' => 'error', 'message' => 'Method Not Allowed']);
        }
        break;

    case '/api/process_stage1':
        if ($method === 'POST') {
            if (isset($payload['message'])) {
                $stage1 = new ProcessingStage1();
                $stage1->process($payload['message']);
                echo json_encode(['status' => 'success', 'message' => 'ProcessingStage1 processed']);
            } else {
                http_response_code(400); // Bad Request
                echo json_encode(['status' => 'error', 'message' => 'Missing "message" in payload']);
            }
        } else {
            http_response_code(405); // Method Not Allowed
            echo json_encode(['status' => 'error', 'message' => 'Method Not Allowed']);
        }
        break;

    default:
        http_response_code(404); // Not Found
        echo json_encode(['status' => 'error', 'message' => 'Endpoint Not Found']);
        break;
}

// ----------------- Your Original Functions/Classes -----------------

function chofs($id, $content) {
    error_log("Function chofs called with id: $id and content: $content");
}

class ProcessingStage1 {
    public function process($message) {
        error_log("Processing stage 1 with message: $message");
    }
}
?>