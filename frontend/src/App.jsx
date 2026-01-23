import { useMemo, useState } from 'react'
import './App.css'

const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const normalizeBaseUrl = (value) => value.trim().replace(/\/$/, '')

const buildUrl = (baseUrl, path) => {
  const normalized = normalizeBaseUrl(baseUrl)
  return normalized ? `${normalized}${path}` : path
}

const formatResultPayload = (payload) => {
  if (payload === null || payload === undefined) {
    return 'Sem resposta'
  }
  if (typeof payload === 'string') {
    return payload.length ? payload : 'Sem resposta'
  }
  return JSON.stringify(payload, null, 2)
}

const ResultPanel = ({ result }) => {
  if (!result) {
    return <p className="muted">Execute a chamada para ver o retorno.</p>
  }

  if (result.error) {
    return (
      <div className="result error">
        <div className="result-meta">
          <span>Erro</span>
          <span>{result.durationMs}ms</span>
        </div>
        <pre>{result.error}</pre>
      </div>
    )
  }

  return (
    <div className={`result ${result.ok ? 'success' : 'error'}`}>
      <div className="result-meta">
        <span>{result.ok ? 'OK' : 'Erro'} {result.status}</span>
        <span>{result.durationMs}ms</span>
      </div>
      <div className="result-url">{result.url}</div>
      <pre>{formatResultPayload(result.data)}</pre>
    </div>
  )
}

function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState(DEFAULT_BASE_URL)
  const normalizedBaseUrl = useMemo(() => normalizeBaseUrl(apiBaseUrl), [apiBaseUrl])
  const [requestId, setRequestId] = useState('demo-request-001')

  const [healthResult, setHealthResult] = useState(null)
  const [userResult, setUserResult] = useState(null)
  const [productsResult, setProductsResult] = useState(null)
  const [transactionResult, setTransactionResult] = useState(null)
  const [analyticsResult, setAnalyticsResult] = useState(null)
  const [errorResult, setErrorResult] = useState(null)

  const [userId, setUserId] = useState('user_001')
  const [transactionForm, setTransactionForm] = useState({
    user_id: 'user_001',
    product_id: 'prod_002',
    quantity: '1'
  })
  const [errorForm, setErrorForm] = useState({
    type: 'validation',
    user_id: 'demo-user',
    amount: '-10',
    currency: 'BRL',
    divisor: '0',
    dividend: '1',
    timeout: '3'
  })

  const apiRequest = async ({ path, method = 'GET', body }) => {
    const url = buildUrl(apiBaseUrl, path)
    const headers = { 'Accept': 'application/json' }
    if (requestId.trim()) {
      headers['X-Request-Id'] = requestId.trim()
    }
    if (body) {
      headers['Content-Type'] = 'application/json'
    }

    const start = performance.now()
    try {
      const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined
      })
      const rawText = await response.text()
      let parsed = null
      if (rawText) {
        try {
          parsed = JSON.parse(rawText)
        } catch {
          parsed = rawText
        }
      }
      return {
        ok: response.ok,
        status: response.status,
        url: response.url || url,
        durationMs: Math.round(performance.now() - start),
        data: parsed
      }
    } catch (error) {
      return {
        ok: false,
        error: error instanceof Error ? error.message : 'Erro de rede',
        durationMs: Math.round(performance.now() - start)
      }
    }
  }

  const handleHealth = async () => {
    setHealthResult(await apiRequest({ path: '/health' }))
  }

  const handleUserLookup = async (targetUserId = userId) => {
    if (!targetUserId.trim()) {
      setUserResult({ ok: false, error: 'Informe um user_id válido', durationMs: 0 })
      return
    }
    setUserResult(await apiRequest({ path: `/api/user/${targetUserId.trim()}` }))
  }

  const handleProducts = async () => {
    setProductsResult(await apiRequest({ path: '/api/products' }))
  }

  const handleAnalytics = async () => {
    setAnalyticsResult(await apiRequest({ path: '/api/analytics/transactions' }))
  }

  const submitTransaction = async (payloadOverride) => {
    const payload = payloadOverride ?? {
      user_id: transactionForm.user_id.trim(),
      product_id: transactionForm.product_id.trim(),
      quantity: Number(transactionForm.quantity)
    }
    setTransactionResult(
      await apiRequest({ path: '/api/transaction', method: 'POST', body: payload })
    )
  }

  const handleErrorSimulation = async () => {
    const params = new URLSearchParams({
      type: errorForm.type,
      user_id: errorForm.user_id,
      amount: errorForm.amount,
      currency: errorForm.currency
    })
    if (errorForm.type === 'division') {
      params.set('divisor', errorForm.divisor)
      params.set('dividend', errorForm.dividend)
    }
    if (errorForm.type === 'timeout') {
      params.set('timeout', errorForm.timeout)
    }
    setErrorResult(await apiRequest({ path: `/api/error/simulate?${params.toString()}` }))
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Datadog APM Frontend Demo</h1>
          <p>UI rápida para simular interações e erros da API Python.</p>
        </div>
        <div className="base-url">
          <label>
            API Base URL
            <input
              type="text"
              value={apiBaseUrl}
              onChange={(event) => setApiBaseUrl(event.target.value)}
              placeholder="Use vazio para proxy do Vite"
            />
          </label>
          <small>Atual: {normalizedBaseUrl || 'proxy / localhost'}</small>
        </div>
        <div className="base-url">
          <label>
            X-Request-Id
            <input
              type="text"
              value={requestId}
              onChange={(event) => setRequestId(event.target.value)}
              placeholder="demo-request-001"
            />
          </label>
        </div>
      </header>

      <main className="grid">
        <section className="card">
          <h2>Health Check</h2>
          <p>Usa o endpoint de health com logging debug.</p>
          <button onClick={handleHealth}>Testar /health</button>
          <ResultPanel result={healthResult} />
        </section>

        <section className="card">
          <h2>Buscar Usuário</h2>
          <div className="field-row">
            <label>
              user_id
              <input
                type="text"
                value={userId}
                onChange={(event) => setUserId(event.target.value)}
              />
            </label>
          </div>
          <div className="button-row">
            <button onClick={() => handleUserLookup()}>Buscar</button>
            <button
              className="secondary"
              onClick={() => handleUserLookup('user_999')}
            >
              Simular não encontrado
            </button>
          </div>
          <ResultPanel result={userResult} />
        </section>

        <section className="card">
          <h2>Produtos</h2>
          <p>Lista produtos para validar estoque.</p>
          <button onClick={handleProducts}>Listar produtos</button>
          <ResultPanel result={productsResult} />
        </section>

        <section className="card">
          <h2>Transação</h2>
          <div className="field-grid">
            <label>
              user_id
              <input
                type="text"
                value={transactionForm.user_id}
                onChange={(event) =>
                  setTransactionForm((prev) => ({ ...prev, user_id: event.target.value }))
                }
              />
            </label>
            <label>
              product_id
              <input
                type="text"
                value={transactionForm.product_id}
                onChange={(event) =>
                  setTransactionForm((prev) => ({ ...prev, product_id: event.target.value }))
                }
              />
            </label>
            <label>
              quantity
              <input
                type="number"
                min="1"
                value={transactionForm.quantity}
                onChange={(event) =>
                  setTransactionForm((prev) => ({ ...prev, quantity: event.target.value }))
                }
              />
            </label>
          </div>
          <div className="button-row">
            <button onClick={() => submitTransaction()}>Criar transação</button>
            <button
              className="secondary"
              onClick={() =>
                submitTransaction({ user_id: transactionForm.user_id.trim() })
              }
            >
              Campos faltando
            </button>
          </div>
          <div className="button-row">
            <button
              className="ghost"
              onClick={() =>
                submitTransaction({
                  user_id: 'user_999',
                  product_id: 'prod_001',
                  quantity: 1
                })
              }
            >
              Usuário inválido
            </button>
            <button
              className="ghost"
              onClick={() =>
                submitTransaction({
                  user_id: 'user_001',
                  product_id: 'prod_999',
                  quantity: 1
                })
              }
            >
              Produto inválido
            </button>
            <button
              className="ghost"
              onClick={() =>
                submitTransaction({
                  user_id: 'user_001',
                  product_id: 'prod_001',
                  quantity: 100
                })
              }
            >
              Estoque insuficiente
            </button>
            <button
              className="ghost"
              onClick={() =>
                submitTransaction({
                  user_id: 'user_003',
                  product_id: 'prod_001',
                  quantity: 1
                })
              }
            >
              Saldo insuficiente
            </button>
          </div>
          <ResultPanel result={transactionResult} />
        </section>

        <section className="card">
          <h2>Analytics</h2>
          <p>Consulta métricas de transações (últimas 10).</p>
          <button onClick={handleAnalytics}>Ver analytics</button>
          <ResultPanel result={analyticsResult} />
        </section>

        <section className="card">
          <h2>Simular Erros</h2>
          <div className="field-grid">
            <label>
              Tipo
              <select
                value={errorForm.type}
                onChange={(event) =>
                  setErrorForm((prev) => ({ ...prev, type: event.target.value }))
                }
              >
                <option value="validation">validation (ValueError)</option>
                <option value="division">division (ZeroDivisionError)</option>
                <option value="timeout">timeout</option>
                <option value="generic">generic</option>
              </select>
            </label>
            <label>
              user_id
              <input
                type="text"
                value={errorForm.user_id}
                onChange={(event) =>
                  setErrorForm((prev) => ({ ...prev, user_id: event.target.value }))
                }
              />
            </label>
            <label>
              amount
              <input
                type="text"
                value={errorForm.amount}
                onChange={(event) =>
                  setErrorForm((prev) => ({ ...prev, amount: event.target.value }))
                }
              />
            </label>
            <label>
              currency
              <input
                type="text"
                value={errorForm.currency}
                onChange={(event) =>
                  setErrorForm((prev) => ({ ...prev, currency: event.target.value }))
                }
              />
            </label>
            <label>
              dividend
              <input
                type="text"
                value={errorForm.dividend}
                onChange={(event) =>
                  setErrorForm((prev) => ({ ...prev, dividend: event.target.value }))
                }
                disabled={errorForm.type !== 'division'}
              />
            </label>
            <label>
              divisor
              <input
                type="text"
                value={errorForm.divisor}
                onChange={(event) =>
                  setErrorForm((prev) => ({ ...prev, divisor: event.target.value }))
                }
                disabled={errorForm.type !== 'division'}
              />
            </label>
            <label>
              timeout (s)
              <input
                type="text"
                value={errorForm.timeout}
                onChange={(event) =>
                  setErrorForm((prev) => ({ ...prev, timeout: event.target.value }))
                }
                disabled={errorForm.type !== 'timeout'}
              />
            </label>
          </div>
          <button onClick={handleErrorSimulation}>Simular erro</button>
          <ResultPanel result={errorResult} />
        </section>
      </main>
    </div>
  )
}

export default App
