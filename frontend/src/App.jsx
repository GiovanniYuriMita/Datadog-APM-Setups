import { useEffect, useMemo, useState } from 'react'
import { datadogRum } from '@datadog/browser-rum'
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

const createSessionId = () =>
  `sess_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [profile, setProfile] = useState({ name: '', email: '' })
  const [sessionId, setSessionId] = useState('')
  const [apiBaseUrl, setApiBaseUrl] = useState(DEFAULT_BASE_URL)
  const normalizedBaseUrl = useMemo(() => normalizeBaseUrl(apiBaseUrl), [apiBaseUrl])
  const [requestId, setRequestId] = useState('demo-request-001')

  const [healthResult, setHealthResult] = useState(null)
  const [userResult, setUserResult] = useState(null)
  const [productsResult, setProductsResult] = useState(null)
  const [transactionResult, setTransactionResult] = useState(null)
  const [analyticsResult, setAnalyticsResult] = useState(null)
  const [errorResult, setErrorResult] = useState(null)
  const [computeErrorResult, setComputeErrorResult] = useState(null)
  const [dynamicBatchResult, setDynamicBatchResult] = useState(null)
  const [dynamicSlowResult, setDynamicSlowResult] = useState(null)
  const [dynamicHiddenErrorResult, setDynamicHiddenErrorResult] = useState(null)

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
  const [computeForm, setComputeForm] = useState({
    base_value: '10',
    multiplier: '2',
    operation: 'scale',
    force_error: true
  })
  const [dynamicBatchForm, setDynamicBatchForm] = useState({
    batch_id: 'batch-workshop-001',
    tax_rate: '0.12',
    discount_threshold: '1200'
  })
  const [dynamicSlowForm, setDynamicSlowForm] = useState({
    user_id: 'user_001',
    delay_seconds: '10'
  })
  const [dynamicHiddenForm, setDynamicHiddenForm] = useState({
    transaction_id: '',
    retries: '1',
    factor: '1.5',
    baseline: '120'
  })

  useEffect(() => {
    const stored = localStorage.getItem('dd-demo-user')
    if (!stored) {
      return
    }
    try {
      const parsed = JSON.parse(stored)
      if (parsed?.name && parsed?.email) {
        setProfile({ name: parsed.name, email: parsed.email })
        if (parsed.sessionId) {
          setSessionId(parsed.sessionId)
        }
        setIsAuthenticated(true)
        datadogRum.setUser({ id: parsed.email, name: parsed.name, email: parsed.email })
      }
    } catch {
      localStorage.removeItem('dd-demo-user')
    }
  }, [])

  const apiRequest = async ({ path, method = 'GET', body }) => {
    const url = buildUrl(apiBaseUrl, path)
    const headers = { 'Accept': 'application/json' }
    if (requestId.trim()) {
      headers['X-Request-Id'] = requestId.trim()
    }
    if (sessionId) {
      headers['X-Session-Id'] = sessionId
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

  const handleComputeError = async () => {
    const payload = {
      base_value: Number(computeForm.base_value),
      multiplier: Number(computeForm.multiplier),
      operation: computeForm.operation,
      force_error: computeForm.force_error
    }
    setComputeErrorResult(
      await apiRequest({ path: '/api/error/compute', method: 'POST', body: payload })
    )
  }

  const handleDynamicBatch = async () => {
    const payload = {
      batch_id: dynamicBatchForm.batch_id.trim() || 'batch-workshop-001',
      tax_rate: Number(dynamicBatchForm.tax_rate),
      discount_threshold: Number(dynamicBatchForm.discount_threshold),
      records: [
        { item_id: 'prod_001', unit_price: 999.99, quantity: 1 },
        { item_id: 'prod_002', unit_price: 29.99, quantity: 2 },
        { item_id: 'prod_003', unit_price: 79.99, quantity: 0 }
      ]
    }
    setDynamicBatchResult(
      await apiRequest({ path: '/api/dynamic/process-batch', method: 'POST', body: payload })
    )
  }

  const handleDynamicSlow = async () => {
    const payload = {
      user_id: dynamicSlowForm.user_id.trim() || 'user_001',
      delay_seconds: Number(dynamicSlowForm.delay_seconds),
      records: [
        { item_id: 'prod_001', unit_price: 999.99, quantity: 1 },
        { item_id: 'prod_002', unit_price: 29.99, quantity: 2 }
      ]
    }
    setDynamicSlowResult(
      await apiRequest({ path: '/api/dynamic/slow-checkout', method: 'POST', body: payload })
    )
  }

  const handleDynamicHiddenError = async () => {
    const payload = {
      transaction_id: dynamicHiddenForm.transaction_id.trim() || undefined,
      retries: Number(dynamicHiddenForm.retries),
      factor: Number(dynamicHiddenForm.factor),
      baseline: Number(dynamicHiddenForm.baseline)
    }
    setDynamicHiddenErrorResult(
      await apiRequest({ path: '/api/dynamic/hidden-error', method: 'POST', body: payload })
    )
  }

  const triggerFrontendError = () => {
    throw new Error('Simulated frontend exception for RUM Error Tracking')
  }

  const triggerFrontendRejection = () => {
    Promise.reject(new Error('Simulated frontend unhandled rejection'))
  }

  const handleLogin = (event) => {
    event.preventDefault()
    const name = profile.name.trim()
    const email = profile.email.trim()
    if (!name || !email) {
      return
    }
    const nextSessionId = sessionId || createSessionId()
    setSessionId(nextSessionId)
    localStorage.setItem('dd-demo-user', JSON.stringify({ name, email, sessionId: nextSessionId }))
    datadogRum.setUser({ id: email, name, email })
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    datadogRum.stopSession()
    datadogRum.setUser({})
    localStorage.removeItem('dd-demo-user')
    setIsAuthenticated(false)
    setSessionId('')
  }

  if (!isAuthenticated) {
    return (
      <div className="app auth">
        <header className="app-header">
          <div>
            <h1>Datadog APM Frontend Demo</h1>
            <p>Informe nome e email para iniciar uma sessão.</p>
          </div>
        </header>
        <section className="card">
          <h2>Login fake</h2>
          <form className="field-grid" onSubmit={handleLogin}>
            <label>
              Nome
              <input
                type="text"
                value={profile.name}
                onChange={(event) =>
                  setProfile((prev) => ({ ...prev, name: event.target.value }))
                }
                placeholder="Ex: Maria Silva"
              />
            </label>
            <label>
              Email
              <input
                type="email"
                value={profile.email}
                onChange={(event) =>
                  setProfile((prev) => ({ ...prev, email: event.target.value }))
                }
                placeholder="email@exemplo.com"
              />
            </label>
            <button type="submit">Entrar</button>
          </form>
        </section>
      </div>
    )
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
            Usuário logado
            <input
              type="text"
              value={`${profile.name} <${profile.email}>`}
              readOnly
            />
          </label>
          <button className="secondary" onClick={handleLogout}>
            Logout
          </button>
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

        <section className="card">
          <h2>Exception com inputs/outputs</h2>
          <p>POST que calcula valores e dispara exceção.</p>
          <div className="field-grid">
            <label>
              base_value
              <input
                type="number"
                value={computeForm.base_value}
                onChange={(event) =>
                  setComputeForm((prev) => ({ ...prev, base_value: event.target.value }))
                }
              />
            </label>
            <label>
              multiplier
              <input
                type="number"
                value={computeForm.multiplier}
                onChange={(event) =>
                  setComputeForm((prev) => ({ ...prev, multiplier: event.target.value }))
                }
              />
            </label>
            <label>
              operation
              <select
                value={computeForm.operation}
                onChange={(event) =>
                  setComputeForm((prev) => ({ ...prev, operation: event.target.value }))
                }
              >
                <option value="scale">scale</option>
                <option value="divide">divide</option>
              </select>
            </label>
            <label>
              force_error
              <select
                value={computeForm.force_error ? 'true' : 'false'}
                onChange={(event) =>
                  setComputeForm((prev) => ({ ...prev, force_error: event.target.value === 'true' }))
                }
              >
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
            </label>
          </div>
          <button onClick={handleComputeError}>Executar compute</button>
          <ResultPanel result={computeErrorResult} />
        </section>

        <section className="card dynamic-demo">
          <h2>Dynamic Instrumentation Demo</h2>
          <p>
            Cenários para instrumentar pela UI do Datadog: entrada/saída,
            lentidão e erro "escondido" com status incorreto.
          </p>

          <h3>1) process_batch (inputs/outputs)</h3>
          <div className="field-grid">
            <label>
              batch_id
              <input
                type="text"
                value={dynamicBatchForm.batch_id}
                onChange={(event) =>
                  setDynamicBatchForm((prev) => ({ ...prev, batch_id: event.target.value }))
                }
              />
            </label>
            <label>
              tax_rate
              <input
                type="number"
                step="0.01"
                value={dynamicBatchForm.tax_rate}
                onChange={(event) =>
                  setDynamicBatchForm((prev) => ({ ...prev, tax_rate: event.target.value }))
                }
              />
            </label>
            <label>
              discount_threshold
              <input
                type="number"
                value={dynamicBatchForm.discount_threshold}
                onChange={(event) =>
                  setDynamicBatchForm((prev) => ({ ...prev, discount_threshold: event.target.value }))
                }
              />
            </label>
          </div>
          <button onClick={handleDynamicBatch}>Executar process_batch</button>
          <ResultPanel result={dynamicBatchResult} />

          <h3>2) Slow checkout (~10s)</h3>
          <div className="field-grid">
            <label>
              user_id
              <input
                type="text"
                value={dynamicSlowForm.user_id}
                onChange={(event) =>
                  setDynamicSlowForm((prev) => ({ ...prev, user_id: event.target.value }))
                }
              />
            </label>
            <label>
              delay_seconds
              <input
                type="number"
                min="1"
                value={dynamicSlowForm.delay_seconds}
                onChange={(event) =>
                  setDynamicSlowForm((prev) => ({ ...prev, delay_seconds: event.target.value }))
                }
              />
            </label>
          </div>
          <button onClick={handleDynamicSlow}>Executar slow-checkout</button>
          <ResultPanel result={dynamicSlowResult} />

          <h3>3) Hidden error (retorna 200)</h3>
          <div className="field-grid">
            <label>
              transaction_id (vazio para falhar)
              <input
                type="text"
                value={dynamicHiddenForm.transaction_id}
                onChange={(event) =>
                  setDynamicHiddenForm((prev) => ({ ...prev, transaction_id: event.target.value }))
                }
              />
            </label>
            <label>
              retries
              <input
                type="number"
                value={dynamicHiddenForm.retries}
                onChange={(event) =>
                  setDynamicHiddenForm((prev) => ({ ...prev, retries: event.target.value }))
                }
              />
            </label>
            <label>
              factor
              <input
                type="number"
                step="0.1"
                value={dynamicHiddenForm.factor}
                onChange={(event) =>
                  setDynamicHiddenForm((prev) => ({ ...prev, factor: event.target.value }))
                }
              />
            </label>
            <label>
              baseline
              <input
                type="number"
                value={dynamicHiddenForm.baseline}
                onChange={(event) =>
                  setDynamicHiddenForm((prev) => ({ ...prev, baseline: event.target.value }))
                }
              />
            </label>
          </div>
          <button onClick={handleDynamicHiddenError}>Executar hidden-error</button>
          <ResultPanel result={dynamicHiddenErrorResult} />
        </section>

        <section className="card">
          <h2>Erro apenas no frontend</h2>
          <p>Dispara erro local para o RUM Error Tracking.</p>
          <div className="button-row">
            <button className="ghost" onClick={triggerFrontendError}>
              Lançar exception
            </button>
            <button className="ghost" onClick={triggerFrontendRejection}>
              Unhandled rejection
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
