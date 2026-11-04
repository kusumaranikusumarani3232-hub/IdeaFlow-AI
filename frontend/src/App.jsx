import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DashboardOverview from './components/DashboardOverview';
import ProjectWorkspace from './components/ProjectWorkspace';
import AICreativeStudio from './components/AICreativeStudio';
import SwitchInspector from './components/SwitchInspector';
import ProjectCompletion from './components/ProjectCompletion';
import IntegrationsModal from './components/IntegrationsModal';
import {
  fetchProjects,
  fetchProjectDetails,
  fetchSwitchStatus,
  fetchDiscordStatus,
  simulateDiscordMessage
} from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [switchStatus, setSwitchStatus] = useState(null);
  const [discordStatus, setDiscordStatus] = useState(null);
  const [demoMode, setDemoMode] = useState(true);
  const [loading, setLoading] = useState(true);

  // Load projects and statuses
  const loadData = async () => {
    try {
      const [projs, swStatus, dcStatus] = await Promise.all([
        fetchProjects().catch(() => []),
        fetchSwitchStatus().catch(() => null),
        fetchDiscordStatus().catch(() => null)
      ]);
      setProjects(projs);
      setSwitchStatus(swStatus);
      setDiscordStatus(dcStatus);

      // Select active project
      const currentId = selectedProjectId || projs[0]?.id;
      if (currentId) {
        setSelectedProjectId(currentId);
        const details = await fetchProjectDetails(currentId).catch(() => null);
        setSelectedProject(details);
      }
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, [selectedProjectId]);

  const handleRefreshProject = async () => {
    if (selectedProjectId) {
      try {
        const details = await fetchProjectDetails(selectedProjectId);
        setSelectedProject(details);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleTriggerSimulation = async (content) => {
    try {
      await simulateDiscordMessage(content);
      // Wait brief moment for agent to process and write to DB
      await new Promise((r) => setTimeout(r, 600));
      await loadData();
    } catch (err) {
      console.error('Simulation error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0d14] text-slate-100 flex flex-col selection:bg-emerald-500 selection:text-slate-950">
      {/* Background radial glows */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute -top-40 -left-40 w-[600px] h-[600px] bg-emerald-600/10 rounded-full blur-[128px]"></div>
        <div className="absolute top-1/2 -right-40 w-[500px] h-[500px] bg-cyan-600/10 rounded-full blur-[128px]"></div>
        <div className="absolute -bottom-40 left-1/3 w-[600px] h-[600px] bg-purple-600/5 rounded-full blur-[128px]"></div>
      </div>

      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          switchStatus={switchStatus}
          discordStatus={discordStatus}
          demoMode={demoMode}
          setDemoMode={setDemoMode}
        />

        <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8">
          {loading ? (
            <div className="py-24 text-center space-y-3">
              <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-xs font-mono text-slate-400">Connecting to Switch Agent Protocol...</p>
            </div>
          ) : (
            <>
              {activeTab === 'dashboard' && (
                <DashboardOverview
                  projects={projects}
                  selectedProject={selectedProject}
                  setSelectedProject={setSelectedProject}
                  setActiveTab={setActiveTab}
                  switchStatus={switchStatus}
                  onTriggerSimulation={handleTriggerSimulation}
                />
              )}

              {activeTab === 'workspace' && (
                <ProjectWorkspace
                  project={selectedProject}
                  onRefreshProject={handleRefreshProject}
                  onTriggerSimulation={handleTriggerSimulation}
                />
              )}

              {activeTab === 'studio' && (
                <AICreativeStudio
                  project={selectedProject}
                  onRefreshProject={handleRefreshProject}
                />
              )}

              {activeTab === 'inspector' && (
                <SwitchInspector
                  switchStatus={switchStatus}
                  onRefreshStatus={loadData}
                />
              )}

              {activeTab === 'deliverables' && (
                <ProjectCompletion
                  project={selectedProject}
                />
              )}

              {activeTab === 'settings' && (
                <IntegrationsModal
                  switchStatus={switchStatus}
                  discordStatus={discordStatus}
                  onRefresh={loadData}
                />
              )}
            </>
          )}
        </main>

        {/* Global Footer */}
        <footer className="border-t border-slate-900/80 glass-panel py-6 px-4 text-center text-xs text-slate-500 font-mono">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block"></span>
              <span>IdeaFlow AI • Flip the Switch Hackathon 2026 (Track 02)</span>
            </div>
            <div>
              <span>Powered by SandboxAQ Switch Open-Source Agent Protocol & Discord</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
