import React, { useState } from 'react';
import {
  Sparkles,
  CheckCircle2,
  Clock,
  Send,
  Plus,
  FileText,
  Share2,
  Copy,
  Check,
  Compass,
  ListTodo,
  Layers,
  MessageSquare,
  HelpCircle,
  Tag,
  Radio
} from 'lucide-react';
import { updateTaskStatus, createTask, createDecision, createDraft, sendChatMessage } from '../api';

export default function ProjectWorkspace({
  project,
  onRefreshProject,
  onTriggerSimulation
}) {
  const [subTab, setSubTab] = useState('roadmap'); // roadmap | tasks | drafts | decisions | chat
  const [chatInput, setChatInput] = useState('');
  const [chatSending, setChatSending] = useState(false);
  const [copiedDraftId, setCopiedDraftId] = useState(null);

  // New item modal states
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskCategory, setNewTaskCategory] = useState('pre-production');
  const [newTaskPriority, setNewTaskPriority] = useState('medium');
  const [newTaskAssignee, setNewTaskAssignee] = useState('IdeaFlow Agent');

  const [showDecisionModal, setShowDecisionModal] = useState(false);
  const [newDecisionTitle, setNewDecisionTitle] = useState('');
  const [newDecisionText, setNewDecisionText] = useState('');
  const [newDecisionRationale, setNewDecisionRationale] = useState('');
  const [newDecisionCategory, setNewDecisionCategory] = useState('Identity');

  if (!project) {
    return (
      <div className="glass-panel p-12 rounded-2xl text-center space-y-3">
        <Sparkles className="w-8 h-8 text-slate-500 mx-auto" />
        <h3 className="text-lg font-bold text-white">No Project Selected</h3>
        <p className="text-xs text-slate-400">Select or create a creative project from the dashboard.</p>
      </div>
    );
  }

  const handleTaskToggle = async (taskId, currentStatus) => {
    const nextStatus = currentStatus === 'done' ? 'todo' : currentStatus === 'todo' ? 'in_progress' : 'done';
    try {
      await updateTaskStatus(taskId, nextStatus);
      onRefreshProject();
    } catch (e) {
      console.error('Error toggling task:', e);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    try {
      await createTask(project.id, {
        project_id: project.id,
        title: newTaskTitle,
        category: newTaskCategory,
        priority: newTaskPriority,
        assigned_to: newTaskAssignee,
        status: 'todo'
      });
      setNewTaskTitle('');
      setShowTaskModal(false);
      onRefreshProject();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateDecision = async (e) => {
    e.preventDefault();
    if (!newDecisionTitle.trim() || !newDecisionText.trim()) return;
    try {
      await createDecision(project.id, {
        project_id: project.id,
        title: newDecisionTitle,
        decision: newDecisionText,
        rationale: newDecisionRationale,
        category: newDecisionCategory,
        decided_by: 'Consensus'
      });
      setNewDecisionTitle('');
      setNewDecisionText('');
      setNewDecisionRationale('');
      setShowDecisionModal(false);
      onRefreshProject();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const msg = chatInput;
    setChatInput('');
    setChatSending(true);
    try {
      // Dispatches via Switch simulation so it triggers the full protocol loop
      await onTriggerSimulation(msg);
      onRefreshProject();
    } finally {
      setChatSending(false);
    }
  };

  const handleCopyDraft = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedDraftId(id);
    setTimeout(() => setCopiedDraftId(null), 2000);
  };

  const tasks = project.tasks || [];
  const decisions = project.decisions || [];
  const drafts = project.drafts || [];
  const messages = project.messages || [];

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase font-semibold">
                {project.category}
              </span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Switch Room: {project.switch_room_id}
              </span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Discord: #creative-lounge
              </span>
            </div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">{project.title}</h1>
            <p className="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">{project.concept}</p>
          </div>

          <div className="flex items-center gap-3 self-start md:self-auto">
            <div className="text-right">
              <span className="text-[11px] font-mono text-slate-400 block">CREATIVE PROGRESS</span>
              <span className="text-xl font-bold text-emerald-400 font-mono">{project.progress}%</span>
            </div>
          </div>
        </div>

        {/* Sub-navigation Tabs */}
        <div className="flex items-center gap-2 border-t border-slate-800 pt-3 overflow-x-auto">
          {[
            { id: 'roadmap', label: 'Roadmap & Identity', icon: Compass, count: project.content_roadmap?.length },
            { id: 'tasks', label: 'Task Management', icon: ListTodo, count: tasks.length },
            { id: 'drafts', label: 'Creative Drafts', icon: FileText, count: drafts.length },
            { id: 'decisions', label: 'Shared Decisions', icon: Layers, count: decisions.length },
            { id: 'chat', label: 'Switch & Discord Feed', icon: MessageSquare, count: messages.length },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = subTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setSubTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium transition-all whitespace-nowrap ${
                  active
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${active ? 'text-emerald-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                    active ? 'bg-emerald-500/30 text-emerald-200' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab 1: Roadmap & Concept */}
      {subTab === 'roadmap' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Visual Identity & Aesthetic */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>Channel Identity & Visual Aesthetic</span>
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                {project.visual_identity || 'Cinematic natural aesthetic with earth-toned palettes, slow camera pans, and macro 4K clarity.'}
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[#1B4332] border border-slate-700 shadow-md"></div>
                  <div>
                    <span className="text-[11px] font-mono text-slate-400 block">PRIMARY</span>
                    <span className="text-xs font-semibold text-white">#1B4332 (Forest)</span>
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[#DDA15E] border border-slate-700 shadow-md"></div>
                  <div>
                    <span className="text-[11px] font-mono text-slate-400 block">SECONDARY</span>
                    <span className="text-xs font-semibold text-white">#DDA15E (Ochre)</span>
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[#E9ECEF] border border-slate-700 shadow-md"></div>
                  <div>
                    <span className="text-[11px] font-mono text-slate-400 block">ACCENT</span>
                    <span className="text-xs font-semibold text-white">#E9ECEF (Mist)</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Content Roadmap Timeline */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Compass className="w-4 h-4 text-cyan-400" />
                <span>Multi-Phase Content Roadmap</span>
              </h3>

              <div className="space-y-3">
                {(project.content_roadmap || []).map((step, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 flex items-start gap-4 hover:border-slate-700 transition-all"
                  >
                    <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-xs flex items-center justify-center shrink-0 mt-0.5">
                      0{idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white">{step.milestone || step}</span>
                        <span className="text-[11px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10">
                          {step.timeline || 'Phase ' + (idx + 1)}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400 block mt-1">Phase: {step.phase || 'Production'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Target Audience & Summary */}
          <div className="space-y-6">
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
              <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">Target Audience Profile</span>
              <p className="text-xs text-slate-200 leading-relaxed">
                {project.target_audience || 'Nature and wildlife lovers, slow-media documentary enthusiasts, outdoor creators aged 18-45 seeking mindful, immersive cinematography.'}
              </p>
            </div>

            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
              <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">Executive Summary</span>
              <p className="text-xs text-slate-200 leading-relaxed">
                {project.summary || 'A cinematic wildlife documentary channel built collaboratively between human vision and IdeaFlow AI agent.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Task Management */}
      {subTab === 'tasks' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Production Tasks</h3>
              <p className="text-xs text-slate-400">Collaborative task pipeline broken down by IdeaFlow Agent</p>
            </div>
            <button
              onClick={() => setShowTaskModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition-all"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Task</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tasks.map((task) => {
              const isDone = task.status === 'done';
              const isInProgress = task.status === 'in_progress';
              return (
                <div
                  key={task.id}
                  className={`p-4 rounded-xl border transition-all ${
                    isDone
                      ? 'bg-slate-900/30 border-slate-800/60 opacity-70'
                      : isInProgress
                      ? 'bg-slate-900/80 border-cyan-500/30 shadow-md shadow-cyan-500/5'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 uppercase">
                      {task.category}
                    </span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase ${
                      task.priority === 'high' ? 'bg-rose-500/10 text-rose-300' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {task.priority}
                    </span>
                  </div>

                  <h4 className={`text-xs font-bold mb-1 ${isDone ? 'line-through text-slate-400' : 'text-white'}`}>
                    {task.title}
                  </h4>
                  <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">{task.description}</p>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-[11px]">
                    <span className="text-slate-400 font-mono">Assigned: <strong className="text-slate-200">{task.assigned_to}</strong></span>
                    <button
                      onClick={() => handleTaskToggle(task.id, task.status)}
                      className={`px-2.5 py-1 rounded text-[11px] font-medium transition-all ${
                        isDone
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : 'bg-slate-800 text-slate-300 hover:bg-emerald-500/20 hover:text-emerald-300'
                      }`}
                    >
                      {isDone ? '✓ Completed' : isInProgress ? 'In Progress' : 'Mark Done'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 3: Creative Drafts */}
      {subTab === 'drafts' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Creative Drafts & Scripts</h3>
              <p className="text-xs text-slate-400">AI-generated pilot scripts, audio cues, and creative deliverables</p>
            </div>
          </div>

          <div className="space-y-4">
            {drafts.map((draft) => (
              <div key={draft.id} className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-emerald-400" />
                    <h4 className="text-sm font-bold text-white">{draft.title}</h4>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                      v{draft.version} • {draft.draft_type}
                    </span>
                  </div>
                  <button
                    onClick={() => handleCopyDraft(draft.id, draft.content)}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition-all"
                  >
                    {copiedDraftId === draft.id ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Copy Script</span>
                      </>
                    )}
                  </button>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {draft.content}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Shared Decisions */}
      {subTab === 'decisions' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Strategic Decisions Log</h3>
              <p className="text-xs text-slate-400">Consensus & strategic direction recorded by Human and IdeaFlow Agent</p>
            </div>
            <button
              onClick={() => setShowDecisionModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition-all"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Record Decision</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {decisions.map((dec) => (
              <div key={dec.id} className="glass-panel p-5 rounded-xl border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20 uppercase">
                    {dec.category}
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">By: {dec.decided_by}</span>
                </div>
                <h4 className="text-xs font-bold text-white">{dec.title}</h4>
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs text-slate-200">
                  <span className="text-emerald-400 font-semibold block mb-1">Decision:</span>
                  {dec.decision}
                </div>
                {dec.rationale && (
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    <strong className="text-slate-300">Rationale:</strong> {dec.rationale}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 5: Collaboration History (Discord & Switch Feed) */}
      {subTab === 'chat' && (
        <div className="glass-panel rounded-2xl border border-slate-800 p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-indigo-400" />
                <span>Switch Collaboration Stream</span>
              </h3>
              <p className="text-xs text-slate-400">Live human & agent messaging relayed through Switch</p>
            </div>
            <span className="text-[11px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10">
              Room: {project.switch_room_id}
            </span>
          </div>

          <div className="space-y-3 max-h-[480px] overflow-y-auto pr-2">
            {messages.map((m) => {
              const isAgent = m.sender_type === 'agent';
              return (
                <div
                  key={m.id}
                  className={`flex items-start gap-3 p-3.5 rounded-xl border ${
                    isAgent
                      ? 'bg-slate-900/90 border-emerald-500/20 ml-4'
                      : 'bg-slate-900/50 border-slate-800 mr-4'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                    isAgent ? 'bg-emerald-500 text-slate-950' : 'bg-indigo-600 text-white'
                  }`}>
                    {isAgent ? 'AI' : 'HU'}
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{m.sender_name}</span>
                      <span className="text-[10px] font-mono text-slate-500 uppercase">
                        {m.platform}
                      </span>
                    </div>
                    <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                      {m.content}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <form onSubmit={handleSendChat} className="flex gap-2 pt-2 border-t border-slate-800">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Message IdeaFlow Agent through Switch (or mention @IdeaFlow in Discord)..."
              className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
            <button
              type="submit"
              disabled={chatSending || !chatInput.trim()}
              className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{chatSending ? 'Sending...' : 'Send'}</span>
            </button>
          </form>
        </div>
      )}

      {/* Task Creation Modal */}
      {showTaskModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white">Create Production Task</h3>
            <form onSubmit={handleCreateTask} className="space-y-3">
              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">TASK TITLE</label>
                <input
                  type="text"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  placeholder="e.g. Color grade outdoor drone sequence"
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-mono text-slate-400 block mb-1">CATEGORY</label>
                  <select
                    value={newTaskCategory}
                    onChange={(e) => setNewTaskCategory(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  >
                    <option value="pre-production">Pre-Production</option>
                    <option value="production">Production</option>
                    <option value="post-production">Post-Production</option>
                    <option value="branding">Branding</option>
                    <option value="distribution">Distribution</option>
                  </select>
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-400 block mb-1">PRIORITY</label>
                  <select
                    value={newTaskPriority}
                    onChange={(e) => setNewTaskPriority(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  >
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowTaskModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold text-xs"
                >
                  Create Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Decision Modal */}
      {showDecisionModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white">Record Strategic Decision</h3>
            <form onSubmit={handleCreateDecision} className="space-y-3">
              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">DECISION TITLE</label>
                <input
                  type="text"
                  value={newDecisionTitle}
                  onChange={(e) => setNewDecisionTitle(e.target.value)}
                  placeholder="e.g. YouTube Title & Thumbnail Formula"
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  required
                />
              </div>
              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">THE DECISION</label>
                <textarea
                  value={newDecisionText}
                  onChange={(e) => setNewDecisionText(e.target.value)}
                  placeholder="What was decided?"
                  rows={2}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  required
                />
              </div>
              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">RATIONALE / CONTEXT</label>
                <textarea
                  value={newDecisionRationale}
                  onChange={(e) => setNewDecisionRationale(e.target.value)}
                  placeholder="Why was this chosen over alternatives?"
                  rows={2}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowDecisionModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold text-xs"
                >
                  Record Decision
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

