import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Brain, Zap, AlertTriangle, Eye, RefreshCw } from 'lucide-react';
import api from '../api/client';

export default function LLMAnalysis() {
  const { projectId } = useParams();
  const [settings, setSettings] = useState({ provider:'', model:'', endpoint:'', api_key:'', temperature:0.7, max_tokens:2000, use_local:false, anonymize_input:false, enabled:false });
  const [analyses, setAnalyses] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [selectedType, setSelectedType] = useState('executive_summary');
  const [saved, setSaved] = useState(false);

  useEffect(() => { loadSettings(); loadAnalyses(); }, [projectId]);

  const loadSettings = async () => {
    try { const { data } = await api.get(`/projects/${projectId}/llm-settings`); setSettings(s => ({...s,...data})); } catch {}
  };
  const loadAnalyses = async () => {
    try { const { data } = await api.get(`/projects/${projectId}/llm-analysis`); setAnalyses(data); } catch {}
  };

  const saveSettings = async () => {
    try { await api.post(`/projects/${projectId}/llm-settings`, settings); setSaved(true); setTimeout(()=>setSaved(false),2000); } catch(e) { alert('Failed to save'); }
  };

  const testConnection = async () => {
    try {
      const { data } = await api.post(`/projects/${projectId}/test-llm-connection`);
      alert(data.connected ? `✓ Connected to ${settings.provider}` : `✗ Connection failed: ${data.error}`);
    } catch(e) { alert('Connection test failed'); }
  };

  const generate = async () => {
    setGenerating(true);
    try {
      const { data } = await api.post(`/projects/${projectId}/generate-llm-analysis`, { analysis_type: selectedType });
      loadAnalyses();
    } catch(e) { alert(e.response?.data?.detail || 'Generation failed'); }
    setGenerating(false);
  };

  const analysisLabels = {
    executive_summary: 'Executive Summary',
    risk_analysis: 'Risk Analysis',
    alignment_interpretation: 'Leadership Alignment Interpretation',
    roadmap: 'Implementation Roadmap',
  };

  return (
    <>
      <div className="page-header">
        <h2>LLM Analysis</h2>
        <p>Optional AI-powered strategic interpretation and narrative generation</p>
      </div>
      <div className="page-content">
        {/* Warning */}
        <div className="alert alert-warning mb-6">
          <AlertTriangle size={18} />
          <div>
            <strong>Data Privacy Notice:</strong> External LLM analysis may send assessment data to the selected provider.
            Use local LLM mode (Ollama) for sensitive or confidential assessments. Enable anonymization to strip identifying details.
          </div>
        </div>

        {/* Settings */}
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="card-title"><Brain size={18} style={{display:'inline',marginRight:8}} /> LLM Configuration</h3>
            <label className="flex items-center gap-2" style={{cursor:'pointer'}}>
              <input type="checkbox" checked={settings.enabled} onChange={e => setSettings({...settings,enabled:e.target.checked})} />
              <span className="text-sm font-semibold">{settings.enabled ? 'Enabled' : 'Disabled'}</span>
            </label>
          </div>

          {settings.enabled && (
            <>
              <div className="grid grid-3">
                <div className="form-group"><label className="form-label">Provider</label>
                  <select className="form-select" value={settings.provider} onChange={e => setSettings({...settings,provider:e.target.value})}>
                    <option value="">Select provider</option>
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="google">Google (Gemini)</option>
                    <option value="ollama">Ollama (Local)</option>
                    <option value="lmstudio">LM Studio (Local)</option>
                    <option value="azure">Azure OpenAI</option>
                    <option value="custom">Custom Endpoint</option>
                  </select></div>
                <div className="form-group"><label className="form-label">Model</label>
                  <input className="form-input" value={settings.model} onChange={e => setSettings({...settings,model:e.target.value})} placeholder="e.g. gpt-4o, claude-3.5-sonnet, llama3" /></div>
                <div className="form-group"><label className="form-label">Endpoint (optional)</label>
                  <input className="form-input" value={settings.endpoint} onChange={e => setSettings({...settings,endpoint:e.target.value})} placeholder="Custom endpoint URL" /></div>
              </div>
              {!['ollama','lmstudio'].includes(settings.provider) && (
                <div className="form-group"><label className="form-label">API Key</label>
                  <input className="form-input" type="password" value={settings.api_key} onChange={e => setSettings({...settings,api_key:e.target.value})} placeholder="sk-..." /></div>
              )}
              <div className="grid grid-3">
                <div className="form-group"><label className="form-label">Temperature</label>
                  <input className="form-input" type="number" step="0.1" min="0" max="2" value={settings.temperature} onChange={e => setSettings({...settings,temperature:parseFloat(e.target.value)})} /></div>
                <div className="form-group"><label className="form-label">Max Tokens</label>
                  <input className="form-input" type="number" value={settings.max_tokens} onChange={e => setSettings({...settings,max_tokens:parseInt(e.target.value)})} /></div>
                <div className="form-group"><label className="form-label">Options</label>
                  <label className="flex items-center gap-2 mt-2" style={{cursor:'pointer'}}>
                    <input type="checkbox" checked={settings.anonymize_input} onChange={e => setSettings({...settings,anonymize_input:e.target.checked})} />
                    <span className="text-sm">Anonymize data before sending</span>
                  </label></div>
              </div>
              <div className="flex gap-2">
                <button className="btn btn-secondary" onClick={testConnection}><Zap size={16} /> Test Connection</button>
                <button className="btn btn-primary" onClick={saveSettings}>{saved ? '✓ Saved' : 'Save Settings'}</button>
              </div>
            </>
          )}
        </div>

        {/* Generate */}
        {settings.enabled && (
          <div className="card mb-6">
            <h3 className="card-title mb-4">Generate Analysis</h3>
            <div className="flex gap-2 items-center">
              <select className="form-select" style={{width:'auto'}} value={selectedType} onChange={e => setSelectedType(e.target.value)}>
                {Object.entries(analysisLabels).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
              </select>
              <button className="btn btn-primary" onClick={generate} disabled={generating || !settings.provider}>
                {generating ? <div className="loading-spinner" /> : <Brain size={18} />}
                {generating ? 'Generating...' : 'Generate'}
              </button>
            </div>
          </div>
        )}

        {/* Results */}
        {analyses.length > 0 && (
          <div className="flex flex-col gap-4">
            {analyses.map(a => (
              <div key={a.id} className="card">
                <div className="flex items-center justify-between mb-3">
                  <span className="badge badge-info">{analysisLabels[a.analysis_type] || a.analysis_type}</span>
                  <span className="text-xs text-muted">{a.provider} / {a.model} · {new Date(a.created_at).toLocaleString()}</span>
                </div>
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8, fontSize: '0.9rem' }}>{a.text}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
