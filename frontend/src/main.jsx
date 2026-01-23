import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { datadogRum } from '@datadog/browser-rum';
import { datadogLogs } from '@datadog/browser-logs';
import version from '../package.json';

datadogRum.init({
    applicationId: '400e1165-3386-4180-86b5-1f3613fc7be9',
    clientToken: 'pubaa37d8325804039175cca91b92d9e5c7',
    site: 'datadoghq.com',
    service: 'chofs-demo',
    env: 'chofs',
    version: version.version,
    sessionSampleRate: 100,
    sessionReplaySampleRate: 100,
    trackBfcacheViews: true,
    defaultPrivacyLevel: 'mask-user-input',
    allowedTracingUrls: [
      (url) => url.startsWith("http://localhost:")

    ],
});

datadogLogs.init({
  clientToken: 'pubaa37d8325804039175cca91b92d9e5c7',
  site: 'datadoghq.com',
  service: 'chofs-demo',
  env: 'chofs',
  version: version.version,
  forwardErrorsToLogs: true,
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
