// Minimal mock API server for local development
// Endpoints:
//  - POST /api/v1/auth/register -> returns fake tourist profile
//  - POST /api/v1/tourists/:id/location -> acknowledges location
//  - POST /api/v1/tourists/:id/panic -> acknowledges panic

const http = require('http');
const url = require('url');

const PORT = 8000;

/**
 * Read request body as JSON safely
 */
function readJson(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', chunk => {
      data += chunk;
      // Protect against excessive payloads
      if (data.length > 1e6) {
        req.socket.destroy();
        reject(new Error('Payload too large'));
      }
    });
    req.on('end', () => {
      if (!data) return resolve({});
      try {
        resolve(JSON.parse(data));
      } catch (e) {
        reject(new Error('Invalid JSON body'));
      }
    });
    req.on('error', reject);
  });
}

function sendJson(res, statusCode, body) {
  const json = JSON.stringify(body);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(json),
  });
  res.end(json);
}

function notFound(res) {
  sendJson(res, 404, { error: 'Not Found' });
}

const server = http.createServer(async (req, res) => {
  const { pathname } = url.parse(req.url || '/', true);
  const method = req.method || 'GET';

  // Health check
  if (method === 'GET' && pathname === '/health') {
    return sendJson(res, 200, { ok: true });
  }

  // Register
  if (method === 'POST' && pathname === '/api/v1/auth/register') {
    try {
      const body = await readJson(req);
      const now = new Date().toISOString();
      return sendJson(res, 200, {
        tourist_id: 'mock-tourist-123',
        name: body?.name || 'Mock User',
        ledger_entry: {
          block_id: 1,
          timestamp: now,
          data_hash: 'mock_data_hash',
          previous_hash: 'mock_previous_hash',
          proof_hash: 'mock_proof_hash',
        },
      });
    } catch (e) {
      return sendJson(res, 400, { error: e.message || 'Bad Request' });
    }
  }

  // Match /api/v1/tourists/:id/location
  const locMatch = pathname && pathname.match(/^\/api\/v1\/tourists\/([^/]+)\/location$/);
  if (method === 'POST' && locMatch) {
    return sendJson(res, 200, { ok: true });
  }

  // Match /api/v1/tourists/:id/panic
  const panicMatch = pathname && pathname.match(/^\/api\/v1\/tourists\/([^/]+)\/panic$/);
  if (method === 'POST' && panicMatch) {
    return sendJson(res, 200, { ok: true });
  }

  return notFound(res);
});

server.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`[mock-server] Listening on http://localhost:${PORT}`);
});


