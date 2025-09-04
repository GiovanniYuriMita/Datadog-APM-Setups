<?php
namespace App\Middleware;

class DatadogMiddleware
{
    /**
     * Processes the incoming HTTP request to add relevant Datadog span tags.
     *
     * @param string $rawInput The raw body of the HTTP request.
     * @param array|null $decodedPayload The decoded payload (e.g., from JSON), if available.
     * @param string $contentType The Content-Type header of the request.
     */
    public static function addRequestPayloadTags(string $rawInput, $decodedPayload, string $contentType): void
    {
        // Ensure the Datadog Tracer is available
        if (!function_exists('\DDTrace\active_span')) {
            error_log("[DDTrace Middleware] DDTrace extension not loaded or active_span() is undefined.");
            return;
        }

        $apiSpan = \DDTrace\active_span();

        if (!$apiSpan) {
            // No active span to tag. This can happen if tracing is disabled or not initiated.
            return;
        }

        // Add the full raw body as a tag, but only if it's considered "text"
        if (str_starts_with($contentType, 'text/') ||
            str_starts_with($contentType, 'application/json') ||
            str_starts_with($contentType, 'application/x-www-form-urlencoded') ||
            str_starts_with($contentType, 'application/xml')) {
            
            // Limit the size of the raw body tag to prevent excessively large spans
            $maxLength = 4096;
            $apiSpan->meta["http.request.body_raw"] = substr($rawInput, 0, $maxLength);
            if (strlen($rawInput) > $maxLength) {
                $apiSpan->meta["http.request.body_raw_truncated"] = 'true';
            }
        }

        // Add individual tags from a decoded array payload
        // if (is_array($decodedPayload)) {
        //     foreach ($decodedPayload as $key => $value) {
        //         // Only tag scalar values to avoid large/complex data structures
        //         if (is_scalar($value)) {
        //             // Prepend with a distinct prefix to avoid conflicts and provide clarity
        //             $apiSpan->meta["http.payload.$key"] = (string)$value;
        //         }
        //     }
        // }
    }
}

?>