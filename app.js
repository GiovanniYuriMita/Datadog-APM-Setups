const tracer = require('dd-trace').init({
  service: 'poshcash',
  env: 'poshcash-teste',
  port: 8126,
});

const express = require('express');
const app = express();
const path = require('path');

app.use(express.json());

app.use(express.static(path.join(__dirname, 'public')));

app.post('/log', (req, res) => {
  const payload = req.body;
  console.log('Received payload:', payload);

  const span = tracer.scope().active();
  if (span) {
    setSpanTagsFromPayload(span, payload);
  }

  res.send('Payload logged');
});

function setSpanTagsFromPayload(span, payload, prefix = '') {
  for (const key in payload) {
    if (payload.hasOwnProperty(key)) {
      const value = payload[key];
      const tagKey = prefix ? `${prefix}.${key}` : key;

      if (typeof value === 'object' && value !== null) {
        setSpanTagsFromPayload(span, value, tagKey);
      } else {
        span.setTag(tagKey, value);
      }
    }
  }
}

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});
  
app.listen(3000, () => {
  console.log('Server is running on http://localhost:3000');
});
  