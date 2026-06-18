import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Calculator, RefreshCw, Users, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import api from '../api/client';

export default function AHPResults() {
  const { projectId } = useParams();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [project, setProject] = useState(null);

  useEffect(() => { load(); }, [projectId]);

  const load = async () => {
    try {
      const { data: p } = await api.get(`/projects/${projectId}`);
      setProject(p);
      try { const { data } = await api.get(`/projects/${projectId}/ahp-results`); setResults(data); } catch {}
    } catch(e) { console.error(e); }
  };

  const runCalculation = async () => {
    setLoading(true);
    try {
      const { data } = await api.post(`/projects/${projectId}/calculate-ahp`);
      setResults(data);
    } catch(e) { alert(e.response?.data?.detail || 'Calculation failed'); }
    setLoading(false);
  };

  const updateAggregation = async (method) => {
    try {
      await api.patch(`/projects/${projectId}`, { aggregation_method: method });
      runCalculation();
    } catch(e) { console.error(e); }
  };

  // Prepare chart data
  const weightData = results ? Object.entries(results.criteria_weights || {}).map(([id, w]) => ({
    name: (results.criterion_names?.[id] || id).substring(0, 20),
    weight: Math.round(w * 1000) / 10,
    fullName: results.criterion_names?.[id] || id,
  })).sort((a, b) => b.weight - a.weight) : [];

  const crLabel = (cr) => {
    if (cr <= 0.1) return { text: 'Good', color: '#26a69a' };
    if (cr <= 0.2) return { text: 'Acceptable', color: '#f9a825' };
    return { text: 'Inconsistent', color: '#ef5350' };
  };

  return (
    <>
      <div className="page-header">
        <h2>AHP Results</h2>
        <p>Criteria weighting and consistency analysis</p>
      </div>
      <div className="page-content">
        {/* Calculate button */}
        <div className="card mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="card-title">Run AHP Calculation</h3>
              <p className="text-sm text-muted mt-2">
                Calculate criteria weights from pairwise comparisons using the geometric mean method.
              </p>
            </div>
            <div className="flex gap-2 items-center">
              <select className="form-select" style={{width:'auto'}} value={project?.aggregation_method || 'equal'} onChange={e => updateAggregation(e.target.value)}>
                <option value="equal">Equal Weighting</option>
                <option value="role_based">Role-Based Weighting</option>
                <option value="custom">Custom Weighting</option>
              </select>
              <button className="btn btn-primary" onClick={runCalculation} disabled={loading}>
                {loading ? <div className="loading-spinner" /> : <Calculator size={18} />}
                {loading ? 'Calculating...' : results ? 'Recalculate' : 'Calculate'}
              </button>
            </div>
          </div>
        </div>

        {!results ? (
          <div className="empty-state">
            <BarChart3 size={48} />
            <h3>No results yet</h3>
            <p>Upload survey files and run the calculation to see AHP results.</p>
          </div>
        ) : (
          <>
            {/* Criteria Weights Chart */}
            <div className="card mb-6">
              <h3 className="card-title mb-4">Criteria Weights</h3>
              <div style={{ height: 350 }}>
                <ResponsiveContainer>
                  <BarChart data={weightData} layout="vertical" margin={{ left: 10, right: 20 }}>
                    <XAxis type="number" domain={[0, 'auto']} tick={{ fill: '#9a9ab0', fontSize: 12 }} tickFormatter={v => `${v}%`} />
                    <YAxis type="category" dataKey="name" width={160} tick={{ fill: '#e8e8f0', fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#e8e8f0' }}
                      formatter={(v, _, p) => [`${v}%`, p.payload.fullName]}
                    />
                    <Bar dataKey="weight" radius={[0, 6, 6, 0]}>
                      {weightData.map((_, i) => (
                        <Cell key={i} fill={`hsl(${210 + i * 8}, 80%, ${55 + i * 2}%)`} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Consistency Ratios */}
            <div className="card mb-6">
              <h3 className="card-title mb-4"><Users size={18} style={{display:'inline',marginRight:8}} /> Respondent Consistency</h3>
              <div className="table-container">
                <table>
                  <thead><tr><th>Respondent</th><th>Role</th><th>CR</th><th>Status</th></tr></thead>
                  <tbody>
                    {results.respondent_details && Object.entries(results.respondent_details).map(([id, d]) => {
                      const cr = crLabel(d.cr);
                      return (
                        <tr key={id}>
                          <td style={{fontWeight:500}}>{d.name}</td>
                          <td><span className="badge badge-neutral">{d.role || '—'}</span></td>
                          <td style={{fontFamily:'var(--font-mono)',fontSize:'0.85rem'}}>{d.cr?.toFixed(4)}</td>
                          <td><span className="badge" style={{background:`${cr.color}20`,color:cr.color}}>{cr.text}</span></td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Aggregation Method */}
            <div className="card">
              <div className="flex items-center gap-2">
                <span className="badge badge-info">{results.aggregation_method || 'equal'}</span>
                <span className="text-sm text-muted">Aggregation method used</span>
                {results.calculated_at && <span className="text-xs text-muted" style={{marginLeft:'auto'}}>Calculated: {new Date(results.calculated_at).toLocaleString()}</span>}
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
