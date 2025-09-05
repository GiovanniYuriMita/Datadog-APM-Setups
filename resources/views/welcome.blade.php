<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laravel Datadog APM Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f8fafc;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2d3748;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #718096;
            margin-bottom: 30px;
        }
        .endpoint {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
        }
        .method {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
        }
        .get { background: #c6f6d5; color: #22543d; }
        .post { background: #bee3f8; color: #2a4365; }
        .url {
            font-family: 'Monaco', 'Menlo', monospace;
            color: #2d3748;
        }
        .description {
            color: #4a5568;
            margin-top: 8px;
            font-size: 14px;
        }
        .test-button {
            background: #4299e1;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
            font-size: 14px;
        }
        .test-button:hover {
            background: #3182ce;
        }
        .status {
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-weight: bold;
        }
        .success { background: #c6f6d5; color: #22543d; }
        .error { background: #fed7d7; color: #c53030; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Laravel Datadog APM Demo</h1>
        <p class="subtitle">Test endpoints to generate traces for Datadog APM monitoring</p>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="url">/api/health</span>
            <div class="description">Health check endpoint</div>
            <button class="test-button" onclick="testEndpoint('GET', '/api/health')">Test</button>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="url">/api/echo</span>
            <div class="description">Echo back request data</div>
            <button class="test-button" onclick="testEcho()">Test</button>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="url">/api/process</span>
            <div class="description">Process data with custom span</div>
            <button class="test-button" onclick="testProcess()">Test</button>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="url">/api/custom-function</span>
            <div class="description">Custom traced function</div>
            <button class="test-button" onclick="testCustomFunction()">Test</button>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="url">/api/database</span>
            <div class="description">Simulate database query</div>
            <button class="test-button" onclick="testDatabase()">Test</button>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="url">/api/external</span>
            <div class="description">Simulate external API call</div>
            <button class="test-button" onclick="testExternal()">Test</button>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="url">/api/error</span>
            <div class="description">Generate error for testing</div>
            <button class="test-button" onclick="testError()">Test</button>
        </div>

        <div id="status"></div>
    </div>

    <script>
        function showStatus(message, isError = false) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${isError ? 'error' : 'success'}">${message}</div>`;
            setTimeout(() => statusDiv.innerHTML = '', 3000);
        }

        async function testEndpoint(method, url, data = null) {
            try {
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                };
                
                if (data) {
                    options.body = JSON.stringify(data);
                }

                const response = await fetch(url, options);
                const result = await response.json();
                
                showStatus(`${method} ${url} - Status: ${response.status} - Response: ${JSON.stringify(result).substring(0, 100)}...`);
            } catch (error) {
                showStatus(`Error testing ${method} ${url}: ${error.message}`, true);
            }
        }

        function testEcho() {
            testEndpoint('POST', '/api/echo', {
                message: 'Hello from frontend!',
                timestamp: new Date().toISOString(),
                test_data: { id: 123, name: 'Test User' }
            });
        }

        function testProcess() {
            testEndpoint('POST', '/api/process', {
                id: 'process-123',
                data: ['item1', 'item2', 'item3'],
                config: { timeout: 5000, retries: 3 },
                metadata: { source: 'frontend', version: '1.0.0' }
            });
        }

        function testCustomFunction() {
            testEndpoint('POST', '/api/custom-function', {
                id: 'custom-456',
                content: 'Custom function test data'
            });
        }

        function testDatabase() {
            testEndpoint('GET', '/api/database?q=SELECT * FROM users WHERE active = 1');
        }

        function testExternal() {
            testEndpoint('GET', '/api/external?endpoint=users');
        }

        function testError() {
            testEndpoint('GET', '/api/error?type=validation');
        }
    </script>
</body>
</html>