import { useState, useEffect } from 'react';
import { Building2, Brain, Zap, Save, CheckCircle, Globe, Users, Server, Shield } from 'lucide-react';
import api from '../api/client';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('company');
  const [settings, setSettings] = useState({
    company_name: '', industry: '', company_size: '', headquarters: '', website: '',
    primary_contact: '', primary_contact_email: '', primary_vendor_ecosystem: '',
    key_systems: '', ai_maturity_level: '', notes: '',
    llm_provider: '', llm_model: '', llm_endpoint: '', llm_api_key: '',
    llm_temperature: 0.7, llm_max_tokens: 2000, llm_anonymize: false, llm_enabled: false,
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    api.get('/settings').then(r => setSettings(s => ({ ...s, ...r.data }))).catch(console.error);
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      const { data } = await api.put('/settings', settings);
      setSettings(s => ({ ...s, ...data }));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (e) { alert('Failed to save settings'); }
    setSaving(false);
  };

  const testConnection = async () => {
    setTestResult(null);
    try {
      // Simple connectivity test - try a health-check style call
      const providerEndpoints = {
        ollama: settings.llm_endpoint || 'http://localhost:11434',
        lmstudio: settings.llm_endpoint || 'http://localhost:1234',
      };
      setTestResult({ status: 'testing' });
      // We'll just validate the settings are filled in
      if (!settings.llm_provider) {
        setTestResult({ status: 'error', message: 'Select a provider first' });
        return;
      }
      if (!['ollama', 'lmstudio'].includes(settings.llm_provider) && !settings.llm_api_key) {
        setTestResult({ status: 'error', message: 'API key is required for cloud providers' });
        return;
      }
      if (!settings.llm_model) {
        setTestResult({ status: 'error', message: 'Model name is required' });
        return;
      }
      setTestResult({ status: 'ok', message: `Configuration looks valid for ${settings.llm_provider} / ${settings.llm_model}` });
    } catch (e) {
      setTestResult({ status: 'error', message: 'Validation failed' });
    }
  };

  const update = (field, value) => setSettings(s => ({ ...s, [field]: value }));

  const tabs = [
    { id: 'company', label: 'Company Profile', icon: Building2 },
    { id: 'ai', label: 'AI Model Setup', icon: Brain },
  ];

  return (
    <>
      <div className="page-header">
        <h2>Settings</h2>
        <p>Configure your company profile and default AI model settings</p>
      </div>
      <div className="page-content">
        {/* Tab bar */}
        <div className="flex gap-2 mb-6">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon size={16} /> {tab.label}
            </button>
          ))}
          <div style={{ flex: 1 }} />
          <button className="btn btn-primary" onClick={save} disabled={saving}>
            {saved ? <><CheckCircle size={16} /> Saved</> : saving ? <><div className="loading-spinner" /> Saving...</> : <><Save size={16} /> Save Settings</>}
          </button>
        </div>

        {/* Company Profile Tab */}
        {activeTab === 'company' && (
          <div className="card animate-in">
            <h3 className="card-title mb-4">
              <Building2 size={18} style={{ display: 'inline', marginRight: 8 }} />
              Company Profile
            </h3>
            <p className="text-sm text-muted mb-6">
              This information is used as defaults when creating new assessments and is included in exported reports.
            </p>

            <div className="grid grid-2">
              <div className="form-group">
                <label className="form-label">Company Name</label>
                <input className="form-input" value={settings.company_name} onChange={e => update('company_name', e.target.value)} placeholder="Your company name" />
              </div>
              <div className="form-group">
                <label className="form-label">Industry</label>
                <select className="form-select" value={settings.industry} onChange={e => update('industry', e.target.value)}>
                  <option value="">Select industry</option>
                  <option>Manufacturing</option><option>Financial Services</option>
                  <option>Healthcare</option><option>Technology</option><option>Retail</option>
                  <option>Energy</option><option>Government</option><option>Education</option>
                  <option>Professional Services</option><option>Other</option>
                </select>
              </div>
            </div>

            <div className="grid grid-2">
              <div className="form-group">
                <label className="form-label">Company Size</label>
                <select className="form-select" value={settings.company_size} onChange={e => update('company_size', e.target.value)}>
                  <option value="">Select size</option>
                  <option>1-50 employees</option><option>51-200 employees</option>
                  <option>201-1000 employees</option><option>1001-5000 employees</option>
                  <option>5001-10000 employees</option><option>10000+ employees</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Headquarters</label>
                <input className="form-input" value={settings.headquarters} onChange={e => update('headquarters', e.target.value)} placeholder="City, Country" />
              </div>
            </div>

            <div className="grid grid-2">
              <div className="form-group">
                <label className="form-label"><Globe size={14} style={{ display: 'inline', marginRight: 4 }} /> Website</label>
                <input className="form-input" value={settings.website} onChange={e => update('website', e.target.value)} placeholder="https://..." />
              </div>
              <div className="form-group">
                <label className="form-label">AI Maturity Level</label>
                <select className="form-select" value={settings.ai_maturity_level} onChange={e => update('ai_maturity_level', e.target.value)}>
                  <option value="">Select level</option>
                  <option>Exploring</option><option>Experimenting</option>
                  <option>Implementing</option><option>Scaling</option><option>Optimizing</option>
                </select>
              </div>
            </div>

            <div className="grid grid-2">
              <div className="form-group">
                <label className="form-label"><Users size={14} style={{ display: 'inline', marginRight: 4 }} /> Primary Contact</label>
                <input className="form-input" value={settings.primary_contact} onChange={e => update('primary_contact', e.target.value)} placeholder="Full name" />
              </div>
              <div className="form-group">
                <label className="form-label">Contact Email</label>
                <input className="form-input" type="email" value={settings.primary_contact_email} onChange={e => update('primary_contact_email', e.target.value)} placeholder="email@company.com" />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label"><Server size={14} style={{ display: 'inline', marginRight: 4 }} /> Primary Vendor Ecosystem</label>
              <input className="form-input" value={settings.primary_vendor_ecosystem} onChange={e => update('primary_vendor_ecosystem', e.target.value)} placeholder="e.g. Microsoft, SAP, Google Cloud, AWS" />
            </div>

            <div className="form-group">
              <label className="form-label">Key Systems</label>
              <textarea className="form-textarea" rows={2} value={settings.key_systems} onChange={e => update('key_systems', e.target.value)} placeholder="e.g. SAP S/4HANA, Salesforce, Dynamics 365, Snowflake..." />
            </div>

            <div className="form-group">
              <label className="form-label">Notes</label>
              <textarea className="form-textarea" rows={3} value={settings.notes} onChange={e => update('notes', e.target.value)} placeholder="Additional context about your company or AI strategy..." />
            </div>
          </div>
        )}

        {/* AI Model Setup Tab */}
        {activeTab === 'ai' && (
          <div className="card animate-in">
            <h3 className="card-title mb-4">
              <Brain size={18} style={{ display: 'inline', marginRight: 8 }} />
              Default AI Model Configuration
            </h3>
            <p className="text-sm text-muted mb-4">
              Configure the default LLM provider for AI-powered analysis. These settings are used as defaults for new assessments.
            </p>

            <div className="alert alert-warning mb-6">
              <Shield size={18} />
              <div>
                <strong>Data Privacy:</strong> Cloud providers (OpenAI, Anthropic, Azure) send data externally.
                Use local models (Ollama, LM Studio) for confidential assessments, or enable anonymization.
              </div>
            </div>

            <div className="flex items-center justify-between mb-6" style={{
              padding: '16px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)',
              border: `1px solid ${settings.llm_enabled ? 'rgba(38,166,154,0.3)' : 'var(--border-subtle)'}`,
            }}>
              <div>
                <span style={{ fontWeight: 600 }}>LLM Analysis</span>
                <span className="text-sm text-muted" style={{ marginLeft: 8 }}>
                  {settings.llm_enabled ? 'Enabled - AI analysis available in assessments' : 'Disabled - Enable to use AI-powered analysis'}
                </span>
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                <input type="checkbox" checked={settings.llm_enabled} onChange={e => update('llm_enabled', e.target.checked)} />
                <span style={{ fontWeight: 600, color: settings.llm_enabled ? '#26a69a' : 'var(--text-tertiary)' }}>
                  {settings.llm_enabled ? 'ON' : 'OFF'}
                </span>
              </label>
            </div>

            {settings.llm_enabled && (
              <>
                <div className="grid grid-3">
                  <div className="form-group">
                    <label className="form-label">Provider</label>
                    <select className="form-select" value={settings.llm_provider} onChange={e => update('llm_provider', e.target.value)}>
                      <option value="">Select provider</option>
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic</option>
                      <option value="google">Google (Gemini)</option>
                      <option value="openrouter">OpenRouter</option>
                      <option value="ollama">Ollama (Local)</option>
                      <option value="lmstudio">LM Studio (Local)</option>
                      <option value="azure">Azure OpenAI</option>
                      <option value="custom">Custom Endpoint</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Model</label>
                    <input className="form-input" value={settings.llm_model} onChange={e => update('llm_model', e.target.value)} placeholder="e.g. gpt-4o, claude-3.5-sonnet, llama3" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Endpoint (optional)</label>
                    <input className="form-input" value={settings.llm_endpoint} onChange={e => update('llm_endpoint', e.target.value)} placeholder="Custom URL" />
                  </div>
                </div>

                {!['ollama', 'lmstudio'].includes(settings.llm_provider) && (
                  <div className="form-group">
                    <label className="form-label">API Key</label>
                    <input className="form-input" type="password" value={settings.llm_api_key} onChange={e => update('llm_api_key', e.target.value)} placeholder="sk-..." />
                  </div>
                )}

                <div className="grid grid-3">
                  <div className="form-group">
                    <label className="form-label">Temperature</label>
                    <input className="form-input" type="number" step="0.1" min="0" max="2" value={settings.llm_temperature} onChange={e => update('llm_temperature', parseFloat(e.target.value))} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Max Tokens</label>
                    <input className="form-input" type="number" value={settings.llm_max_tokens} onChange={e => update('llm_max_tokens', parseInt(e.target.value))} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Options</label>
                    <label className="flex items-center gap-2 mt-2" style={{ cursor: 'pointer' }}>
                      <input type="checkbox" checked={settings.llm_anonymize} onChange={e => update('llm_anonymize', e.target.checked)} />
                      <span className="text-sm">Anonymize data before sending</span>
                    </label>
                  </div>
                </div>

                <div className="flex gap-2 mt-4">
                  <button className="btn btn-secondary" onClick={testConnection}>
                    <Zap size={16} /> Validate Configuration
                  </button>
                  {testResult && (
                    <span className={`badge ${testResult.status === 'ok' ? 'badge-success' : testResult.status === 'testing' ? 'badge-info' : 'badge-error'}`} style={{ alignSelf: 'center' }}>
                      {testResult.status === 'testing' ? 'Testing...' : testResult.message}
                    </span>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </>
  );
}
