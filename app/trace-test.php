<?php
require __DIR__ . '/../vendor/autoload.php';

use Laminas\Log\Logger;
use Laminas\Log\Writer\Stream;
use Laminas\Log\Formatter\Simple;

// Function to get trace and span IDs for logging
function getTraceSpanIds() {
    try {
        $traceId = Tracer::getTraceId();
        $spanId = Tracer::getSpanId();
        return sprintf(' [dd.trace_id=%s dd.span_id=%s]', $traceId, $spanId);
    } catch (Exception $e) {
        // Log any errors in fetching trace/span IDs
        error_log('Error fetching trace/span IDs: ' . $e->getMessage());
        return ' [dd.trace_id=NA dd.span_id=NA]';
    }
}

// Custom formatter to include trace and span IDs
class CustomFormatter extends Simple {
    public function format($event) {
        $traceSpanIds = getTraceSpanIds();
        $event['message'] .= $traceSpanIds;
        return parent::format($event);
    }
}

// Set up Laminas logger
$logger = new Logger;
$logDir = __DIR__ . '../logs/php-logs.log';
$writer = new Stream($logDir . '/php-logs.log');
$formatter = new Simple('%timestamp% %priorityName% (%priority%): %message% %extra%' . PHP_EOL);
$writer->setFormatter($formatter);
$logger->addWriter($writer);

// Make the logger available globally
$GLOBALS['logger'] = $logger;

// ----------------- Traces Definitions
\DDTrace\trace_function('chofs', function (\DDTrace\SpanData $span, $args) {
    $span->name = 'CustomSpanPHP';
    $span->resource = 'ResourceABC' . $args[0];
    $span->service = 'bw-php';
    $span->meta['endpoint'] = $args[1];
});

\DDTrace\trace_method('ProcessingStage1', 'process', function (\DDTrace\SpanData $span, $args) {
    $span->service = 'bw-php';
    $span->resource = 'message:' . $args[0];
}); 

// -----------------

function chofs($id, $content) {
    global $logger;
    $logger->info("Function chofs called with id: $id and content: $content");
    echo "Function chofs called with id: $id and content: $content<br>";
}

class ProcessingStage1 {
    public function process($message) {
        global $logger;
        $logger->info("Processing stage 1 with message: $message");
        echo "Processing stage 1 with message: $message<br>";
    }
}

if (isset($_POST['action']) && $_POST['action'] == 'call_function') {
    chofs(123, 'https://app.datadoghq.com');
    $stage1 = new ProcessingStage1();
    $stage1->process('Hello from Stage 1');
    return;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Trace Test</title>
</head>
<body>
    <button id="traceButton">Call chofs</button>
    <script>
        document.getElementById('traceButton').addEventListener('click', function() {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "trace-test.php", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.onload = function() {
                if (xhr.status === 200) {
                    alert('Function called successfully!');
                } else {
                    alert('Request failed.  Returned status of ' + xhr.status);
                }
            };
            xhr.send("action=call_function");
        });
    </script>
</body>
</html>