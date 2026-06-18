import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Target, TrendingUp, ArrowRight, Map, Users, Award } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';
import api from '../api/client';

export default function Recommendation() {
  const { projectId } = useParams();
  const [results, setResults] = useState(null);

  useEffect(() => {
    api.get(`/projects/${projectId}/ahp-results`).then(r => setResults(r.data)).catch(() => {});
  }, [projectId]);

  if (!results || !results.recommendation) return (
    <><div className="page-header"><h2>Architecture Recommendation</h2><p>Run the AHP calculation first to see the recommendation</p></div>
    <div className="page-content"><div className="empty-state"><Target size={48} /><h3>No recommendation available</h3><p>Go to AHP Results and run the calculation.</p></div></div></>
  );

  const rec = results.recommendation;
  const outcomeColors = { vendor: '#42a5f5', hybrid: '#26a69a', independent: '#7c4dff' };

  // Radar chart data
  const radarData = rec.top_drivers?.map(d => ({
    criterion: d.name.substring(0, 15),
    weight: Math.round(d.weight * 100),
  })) || [];

  return (
    <>
      <div className="page-header">
        <h2>Architecture Recommendation</h2>
        <p>Strategic AI architecture positioning based on AHP analysis</p>
      </div>
      <div className="page-content">
        {/* Hero Recommendation */}
        <div className="card mb-6 animate-score" style={{
          textAlign: 'center', padding: '40px 32px',
          background: 'linear-gradient(135deg, rgba(33,150,243,0.08), rgba(13,13,21,0.95))',
          border: '1px solid rgba(33,150,243,0.2)',
          boxShadow: '0 0 40px rgba(33,150,243,0.1)',
        }}>
          <div className="badge badge-info mb-4" style={{display:'inline-flex',marginBottom:16}}>
            <Award size={12} /> Recommended Position
          </div>
          <h2 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: 8 }}>{rec.recommended_label}</h2>
          <div style={{ fontSize: '3.5rem', fontWeight: 800, color: outcomeColors[rec.recommended_outcome], lineHeight: 1, marginBottom: 8 }}>
            {rec.recommended_score?.toFixed(0)}
          </div>
          <div className="text-sm text-muted">/ 100 — {rec.confidence} confidence</div>
        </div>

        {/* Score Comparison */}
        <div className="grid grid-3 mb-6">
          {rec.outcome_ranking?.map((o, i) => (
            <div key={o.outcome} className="card animate-in" style={{ textAlign: 'center', padding: '24px', animationDelay: `${i * 100}ms` }}>
              {i === 0 && <span className="badge badge-info" style={{display:'inline-flex',marginBottom:8}}>★ #{i+1}</span>}
              {i > 0 && <span className="badge badge-neutral" style={{display:'inline-flex',marginBottom:8}}>#{i+1}</span>}
              <div style={{ fontSize: '2rem', fontWeight: 800, color: outcomeColors[o.outcome], marginBottom: 4 }}>
                {o.final_score?.toFixed(0)}
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: 4 }}>{o.label}</div>
              {o.base_score !== o.final_score && (
                <div className="text-xs text-muted">Base: {o.base_score?.toFixed(0)} → Strategic: {o.final_score?.toFixed(0)}</div>
              )}
            </div>
          ))}
        </div>

        {/* Next Step vs Target State */}
        <div className="grid grid-2 mb-6">
          <div className="card">
            <h4 className="card-title" style={{marginBottom:12}}><ArrowRight size={16} style={{display:'inline',marginRight:6}} /> Recommended Next Step</h4>
            <div style={{fontSize:'1.1rem', fontWeight:600, color:'var(--accent-primary)'}}>{rec.next_step?.label}</div>
            <p className="text-sm text-muted mt-2">{rec.transition_reason}</p>
          </div>
          <div className="card">
            <h4 className="card-title" style={{marginBottom:12}}><TrendingUp size={16} style={{display:'inline',marginRight:6}} /> Long-Term Target State</h4>
            <div style={{fontSize:'1.1rem', fontWeight:600, color:'#7c4dff'}}>{rec.target_state?.label}</div>
          </div>
        </div>

        {/* Top Drivers */}
        <div className="grid grid-2 mb-6">
          <div className="card">
            <h4 className="card-title mb-4">Top Decision Drivers</h4>
            {rec.top_drivers?.map((d, i) => (
              <div key={d.criterion_id} className="flex items-center justify-between" style={{ padding: '8px 0', borderBottom: i < rec.top_drivers.length-1 ? '1px solid var(--border-subtle)' : 'none' }}>
                <span style={{fontWeight:500}}>{d.name}</span>
                <span className="badge badge-info">{(d.weight * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
          {radarData.length > 0 && (
            <div className="card">
              <h4 className="card-title mb-4">Driver Distribution</h4>
              <div style={{height:250}}>
                <ResponsiveContainer>
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.08)" />
                    <PolarAngleAxis dataKey="criterion" tick={{fill:'#9a9ab0',fontSize:11}} />
                    <Radar dataKey="weight" stroke="#2196f3" fill="rgba(33,150,243,0.15)" strokeWidth={2} />
                    <Tooltip contentStyle={{background:'#1a1a2e',border:'1px solid rgba(255,255,255,0.1)',borderRadius:8,color:'#e8e8f0'}} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>

        {/* Roadmap */}
        {rec.roadmap && (
          <div className="card mb-6">
            <h4 className="card-title mb-4"><Map size={16} style={{display:'inline',marginRight:6}} /> Recommended Roadmap</h4>
            <div className="flex flex-col gap-3">
              {rec.roadmap.map((phase, i) => (
                <div key={i} className="flex gap-4 animate-in" style={{animationDelay:`${i*80}ms`}}>
                  <div style={{
                    minWidth:100, padding:'8px 14px', borderRadius:'var(--radius-md)',
                    background:'var(--accent-glow)', color:'var(--accent-primary)',
                    fontWeight:600, fontSize:'0.85rem', textAlign:'center',
                  }}>{phase.phase}</div>
                  <div style={{flex:1,padding:'8px 0',borderBottom:'1px solid var(--border-subtle)'}}>
                    <span style={{fontSize:'0.9rem'}}>{phase.focus}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Alignment Summary */}
        {rec.alignment_summary && (
          <div className="card">
            <h4 className="card-title mb-2"><Users size={16} style={{display:'inline',marginRight:6}} /> Leadership Alignment</h4>
            <p className="text-sm" style={{lineHeight:1.7}}>{rec.alignment_summary}</p>
          </div>
        )}

        {/* Interpretation */}
        <div className="card mt-4" style={{background:'linear-gradient(135deg,rgba(33,150,243,0.05),transparent)'}}>
          <h4 className="card-title mb-2">Interpretation</h4>
          <p style={{lineHeight:1.8,fontSize:'0.95rem'}}>{rec.interpretation}</p>
        </div>
      </div>
    </>
  );
}
