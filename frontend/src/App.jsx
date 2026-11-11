import { useEffect, useState } from 'react'
import {
  Search, Plus, Building2, FileText, MapPin, Clock3, Save,
  ArrowUpRight, Trash2, RefreshCw, Sparkles, Copy, Check,
  ExternalLink, HelpCircle, Menu, X, ShieldCheck, Globe, ChevronRight
} from 'lucide-react'

const API = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

const EMPTY_FORM = {
  company_name: '',
  industry: 'Paint / Construction',
  location: '',
  company_overview: '',
  potential_paint_requirements: '',
  project_signals: '',
  meeting_questions: '',
  next_steps: '',
  source_urls: ''
}

export default function App() {
  const [briefs, setBriefs] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [notice, setNotice] = useState('')
  const [error, setError] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [showMcpModal, setShowMcpModal] = useState(false)
  const [copiedPrompt, setCopiedPrompt] = useState(null)
  const [copiedConfig, setCopiedConfig] = useState(false)
  const [copiedBrief, setCopiedBrief] = useState(false)
  const [apiOnline, setApiOnline] = useState(true)

  const selectedBrief = briefs.find(b => b.id === selectedId)

  async function api(path, options = {}) {
    const res = await fetch(`${API}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      },
      ...options
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || `Request failed with status ${res.status}`)
    }
    return res.status === 204 ? null : res.json()
  }

  async function loadBriefs() {
    try {
      setLoading(true)
      setError('')
      const q = search.trim() ? `?q=${encodeURIComponent(search.trim())}` : ''
      const data = await api(`/briefs${q}`)
      setBriefs(data)
      setApiOnline(true)

      // If a selected item was deleted or missing, reset
      if (selectedId && !data.some(b => b.id === selectedId)) {
        if (!isCreating) {
          setSelectedId(null)
          setForm(EMPTY_FORM)
        }
      }
    } catch (err) {
      setError(err.message || 'Unable to connect to MASCoT backend.')
      setApiOnline(false)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadBriefs()
  }, [search])

  useEffect(() => {
    if (selectedBrief && !isCreating) {
      setForm({ ...selectedBrief })
    }
  }, [selectedBrief?.id])

  function handleStartNew() {
    setIsCreating(true)
    setSelectedId(null)
    setForm(EMPTY_FORM)
    setNotice('Create a new company brief. Fill in the fields below and click Save.')
    setError('')
    setMobileMenuOpen(false)
  }

  function handleSelect(brief) {
    setIsCreating(false)
    setSelectedId(brief.id)
    setForm({ ...brief })
    setNotice('')
    setError('')
    setMobileMenuOpen(false)
  }

  const updateField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  async function handleSave(e) {
    e?.preventDefault()
    if (!form.company_name.trim()) {
      setError('Company name is required.')
      return
    }

    setSaving(true)
    setError('')
    try {
      if (isCreating) {
        const created = await api('/briefs', {
          method: 'POST',
          body: JSON.stringify(form)
        })
        setIsCreating(false)
        setSelectedId(created.id)
        setForm({ ...created })
        setNotice(`Company brief for "${created.company_name}" created successfully.`)
      } else {
        const updated = await api(`/briefs/${selectedId}`, {
          method: 'PATCH',
          body: JSON.stringify(form)
        })
        setSelectedId(updated.id)
        setForm({ ...updated })
        setNotice(`Changes to "${updated.company_name}" saved successfully.`)
      }
      await loadBriefs()
    } catch (err) {
      setError(err.message || 'Failed to save changes.')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete() {
    if (!selectedId) return
    const name = selectedBrief?.company_name || 'this company'
    if (!window.confirm(`Are you sure you want to delete the brief for "${name}"? This cannot be undone.`)) {
      return
    }

    setSaving(true)
    try {
      await api(`/briefs/${selectedId}`, { method: 'DELETE' })
      setSelectedId(null)
      setIsCreating(false)
      setForm(EMPTY_FORM)
      setNotice(`Brief for "${name}" was deleted.`)
      await loadBriefs()
    } catch (err) {
      setError(err.message || 'Failed to delete brief.')
    } finally {
      setSaving(false)
    }
  }

  function copyMarkdownBrief() {
    if (!form.company_name) return
    const md = `# Company Brief: ${form.company_name}
**Industry:** ${form.industry || 'N/A'}
**Location:** ${form.location || 'N/A'}

## Overview
${form.company_overview || 'No overview provided.'}

## Potential Paint Requirements
${form.potential_paint_requirements || 'No paint requirements identified.'}

## Project Signals
${form.project_signals || 'No signals recorded.'}

## Meeting Preparation Questions
${form.meeting_questions || 'No meeting questions prepared.'}

## Next Steps
${form.next_steps || 'No next steps assigned.'}

## Sources & Citations
${form.source_urls || 'N/A'}

---
*Retrieved from MASCoT Company Intelligence Workspace*`

    navigator.clipboard.writeText(md)
    setCopiedBrief(true)
    setTimeout(() => setCopiedBrief(false), 2500)
  }

  const samplePrompts = [
    {
      title: '1. Research & Create Brief',
      text: 'Research ABC Infrastructure, a construction company based in Hyderabad. Prepare a company intelligence brief covering its business overview, potential paint requirements, relevant project signals, meeting preparation questions, and next steps. Include source URLs where available. Save the brief in MASCoT.'
    },
    {
      title: '2. Retrieve Saved Brief',
      text: 'Find the company intelligence brief for ABC Infrastructure in MASCoT and show me the information currently saved.'
    },
    {
      title: '3. Update Existing Brief',
      text: 'Update the ABC Infrastructure brief with these additional meeting notes: Validated demand for 45,000L epoxy protective coatings for Hyderabad Metro expansion. Set next step to submit primer batch for laboratory corrosion testing by Friday. Save the changes in MASCoT.'
    },
    {
      title: '4. Verify Synchronisation',
      text: 'Retrieve the latest ABC Infrastructure brief from MASCoT and show me its current next steps.'
    }
  ]

  const [mcpTab, setMcpTab] = useState('cloud')

  const mcpCloudConfig = JSON.stringify({
    mcpServers: {
      "mascot-intelligence": {
        url: (import.meta.env.VITE_MCP_URL || "https://mascot-mcp-fins.onrender.com/mcp"),
        transport: "streamable-http"
      }
    }
  }, null, 2)

  const mcpLocalConfig = JSON.stringify({
    mcpServers: {
      "mascot-intelligence": {
        url: "http://localhost:8001/mcp",
        transport: "streamable-http"
      }
    }
  }, null, 2)

  const activeMcpConfig = mcpTab === 'cloud' ? mcpCloudConfig : mcpLocalConfig

  return (
    <div className="shell">
      {/* SIDEBAR NAVIGATION */}
      <aside className={`sidebar ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        <div className="brand">
          <div className="brandmark">
            <Building2 size={22} />
          </div>
          <div className="brand-text">
            <b>MASCoT</b>
            <small>Company Intelligence</small>
          </div>
          {mobileMenuOpen && (
            <button className="icon-btn close-sidebar" onClick={() => setMobileMenuOpen(false)}>
              <X size={18} />
            </button>
          )}
        </div>

        <div className="section-label">WORKSPACE</div>
        <nav className="nav active">
          <FileText size={17} />
          <span>Company Briefs</span>
          <span className="badge">{briefs.length}</span>
        </nav>

        <div className="sidebottom">
          <div className="mcp-card">
            <div className="mcp-card-header">
              <Sparkles size={16} />
              <b>Bring Your Own Claude</b>
            </div>
            <p>
              Claude researches, qualifies, and writes. MASCoT stores, edits, and keeps your records in sync.
            </p>
            <button className="btn-secondary-sm" onClick={() => setShowMcpModal(true)}>
              <HelpCircle size={14} /> Connect Claude via MCP
            </button>
          </div>

          <div className="system-pill">
            <ShieldCheck size={13} />
            <span>Zero In-App AI · 100% Persistent</span>
          </div>
          <small className="version-tag">MASCoT v1.0 · Volopay Assignment</small>
        </div>
      </aside>

      {/* MAIN VIEWPORT */}
      <main>
        {/* TOP STATUS BAR */}
        <header className="topbar">
          <div className="breadcrumbs">
            <button className="mobile-toggle" onClick={() => setMobileMenuOpen(true)}>
              <Menu size={18} />
            </button>
            <span>Workspace</span>
            <ChevronRight size={14} />
            <b>Company Briefs</b>
          </div>

          <div className="topbar-actions">
            <div className={`status-pill ${apiOnline ? 'online' : 'offline'}`}>
              <span className="status-dot"></span>
              <span>{apiOnline ? 'API Connected' : 'API Disconnected'}</span>
            </div>

            <button className="icon-btn" onClick={loadBriefs} title="Refresh records from database">
              <RefreshCw size={15} className={loading ? 'spinning' : ''} />
            </button>

            <button className="btn-mcp-top" onClick={() => setShowMcpModal(true)}>
              <Sparkles size={14} />
              <span>Connect Claude</span>
            </button>
          </div>
        </header>

        {/* WORKSPACE CONTENT AREA */}
        <div className="content">
          {/* HEADING & STATS */}
          <div className="heading-row">
            <div>
              <span className="eyebrow">MARKET & ACCOUNT STRATEGY</span>
              <h1>Company Intelligence Workspace</h1>
              <p>Curate, maintain, and synchronise strategic sales briefs for paint and coatings customer meetings.</p>
            </div>
            <button className="primary-btn" onClick={handleStartNew}>
              <Plus size={17} /> New Brief
            </button>
          </div>

          {/* METRIC CARDS */}
          <div className="stats-grid">
            <div className="stat-card">
              <small>SAVED INTELLIGENCE BRIEFS</small>
              <b>{briefs.length}</b>
              <label>Company records in database</label>
            </div>
            <div className="stat-card">
              <small>ACTIVE LOCATIONS</small>
              <b>{new Set(briefs.map(b => b.location).filter(Boolean)).size}</b>
              <label>Distinct project regions tracked</label>
            </div>
            <div className="stat-card architecture-card">
              <small>OPERATIONAL MODEL</small>
              <b className="accent-text">Claude + MCP + MASCoT</b>
              <label>External Claude reasoning · MASCoT permanent storage</label>
            </div>
          </div>

          {/* ERROR ALERT */}
          {error && (
            <div className="alert alert-error">
              <div>
                <strong>Error:</strong> {error}
              </div>
              <button onClick={() => setError('')} className="alert-close"><X size={14} /></button>
            </div>
          )}

          {/* TWO-COLUMN WORKSPACE: LIST & EDITOR */}
          <div className="workspace-grid">
            {/* LEFT: BRIEFS DIRECTORY */}
            <section className="directory-panel">
              <div className="directory-header">
                <div>
                  <h3>Saved Companies</h3>
                  <small>{briefs.length} {briefs.length === 1 ? 'record' : 'records'}</small>
                </div>
                <button className="icon-btn-sm" onClick={loadBriefs} title="Refresh directory">
                  <RefreshCw size={13} className={loading ? 'spinning' : ''} />
                </button>
              </div>

              <div className="search-box">
                <Search size={15} />
                <input
                  type="text"
                  placeholder="Search by company, industry, or location..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
                {search && (
                  <button className="search-clear" onClick={() => setSearch('')}>
                    <X size={13} />
                  </button>
                )}
              </div>

              <div className="records-list">
                {briefs.map(b => (
                  <button
                    key={b.id}
                    className={`record-card ${selectedId === b.id && !isCreating ? 'active' : ''}`}
                    onClick={() => handleSelect(b)}
                  >
                    <div className="record-avatar">
                      {b.company_name.slice(0, 1).toUpperCase()}
                    </div>
                    <div className="record-details">
                      <b>{b.company_name}</b>
                      <div className="record-meta">
                        <span><MapPin size={11} /> {b.location || 'Location not specified'}</span>
                        <span><Clock3 size={11} /> {new Date(b.updated_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <ArrowUpRight size={14} className="record-arrow" />
                  </button>
                ))}

                {!briefs.length && !loading && (
                  <div className="directory-empty">
                    <FileText size={28} />
                    <h4>No company briefs found</h4>
                    <p>
                      {search
                        ? 'No saved companies match your search criteria.'
                        : 'Your intelligence workspace is currently empty.'}
                    </p>
                    <button className="btn-text-action" onClick={handleStartNew}>
                      Create your first brief
                    </button>
                  </div>
                )}

                {loading && (
                  <div className="directory-loading">
                    <RefreshCw size={20} className="spinning" />
                    <span>Loading company records...</span>
                  </div>
                )}
              </div>
            </section>

            {/* RIGHT: EDITOR WORKSPACE */}
            <section className="editor-panel">
              {selectedId || isCreating ? (
                <form onSubmit={handleSave} className="editor-form">
                  <div className="editor-header">
                    <div>
                      <span className="eyebrow">
                        {isCreating ? 'NEW RECORD' : `BRIEF #${selectedId}`}
                      </span>
                      <h2>
                        {isCreating
                          ? 'Create Company Intelligence Brief'
                          : form.company_name || 'Company Intelligence Brief'}
                      </h2>
                      {!isCreating && selectedBrief?.updated_at && (
                        <p className="timestamp">
                          Last updated: {new Date(selectedBrief.updated_at).toLocaleString()}
                        </p>
                      )}
                    </div>

                    <div className="editor-actions">
                      {!isCreating && (
                        <>
                          <button
                            type="button"
                            className="btn-secondary"
                            onClick={copyMarkdownBrief}
                            title="Copy full brief in Markdown format"
                          >
                            {copiedBrief ? <Check size={15} /> : <Copy size={15} />}
                            <span>{copiedBrief ? 'Copied' : 'Export'}</span>
                          </button>
                          <button
                            type="button"
                            className="btn-danger"
                            onClick={handleDelete}
                            disabled={saving}
                            title="Delete this company brief"
                          >
                            <Trash2 size={15} />
                          </button>
                        </>
                      )}
                      <button type="submit" className="primary-btn" disabled={saving}>
                        <Save size={15} />
                        <span>{saving ? 'Saving...' : 'Save Changes'}</span>
                      </button>
                    </div>
                  </div>

                  {notice && (
                    <div className="alert alert-success">
                      <Check size={15} />
                      <span>{notice}</span>
                    </div>
                  )}

                  <div className="form-sections">
                    {/* SECTION 1: FIRMOGRAPHICS */}
                    <div className="form-card">
                      <div className="form-card-title">
                        <Building2 size={15} />
                        <span>Firmographics & Company Context</span>
                      </div>
                      <div className="form-grid-3">
                        <label className="field-group required">
                          <span>Company Name <em>*</em></span>
                          <input
                            type="text"
                            required
                            placeholder="e.g. ABC Infrastructure"
                            value={form.company_name}
                            onChange={e => updateField('company_name', e.target.value)}
                          />
                        </label>

                        <label className="field-group">
                          <span>Industry</span>
                          <input
                            type="text"
                            placeholder="e.g. Paint / Commercial Construction"
                            value={form.industry}
                            onChange={e => updateField('industry', e.target.value)}
                          />
                        </label>

                        <label className="field-group">
                          <span>Location</span>
                          <input
                            type="text"
                            placeholder="e.g. Hyderabad, Telangana"
                            value={form.location}
                            onChange={e => updateField('location', e.target.value)}
                          />
                        </label>
                      </div>

                      <label className="field-group full-width">
                        <span>Company Overview</span>
                        <textarea
                          rows={4}
                          placeholder="Summarise core business model, key operating divisions, regional footprint, and scale..."
                          value={form.company_overview}
                          onChange={e => updateField('company_overview', e.target.value)}
                        />
                      </label>
                    </div>

                    {/* SECTION 2: PAINT INTELLIGENCE & SIGNALS */}
                    <div className="form-card">
                      <div className="form-card-title">
                        <Sparkles size={15} />
                        <span>Commercial Paint Intelligence & Project Signals</span>
                      </div>
                      <div className="form-grid-2">
                        <label className="field-group">
                          <span>Potential Paint Requirements</span>
                          <textarea
                            rows={4}
                            placeholder="Identify industrial coatings, high-build epoxy flooring, anti-carbonation paints, or architectural finishes..."
                            value={form.potential_paint_requirements}
                            onChange={e => updateField('potential_paint_requirements', e.target.value)}
                          />
                        </label>

                        <label className="field-group">
                          <span>Relevant Project Signals</span>
                          <textarea
                            rows={4}
                            placeholder="Track tender awards, new construction permits, plant expansions, capital expenditure announcements..."
                            value={form.project_signals}
                            onChange={e => updateField('project_signals', e.target.value)}
                          />
                        </label>
                      </div>
                    </div>

                    {/* SECTION 3: MEETING PREP & NEXT STEPS */}
                    <div className="form-card">
                      <div className="form-card-title">
                        <Clock3 size={15} />
                        <span>Meeting Preparation & Sales Action Items</span>
                      </div>
                      <div className="form-grid-2">
                        <label className="field-group">
                          <span>Meeting Preparation Questions</span>
                          <textarea
                            rows={4}
                            placeholder="Formulate qualification questions: specifications required, surface prep standards, procurement cycle, decision makers..."
                            value={form.meeting_questions}
                            onChange={e => updateField('meeting_questions', e.target.value)}
                          />
                        </label>

                        <label className="field-group">
                          <span>Next Steps & Follow-ups</span>
                          <textarea
                            rows={4}
                            placeholder="Action items, deliverables, quote preparation, sample batch dispatch, account owner assignments..."
                            value={form.next_steps}
                            onChange={e => updateField('next_steps', e.target.value)}
                          />
                        </label>
                      </div>
                    </div>

                    {/* SECTION 4: CITATIONS & SOURCES */}
                    <div className="form-card">
                      <div className="form-card-title">
                        <Globe size={15} />
                        <span>Sources & Reference URLs</span>
                      </div>
                      <label className="field-group full-width">
                        <textarea
                          rows={3}
                          placeholder="Paste reference links, news articles, tender notices, or official website URLs (one per line)..."
                          value={form.source_urls}
                          onChange={e => updateField('source_urls', e.target.value)}
                        />
                      </label>
                    </div>
                  </div>
                </form>
              ) : (
                <div className="welcome-state">
                  <div className="welcome-icon">
                    <Building2 size={36} />
                  </div>
                  <span className="eyebrow">READY FOR INTELLIGENCE</span>
                  <h2>Select or Create a Company Brief</h2>
                  <p>
                    Choose an existing company from the directory on the left, create a new record manually,
                    or ask Claude to research and save a company brief directly via MCP.
                  </p>
                  <div className="welcome-actions">
                    <button className="primary-btn" onClick={handleStartNew}>
                      <Plus size={16} /> Create Company Brief
                    </button>
                    <button className="btn-secondary" onClick={() => setShowMcpModal(true)}>
                      <Sparkles size={16} /> How Claude Connects
                    </button>
                  </div>

                  <div className="workflow-steps">
                    <h4>The MASCoT + Claude Workflow</h4>
                    <div className="steps-grid">
                      <div className="step-card">
                        <div className="step-num">01</div>
                        <b>Prompt Claude</b>
                        <p>Ask your Claude account to research a prospective infrastructure or commercial company.</p>
                      </div>
                      <div className="step-card">
                        <div className="step-num">02</div>
                        <b>MCP Storage</b>
                        <p>Claude invokes <code>create_company_brief</code> via MCP to save the structured intelligence.</p>
                      </div>
                      <div className="step-card">
                        <div className="step-num">03</div>
                        <b>Collaborate & Edit</b>
                        <p>Review and edit notes in MASCoT. Both Claude and your web application stay 100% synchronised.</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </section>
          </div>

          <footer className="app-footer">
            <span>MASCoT – Company Intelligence Workspace · Built for Volopay Product & Tech Assignment</span>
            <span className="footer-dot">•</span>
            <span>External Intelligence via MCP · No Embedded AI</span>
          </footer>
        </div>
      </main>

      {/* CLAUDE & MCP INTEGRATION MODAL */}
      {showMcpModal && (
        <div className="modal-backdrop" onClick={() => setShowMcpModal(false)}>
          <div className="modal-dialog" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title">
                <Sparkles size={18} />
                <h3>Connect Claude to MASCoT via MCP</h3>
              </div>
              <button className="modal-close" onClick={() => setShowMcpModal(false)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              <div className="architecture-callout">
                <b>Architecture Principle: Zero In-App AI</b>
                <p>
                  MASCoT does not contain any AI models, LLM API keys, or embedded chatbots.
                  You connect your own Claude account through the Model Context Protocol (MCP).
                  Claude performs the reasoning and synthesis; MASCoT permanently persists, retrieves, and edits the records.
                </p>
              </div>

              <h4>1. Configure Claude MCP Connector</h4>
              <p>Select your deployment environment and add this configuration to your <code>claude_desktop_config.json</code>:</p>
              
              <div style={{ display: 'flex', gap: '8px', margin: '8px 0' }}>
                <button
                  type="button"
                  className={mcpTab === 'cloud' ? 'btn-secondary active' : 'btn-secondary'}
                  style={{ background: mcpTab === 'cloud' ? '#eef5f2' : '#fff', borderColor: mcpTab === 'cloud' ? '#2e7a5c' : '#dce1e7', fontWeight: 600, fontSize: '11.5px' }}
                  onClick={() => setMcpTab('cloud')}
                >
                  Cloud / Production (Streamable HTTP)
                </button>
                <button
                  type="button"
                  className={mcpTab === 'local' ? 'btn-secondary active' : 'btn-secondary'}
                  style={{ background: mcpTab === 'local' ? '#eef5f2' : '#fff', borderColor: mcpTab === 'local' ? '#2e7a5c' : '#dce1e7', fontWeight: 600, fontSize: '11.5px' }}
                  onClick={() => setMcpTab('local')}
                >
                  Local Development (localhost:8001)
                </button>
              </div>

              <div className="code-block-container">
                <pre><code>{activeMcpConfig}</code></pre>
                <button
                  className="copy-code-btn"
                  onClick={() => {
                    navigator.clipboard.writeText(activeMcpConfig)
                    setCopiedConfig(true)
                    setTimeout(() => setCopiedConfig(false), 2000)
                  }}
                >
                  {copiedConfig ? <Check size={14} /> : <Copy size={14} />}
                  <span>{copiedConfig ? 'Copied' : 'Copy JSON'}</span>
                </button>
              </div>

              <h4>2. Sample Prompts to Try with Claude</h4>
              <div className="prompt-cards">
                {samplePrompts.map((p, idx) => (
                  <div key={idx} className="prompt-card">
                    <div className="prompt-header">
                      <b>{p.title}</b>
                      <button
                        className="copy-prompt-btn"
                        onClick={() => {
                          navigator.clipboard.writeText(p.text)
                          setCopiedPrompt(idx)
                          setTimeout(() => setCopiedPrompt(null), 2000)
                        }}
                      >
                        {copiedPrompt === idx ? <Check size={13} /> : <Copy size={13} />}
                        <span>{copiedPrompt === idx ? 'Copied Prompt' : 'Copy'}</span>
                      </button>
                    </div>
                    <p>"{p.text}"</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="modal-footer">
              <button className="primary-btn" onClick={() => setShowMcpModal(false)}>
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
