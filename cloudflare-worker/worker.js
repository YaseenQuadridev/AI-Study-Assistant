// Cloudflare Worker — Adaptive Study Planner API Gateway (Phase 4)
// Deploy with: wrangler deploy

const SUPABASE_URL = 'https://blowpaeftobvczysekrr.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_ZhJf8u6YjuDewlJp1tTfJw_p7eu8NpH';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, apikey, x-requested-with',
};

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders, status: 204 });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // Health check
    if (path === '/health') {
      return jsonResponse({ status: 'ok', version: '4.0.0', phase: '4' });
    }

    // Edge Function proxy: /edge/process-document
    if (path === '/edge/process-document') {
      return proxyToEdgeFunction(request, env);
    }

    // Supabase REST API proxy
    const supabasePath = path.replace('/api/v3', '/rest/v1');
    const supabaseUrl = SUPABASE_URL + supabasePath + url.search;

    const headers = new Headers(request.headers);
    headers.set('apikey', SUPABASE_ANON_KEY);

    const response = await fetch(supabaseUrl, {
      method: request.method,
      headers: headers,
      body: request.body,
    });

    const responseHeaders = new Headers(response.headers);
    Object.entries(corsHeaders).forEach(([k, v]) => responseHeaders.set(k, v));
    responseHeaders.set('Content-Type', 'application/json');

    return new Response(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  },
};

async function proxyToEdgeFunction(request, env) {
  const edgeUrl = `${SUPABASE_URL}/functions/v1/process-document`;
  const headers = new Headers(request.headers);
  headers.set('Authorization', `Bearer ${SUPABASE_ANON_KEY}`);
  headers.set('apikey', SUPABASE_ANON_KEY);

  const response = await fetch(edgeUrl, {
    method: request.method,
    headers: headers,
    body: request.body,
  });

  const responseHeaders = new Headers(response.headers);
  Object.entries(corsHeaders).forEach(([k, v]) => responseHeaders.set(k, v));

  return new Response(response.body, {
    status: response.status,
    headers: responseHeaders,
  });
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  });
}
