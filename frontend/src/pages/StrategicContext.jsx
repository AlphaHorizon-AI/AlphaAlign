import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Save, FileText, CheckCircle2 } from 'lucide-react';
import api from '../api/client';

export default function StrategicContext() {
  const { projectId } = useParams();
  const [context, setContext] = useState({
    strategic_goals: '',
    regulatory_constraints: '',
    incumbent_vendors: '',
    internal_capabilities: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadContext();
  }, [projectId]);

  const loadContext = async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/projects/${projectId}`);
      setContext({
        strategic_goals: data.strategic_goals || '',
        regulatory_constraints: data.regulatory_constraints || '',
        incumbent_vendors: data.incumbent_vendors || '',
        internal_capabilities: data.internal_capabilities || '',
      });
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const saveContext = async () => {
    setSaving(true);
    try {
      await api.patch(`/projects/${projectId}`, context);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-muted">Loading strategic context...</div>;

  return (
    <>
      <div className="page-header">
        <h2>Strategic Business Context</h2>
        <p>Provide qualitative business context to enhance the final AI narrative recommendations.</p>
      </div>
      
      <div className="page-content max-w-4xl">
        <div className="card mb-6" style={{ padding: '24px' }}>
          <div className="flex items-center gap-3 mb-6 pb-4" style={{ borderBottom: '1px solid var(--border-color)' }}>
            <div style={{ background: 'var(--accent-glow)', padding: '10px', borderRadius: '12px' }}>
              <FileText size={24} className="text-accent" />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.2rem' }}>LLM Context Enrichment</h3>
              <p className="text-sm text-muted" style={{ margin: 0, marginTop: '4px' }}>
                This information is injected directly into the LLM prompt during report generation to provide tailored, context-aware analysis.
              </p>
            </div>
          </div>

          <div className="grid gap-6">
            <div className="form-group">
              <label className="form-label" style={{ fontSize: '1rem', fontWeight: 600 }}>Top Business Goals for AI</label>
              <p className="text-xs text-muted mb-2">What are the primary drivers? (e.g., Operational efficiency, new revenue streams, customer experience)</p>
              <textarea 
                className="form-textarea" 
                rows={4} 
                value={context.strategic_goals}
                onChange={e => setContext({...context, strategic_goals: e.target.value})}
                placeholder="Our primary goal for AI is to..."
              />
            </div>

            <div className="form-group">
              <label className="form-label" style={{ fontSize: '1rem', fontWeight: 600 }}>Incumbent Tech Stack & Vendors</label>
              <p className="text-xs text-muted mb-2">Are you heavily invested in specific ecosystems? (e.g., "We are a Microsoft shop", "Heavy AWS footprint")</p>
              <textarea 
                className="form-textarea" 
                rows={3} 
                value={context.incumbent_vendors}
                onChange={e => setContext({...context, incumbent_vendors: e.target.value})}
                placeholder="Currently, our primary infrastructure is hosted on..."
              />
            </div>

            <div className="form-group">
              <label className="form-label" style={{ fontSize: '1rem', fontWeight: 600 }}>Regulatory & Compliance Constraints</label>
              <p className="text-xs text-muted mb-2">List any specific frameworks or data sovereignty needs. (e.g., GDPR, HIPAA, SOC2, local data storage)</p>
              <textarea 
                className="form-textarea" 
                rows={3} 
                value={context.regulatory_constraints}
                onChange={e => setContext({...context, regulatory_constraints: e.target.value})}
                placeholder="We operate in a highly regulated industry requiring..."
              />
            </div>

            <div className="form-group">
              <label className="form-label" style={{ fontSize: '1rem', fontWeight: 600 }}>Internal AI Capabilities & Talent</label>
              <p className="text-xs text-muted mb-2">Assess your current internal readiness. Do you have dedicated data scientists and MLOps engineers?</p>
              <textarea 
                className="form-textarea" 
                rows={3} 
                value={context.internal_capabilities}
                onChange={e => setContext({...context, internal_capabilities: e.target.value})}
                placeholder="Currently, we have limited internal data science talent..."
              />
            </div>
          </div>

          <div className="flex justify-end mt-8">
            <button 
              className="btn btn-primary" 
              onClick={saveContext}
              disabled={saving}
              style={{ minWidth: '140px', display: 'flex', justifyContent: 'center' }}
            >
              {saving ? 'Saving...' : saved ? (
                <><CheckCircle2 size={16} /> Saved Successfully</>
              ) : (
                <><Save size={16} /> Save Context</>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
