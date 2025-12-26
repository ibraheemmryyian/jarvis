import { useState, useEffect, useRef } from 'react'

function App() {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [currentMode, setCurrentMode] = useState('chat') // 'chat' or 'autonomous'
    const [settings, setSettings] = useState({
        max_tokens: 16384,
        recycle_threshold: 0.75,
        model_name: 'nous-hermes-3-8b'
    })
    const [contextUsage, setContextUsage] = useState({ usage_percent: 0 })
    const [theme, setTheme] = useState('modern')
    const [logs, setLogs] = useState([])
    const [status, setStatus] = useState('online')
    const [checkpoints, setCheckpoints] = useState([])
    const [isResuming, setIsResuming] = useState(false)

    const chatRef = useRef(null)
    const wsRef = useRef(null)

    // Smart detection: Does this request need autonomous mode?
    const detectAutonomousMode = (message) => {
        const msg = message.toLowerCase()

        // Keywords that indicate complex, multi-step tasks
        const autonomousKeywords = [
            // Building/Creating
            'build me', 'build a', 'create a full', 'create an app', 'create a website',
            'make me a', 'make a full', 'develop a', 'develop an',
            'scaffold', 'generate a project', 'set up a', 'setup a',

            // Full scope work
            'full stack', 'fullstack', 'entire', 'complete', 'from scratch',
            'end to end', 'end-to-end', 'production ready', 'production-ready',

            // Multi-step processes
            'deploy', 'launch', 'ship this', 'go live',
            'refactor the entire', 'rewrite', 'rebuild',
            'implement', 'integrate',

            // Business/Research tasks
            'write a business plan', 'create a pitch', 'full analysis',
            'research and', 'analyze and create', 'deep dive',
            'strategy for', 'marketing campaign',

            // Specific projects
            'landing page', 'dashboard', 'admin panel', 'api backend',
            'mobile app', 'web app', 'saas', 'marketplace', 'ecommerce',

            // Autonomous triggers
            'work on this', 'handle this', 'take care of', 'figure out',
            'do everything', 'autonomous', 'auto mode',
        ]

        // Check for autonomous keywords
        for (const keyword of autonomousKeywords) {
            if (msg.includes(keyword)) {
                return true
            }
        }

        // Check for multi-part requests (commas, "and then", numbered lists)
        if ((msg.match(/,/g) || []).length >= 2 && msg.length > 100) {
            return true
        }
        if (msg.includes(' and then ') || msg.includes(' after that ')) {
            return true
        }
        if (/\d\.\s/.test(msg)) { // Numbered list
            return true
        }

        // Long messages often indicate complex tasks
        if (msg.length > 300) {
            return true
        }

        return false
    }

    // WebSocket connection
    useEffect(() => {
        const connect = () => {
            const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`)

            ws.onopen = () => {
                setStatus('online')
                addLog('Connected to Jarvis', 'success')
            }

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data)

                if (data.type === 'response') {
                    setMessages(prev => [...prev, { role: 'assistant', content: data.content }])
                    setIsLoading(false)
                    setCurrentMode('chat')
                    setStatus('online')
                } else if (data.type === 'log') {
                    addLog(data.content, 'info')
                } else if (data.type === 'status') {
                    setSettings(data.settings)
                    setContextUsage(data.context_usage)
                } else if (data.type === 'error') {
                    addLog(data.content, 'error')
                    setIsLoading(false)
                    setCurrentMode('chat')
                    setStatus('online')
                } else if (data.type === 'progress') {
                    addLog(data.content, 'info')
                }
            }

            ws.onclose = () => {
                setStatus('error')
                addLog('Disconnected. Reconnecting...', 'warning')
                setTimeout(connect, 3000)
            }

            ws.onerror = () => {
                setStatus('error')
            }

            wsRef.current = ws
        }

        connect()
        fetchSettings()
        fetchCheckpoints()

        return () => {
            if (wsRef.current) wsRef.current.close()
        }
    }, [])

    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight
        }
    }, [messages])

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme)
    }, [theme])

    const addLog = (message, type = 'info') => {
        const timestamp = new Date().toLocaleTimeString()
        setLogs(prev => [...prev.slice(-50), { message, type, timestamp }])
    }

    const fetchSettings = async () => {
        try {
            const res = await fetch('/api/settings')
            const data = await res.json()
            setSettings(data)
            setContextUsage(data.context_usage || { usage_percent: 0 })
        } catch (e) {
            console.error('Failed to fetch settings:', e)
        }
    }

    const fetchCheckpoints = async () => {
        try {
            const res = await fetch('/api/checkpoints')
            const data = await res.json()
            setCheckpoints(data.checkpoints || [])
        } catch (e) {
            console.error('Failed to fetch checkpoints:', e)
        }
    }

    const resumeFromCheckpoint = async (checkpointId) => {
        if (isResuming) return
        setIsResuming(true)
        setCurrentMode('autonomous')
        setStatus('busy')
        addLog(`🔄 Resuming from checkpoint ${checkpointId}...`, 'success')

        try {
            // Use WebSocket for real-time updates
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({
                    type: 'chat',
                    message: '',
                    autonomous: true,
                    resume_checkpoint: checkpointId
                }))
            } else {
                const res = await fetch(`/api/autonomous/resume/${checkpointId}`, {
                    method: 'POST'
                })
                const data = await res.json()
                addLog('Checkpoint resume complete', 'success')
                setMessages(prev => [...prev, { role: 'assistant', content: data.result?.summary || 'Resumed successfully' }])
            }
        } catch (e) {
            addLog('Failed to resume from checkpoint', 'error')
        }
        setIsResuming(false)
        setCurrentMode('chat')
        setStatus('online')
        fetchCheckpoints() // Refresh list
    }

    const deleteCheckpoint = async (checkpointId) => {
        try {
            await fetch(`/api/checkpoints/${checkpointId}`, { method: 'DELETE' })
            addLog(`Deleted checkpoint ${checkpointId}`, 'info')
            fetchCheckpoints()
        } catch (e) {
            addLog('Failed to delete checkpoint', 'error')
        }
    }

    const updateSettings = async (newSettings) => {
        try {
            const res = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newSettings)
            })
            const data = await res.json()
            setSettings(data.settings)
            addLog('Settings updated', 'success')
        } catch (e) {
            addLog('Failed to update settings', 'error')
        }
    }

    const sendMessage = async (e) => {
        e?.preventDefault()
        if (!input.trim() || isLoading) return

        const userMessage = input.trim()
        setInput('')

        // AUTO-DETECT: Should this be autonomous?
        const shouldBeAutonomous = detectAutonomousMode(userMessage)

        if (shouldBeAutonomous) {
            setCurrentMode('autonomous')
            addLog('🚀 Complex task detected - Autonomous Mode', 'success')
        }

        setMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setIsLoading(true)
        setStatus('busy')

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'chat',
                message: userMessage,
                autonomous: shouldBeAutonomous
            }))
        } else {
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: userMessage,
                        autonomous: shouldBeAutonomous
                    })
                })
                const data = await res.json()
                setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
            } catch (e) {
                addLog('Failed to send message', 'error')
            }
            setIsLoading(false)
            setCurrentMode('chat')
            setStatus('online')
        }
    }

    return (
        <div className="app">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="logo">J</div>
                    <span className="sidebar-title">JARVIS</span>
                </div>

                <div className="sidebar-section">
                    <div className="section-title">Status</div>
                    <div className="status-indicator">
                        <div className={`status-dot ${status}`}></div>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                            {status === 'online' ? 'Ready' : status === 'busy' ? (currentMode === 'autonomous' ? '🚀 Working...' : 'Thinking...') : 'Disconnected'}
                        </span>
                    </div>

                    {currentMode === 'autonomous' && isLoading && (
                        <div style={{
                            marginTop: '12px',
                            padding: '10px 12px',
                            background: 'linear-gradient(135deg, rgba(255,107,53,0.15) 0%, rgba(247,147,30,0.15) 100%)',
                            borderRadius: '8px',
                            border: '1px solid rgba(255,107,53,0.3)'
                        }}>
                            <div style={{ fontSize: '12px', fontWeight: 600, color: '#ff6b35' }}>
                                🚀 AUTONOMOUS MODE
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                                Jarvis is working on your task...
                            </div>
                        </div>
                    )}
                </div>

                <div className="sidebar-section">
                    <div className="section-title">Theme</div>
                    <div className="toggle-container">
                        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Modern</span>
                        <div
                            className={`toggle ${theme === 'legacy' ? 'active' : ''}`}
                            onClick={() => setTheme(theme === 'modern' ? 'legacy' : 'modern')}
                        />
                        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Legacy</span>
                    </div>
                </div>

                <div className="sidebar-section" style={{ flex: 1 }}>
                    <div className="section-title">Activity Log</div>
                    <div className="log-panel">
                        {logs.slice(-15).map((log, i) => (
                            <div key={i} className={`log-entry ${log.type}`}>
                                <span style={{ opacity: 0.5 }}>{log.timestamp}</span> {log.message}
                            </div>
                        ))}
                    </div>
                </div>

                <div style={{
                    padding: '12px',
                    background: 'var(--surface)',
                    borderRadius: '8px',
                    fontSize: '11px',
                    color: 'var(--text-muted)',
                    lineHeight: 1.5
                }}>
                    <strong>💡 Tip:</strong> Just ask naturally. Jarvis auto-detects when to use Autonomous Mode for complex tasks.
                </div>
            </aside>

            {/* Main Chat Area */}
            <main className="main-area">
                <div className="chat-container" ref={chatRef}>
                    {messages.length === 0 && (
                        <div className="message system">
                            <div style={{ fontSize: '18px', marginBottom: '12px' }}>👋 Hey, I'm Jarvis.</div>
                            <div style={{ opacity: 0.8 }}>
                                Just tell me what you need. I'll automatically figure out if it's a quick task or something that needs deeper work.
                            </div>
                            <div style={{ marginTop: '16px', fontSize: '13px', opacity: 0.6 }}>
                                <strong>Examples:</strong><br />
                                • "What's React?" → Quick answer<br />
                                • "Build me a todo app with React and FastAPI" → Full autonomous build
                            </div>
                        </div>
                    )}
                    {messages.map((msg, i) => (
                        <div key={i} className={`message ${msg.role}`}>
                            {msg.content}
                        </div>
                    ))}
                    {isLoading && (
                        <div className="message system">
                            {currentMode === 'autonomous'
                                ? '🚀 Autonomous execution in progress... Check the Activity Log for updates.'
                                : '⏳ Thinking...'}
                        </div>
                    )}
                </div>

                <div className="input-container">
                    <form onSubmit={sendMessage} className="input-wrapper">
                        <input
                            type="text"
                            className="chat-input"
                            placeholder="Tell Jarvis what you need..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            disabled={isLoading}
                        />
                        <button type="submit" className="btn btn-primary" disabled={isLoading}>
                            {isLoading ? '...' : 'Send'}
                        </button>
                    </form>
                </div>
            </main>

            {/* Settings Panel */}
            <aside className="settings-panel">
                <div className="settings-card">
                    <h3>⚙️ Context Settings</h3>

                    <div className="setting-row">
                        <span className="setting-label">Max Tokens</span>
                        <span className="setting-value">{settings.max_tokens?.toLocaleString()}</span>
                    </div>
                    <input
                        type="range"
                        className="slider"
                        min="4096"
                        max="65536"
                        step="4096"
                        value={settings.max_tokens || 16384}
                        onChange={(e) => {
                            const value = parseInt(e.target.value)
                            setSettings(prev => ({ ...prev, max_tokens: value }))
                        }}
                        onMouseUp={(e) => updateSettings({ max_tokens: parseInt(e.target.value) })}
                    />

                    <div className="setting-row" style={{ marginTop: '16px' }}>
                        <span className="setting-label">Recycle Threshold</span>
                        <span className="setting-value">{Math.round((settings.recycle_threshold || 0.75) * 100)}%</span>
                    </div>
                    <input
                        type="range"
                        className="slider"
                        min="50"
                        max="95"
                        step="5"
                        value={(settings.recycle_threshold || 0.75) * 100}
                        onChange={(e) => {
                            const value = parseInt(e.target.value) / 100
                            setSettings(prev => ({ ...prev, recycle_threshold: value }))
                        }}
                        onMouseUp={(e) => updateSettings({ recycle_threshold: parseInt(e.target.value) / 100 })}
                    />
                </div>

                <div className="settings-card">
                    <h3>📊 Context Usage</h3>
                    <div className="setting-row">
                        <span className="setting-label">Current</span>
                        <span className="setting-value">{contextUsage.usage_percent || 0}%</span>
                    </div>
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{
                                width: `${contextUsage.usage_percent || 0}%`,
                                background: (contextUsage.usage_percent || 0) > 75
                                    ? 'var(--warning)'
                                    : 'var(--accent-gradient)'
                            }}
                        />
                    </div>
                </div>

                <div className="settings-card">
                    <h3>🤖 Model</h3>
                    <div className="setting-row">
                        <span className="setting-label">Active</span>
                        <span className="setting-value" style={{ fontSize: '12px' }}>
                            {settings.model_name || 'nous-hermes-3-8b'}
                        </span>
                    </div>
                </div>

                <div className="settings-card">
                    <h3>💾 Checkpoints</h3>
                    {checkpoints.length === 0 ? (
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                            No checkpoints saved yet. Jarvis auto-saves every 5 steps during autonomous mode.
                        </div>
                    ) : (
                        <div style={{ maxHeight: '150px', overflowY: 'auto' }}>
                            {checkpoints.slice(0, 5).map(cp => (
                                <div key={cp.id} style={{
                                    padding: '8px',
                                    marginBottom: '6px',
                                    background: 'rgba(255,255,255,0.03)',
                                    borderRadius: '6px',
                                    border: '1px solid var(--glass-border)'
                                }}>
                                    <div style={{ fontSize: '11px', fontWeight: 600, marginBottom: '4px' }}>
                                        Step {cp.iteration} • {cp.completed}/{cp.completed + cp.pending} done
                                    </div>
                                    <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '6px' }}>
                                        {cp.objective}
                                    </div>
                                    <div style={{ display: 'flex', gap: '6px' }}>
                                        <button
                                            onClick={() => resumeFromCheckpoint(cp.id)}
                                            disabled={isResuming}
                                            style={{
                                                padding: '4px 8px',
                                                fontSize: '10px',
                                                background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-cyan))',
                                                border: 'none',
                                                borderRadius: '4px',
                                                color: 'white',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            ▶ Resume
                                        </button>
                                        <button
                                            onClick={() => deleteCheckpoint(cp.id)}
                                            style={{
                                                padding: '4px 8px',
                                                fontSize: '10px',
                                                background: 'rgba(255,0,0,0.2)',
                                                border: '1px solid rgba(255,0,0,0.3)',
                                                borderRadius: '4px',
                                                color: '#ff6b6b',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            🗑
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="settings-card">
                    <h3>🧠 Capabilities</h3>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                        <div>✓ Full-stack development</div>
                        <div>✓ Research & analysis</div>
                        <div>✓ Git & deployment</div>
                        <div>✓ Docker & CI/CD</div>
                        <div>✓ Code review & testing</div>
                        <div>✓ Documentation</div>
                    </div>
                </div>
            </aside>
        </div>
    )
}

export default App
