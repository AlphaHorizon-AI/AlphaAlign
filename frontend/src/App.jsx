import { Routes, Route, NavLink, useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
  Home as HomeIcon, LayoutDashboard, ListChecks, FileSpreadsheet,
  Upload, Calculator, Target, Shield, Brain, Download, Settings,
  ChevronRight, FolderOpen, Plus, BookOpen, HelpCircle, Info, FileText, Power
} from 'lucide-react';

import Home from './pages/Home';
import ProjectDashboard from './pages/ProjectDashboard';
import CriteriaBuilder from './pages/CriteriaBuilder';
import SurveyGenerator from './pages/SurveyGenerator';
import UploadValidation from './pages/UploadValidation';
import AHPResults from './pages/AHPResults';
import Recommendation from './pages/Recommendation';
import StrategicImportance from './pages/StrategicImportance';
import StrategicContext from './pages/StrategicContext';
import LLMAnalysis from './pages/LLMAnalysis';
import ExportReport from './pages/ExportReport';
import SettingsPage from './pages/SettingsPage';
import ReferenceManual from './pages/ReferenceManual';
import api from './api/client';

function Sidebar({ projectId }) {
  const navigate = useNavigate();
  const [recentProjects, setRecentProjects] = useState([]);

  useEffect(() => {
    api.get('/projects').then(r => setRecentProjects((r.data || []).slice(0, 5))).catch(() => {});
  }, [projectId]);

  const projectNav = projectId ? [
    { to: `/project/${projectId}`, icon: LayoutDashboard, label: 'Dashboard', section: 'Assessment' },
    { to: `/project/${projectId}/criteria`, icon: ListChecks, label: 'Evaluation Criteria', section: null },
    { to: `/project/${projectId}/strategic-context`, icon: FileText, label: 'Strategic Context', section: null },
    { to: `/project/${projectId}/survey`, icon: FileSpreadsheet, label: 'Survey Generator', section: null },
    { to: `/project/${projectId}/upload`, icon: Upload, label: 'Upload & Validate', section: null },
    { to: `/project/${projectId}/ahp`, icon: Calculator, label: 'AHP Results', section: 'Analysis' },
    { to: `/project/${projectId}/recommendation`, icon: Target, label: 'Recommendation', section: null },
    { to: `/project/${projectId}/strategic`, icon: Shield, label: 'Strategic Importance', section: null },
    { to: `/project/${projectId}/llm`, icon: Brain, label: 'LLM Analysis', section: 'Output' },
    { to: `/project/${projectId}/export`, icon: Download, label: 'Export Report', section: null },
  ] : [];

  let lastSection = null;

  return (
    <aside className="sidebar">
      <div className="sidebar-logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
        <img src="/logo.png" alt="AlphaAlign" style={{ width: 60, height: 60 }} />
      </div>
      <nav className="sidebar-nav">
        <NavLink to="/" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <HomeIcon /> Home
        </NavLink>

        {/* Project-specific navigation */}
        {projectNav.map(item => {
          const showSection = item.section && item.section !== lastSection;
          if (item.section) lastSection = item.section;
          return (
            <div key={item.to}>
              {showSection && <div className="nav-section-label">{item.section}</div>}
              <NavLink to={item.to} end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <item.icon /> {item.label}
              </NavLink>
            </div>
          );
        })}

        {/* When no project is selected, show recent projects */}
        {!projectId && (
          <>
            <div className="nav-section-label">Recent Assessments</div>
            {recentProjects.map(p => (
              <div
                key={p.id}
                className="nav-item"
                onClick={() => navigate(`/project/${p.id}`)}
                style={{ cursor: 'pointer' }}
              >
                <FolderOpen /> <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{p.name}</span>
              </div>
            ))}
            {recentProjects.length === 0 && (
              <div className="nav-item" style={{ opacity: 0.4, pointerEvents: 'none' }}>
                <FolderOpen /> No assessments yet
              </div>
            )}
            <div className="nav-section-label">Quick Actions</div>
            <div className="nav-item" onClick={() => {
              const event = new CustomEvent('open-create-modal');
              window.dispatchEvent(event);
            }} style={{ cursor: 'pointer' }}>
              <Plus /> New Assessment
            </div>

          </>
        )}
        {/* Bottom nav - always visible */}
        <div style={{ marginTop: 'auto', paddingTop: 16, borderTop: '1px solid var(--border-subtle)' }}>
          <NavLink to="/reference" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <BookOpen /> Reference Manual
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Settings /> Settings
          </NavLink>
          <div
            className="nav-item nav-item-shutdown"
            onClick={() => {
              if (window.confirm('Shut down AlphaAlign?\n\nThis will stop the backend and frontend servers.')) {
                api.post('/shutdown').then(() => {
                  document.title = 'AlphaAlign — Shut Down';
                  document.body.innerHTML = `
                    <div style="display:flex;align-items:center;justify-content:center;height:100vh;background:#07070d;color:#e8e8f0;font-family:Inter,sans-serif;flex-direction:column;gap:16px">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#26a69a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/></svg>
                      <h2 style="font-size:1.5rem;font-weight:700">AlphaAlign has been shut down</h2>
                      <p style="color:#9a9ab0">You can safely close this tab.</p>
                    </div>`;
                  setTimeout(() => window.close(), 3000);
                }).catch(() => {
                  alert('Could not reach the server. It may already be stopped.');
                });
              }
            }}
            style={{ cursor: 'pointer' }}
          >
            <Power /> Shut Down
          </div>
          <div className="nav-item" style={{ opacity: 0.4, pointerEvents: 'none', fontSize: '0.75rem' }}>
            <Info /> v1.0.0
          </div>
        </div>
      </nav>
    </aside>
  );
}

function ProjectLayout() {
  const { projectId } = useParams();
  return (
    <div className="app-layout">
      <Sidebar projectId={projectId} />
      <main className="main-content">
        <Routes>
          <Route index element={<ProjectDashboard />} />
          <Route path="criteria" element={<CriteriaBuilder />} />
          <Route path="strategic-context" element={<StrategicContext />} />
          <Route path="survey" element={<SurveyGenerator />} />
          <Route path="upload" element={<UploadValidation />} />
          <Route path="ahp" element={<AHPResults />} />
          <Route path="recommendation" element={<Recommendation />} />
          <Route path="strategic" element={<StrategicImportance />} />
          <Route path="llm" element={<LLMAnalysis />} />
          <Route path="export" element={<ExportReport />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={
        <div className="app-layout">
          <Sidebar />
          <main className="main-content"><Home /></main>
        </div>
      } />
      <Route path="/settings" element={
        <div className="app-layout">
          <Sidebar />
          <main className="main-content"><SettingsPage /></main>
        </div>
      } />
      <Route path="/reference" element={
        <div className="app-layout">
          <Sidebar />
          <main className="main-content"><ReferenceManual /></main>
        </div>
      } />
      <Route path="/project/:projectId/*" element={<ProjectLayout />} />
    </Routes>
  );
}
