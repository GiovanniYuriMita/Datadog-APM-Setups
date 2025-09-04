<?php

if (function_exists('\DDTrace\trace_function')) {
    // Trace custom function `chofs`
    \DDTrace\trace_function('chofs', function (\DDTrace\SpanData $span, $args) {
        $span->name = 'CustomSpanPHP.chofs';
        $span->resource = 'ResourceABC' . (isset($args[0]) ? $args[0] : 'N/A');
        $span->meta['endpoint'] = isset($args[1]) ? $args[1] : 'unknown_endpoint';
    });

    // Trace method `ProcessingStage1::process`
    \DDTrace\trace_method('ProcessingStage1', 'process', function (\DDTrace\SpanData $span, $args) {
        $span->resource = 'message:' . (isset($args[0]) ? $args[0] : 'empty_message');
    });
} else {
    error_log("[DDTrace Definitions] DDTrace extension not loaded. Skipping trace definitions.");
}

?>