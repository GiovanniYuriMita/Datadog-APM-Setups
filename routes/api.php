<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ApiController;

Route::get('/health', [ApiController::class, 'health'])->name('api.health');
Route::post('/echo', [ApiController::class, 'echo'])->name('api.echo');
Route::post('/process', [ApiController::class, 'processData'])->name('api.process');
Route::get('/error', [ApiController::class, 'generateError'])->name('api.error');
Route::get('/database', [ApiController::class, 'databaseQuery'])->name('api.database');
Route::get('/external', [ApiController::class, 'externalApi'])->name('api.external');

// Custom traced function endpoint
Route::post('/custom-function', function (Request $request) {
    $data = $request->json()->all();
    
    // This will be traced by DDTrace
    $result = customProcessFunction($data['id'] ?? 'default', $data['content'] ?? 'no content');
    
    return response()->json([
        'status' => 'success',
        'result' => $result,
        'timestamp' => now()->toISOString()
    ]);
})->name('api.custom-function');

// Custom traced function
function customProcessFunction(string $id, string $content): string
{
    // Simulate processing
    usleep(rand(100000, 300000)); // 100-300ms
    
    return "Processed: {$content} (ID: {$id})";
}

// Define custom trace for the function
if (function_exists('\DDTrace\trace_function')) {
    \DDTrace\trace_function('customProcessFunction', function (\DDTrace\SpanData $span, $args) {
        $span->name = 'CustomFunction.process';
        $span->resource = 'custom_function_' . ($args[0] ?? 'unknown');
        $span->meta['function.id'] = $args[0] ?? 'unknown';
        $span->meta['function.content'] = $args[1] ?? 'unknown';
        $span->meta['function.type'] = 'custom_processing';
    });
}