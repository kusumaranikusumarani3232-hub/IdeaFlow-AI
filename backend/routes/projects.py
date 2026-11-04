from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import json
from backend.database import (
    get_db,
    Project,
    Task,
    Decision,
    CreativeDraft,
    ChatMessage
)
from backend.models import (
    ProjectCreate,
    ProjectUpdate,
    TaskCreate,
    TaskUpdate,
    DecisionCreate,
    DraftCreate,
    DraftUpdate,
    ChatMessageCreate
)

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.get("")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return [p.to_dict() for p in projects]

@router.post("")
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        title=data.title,
        concept=data.concept,
        category=data.category or "video",
        target_audience=data.target_audience,
        visual_identity=data.visual_identity,
        discord_channel_id=data.discord_channel_id,
        switch_room_id=data.switch_room_id or "room_discord_nature_channel"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project.to_dict()

@router.get("/{project_id}")
def get_project_details(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    tasks = [t.to_dict() for t in project.tasks]
    decisions = [d.to_dict() for d in project.decisions]
    drafts = [dr.to_dict() for dr in project.drafts]
    messages = [m.to_dict() for m in project.messages]

    data = project.to_dict()
    data["tasks"] = tasks
    data["decisions"] = decisions
    data["drafts"] = drafts
    data["messages"] = messages
    return data

@router.patch("/{project_id}")
def update_project(project_id: str, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if data.title is not None:
        project.title = data.title
    if data.concept is not None:
        project.concept = data.concept
    if data.category is not None:
        project.category = data.category
    if data.status is not None:
        project.status = data.status
    if data.progress is not None:
        project.progress = data.progress
    if data.target_audience is not None:
        project.target_audience = data.target_audience
    if data.visual_identity is not None:
        project.visual_identity = data.visual_identity
    if data.summary is not None:
        project.summary = data.summary
    if data.content_roadmap is not None:
        project.content_roadmap = json.dumps(data.content_roadmap)

    project.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project)
    return project.to_dict()

@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"status": "deleted", "id": project_id}

# --- Tasks ---
@router.get("/{project_id}/tasks")
def list_tasks(project_id: str, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return [t.to_dict() for t in tasks]

@router.post("/{project_id}/tasks")
def create_task(project_id: str, data: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        project_id=project_id,
        title=data.title,
        description=data.description,
        status=data.status or "todo",
        priority=data.priority or "medium",
        category=data.category or "pre-production",
        assigned_to=data.assigned_to or "IdeaFlow Agent",
        due_date=data.due_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task.to_dict()

@router.patch("/tasks/{task_id}")
def update_task(task_id: str, data: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status
        if data.status == "done":
            task.completed_at = datetime.now(timezone.utc)
    if data.priority is not None:
        task.priority = data.priority
    if data.category is not None:
        task.category = data.category
    if data.assigned_to is not None:
        task.assigned_to = data.assigned_to
    if data.due_date is not None:
        task.due_date = data.due_date

    db.commit()
    db.refresh(task)
    return task.to_dict()

# --- Decisions ---
@router.post("/{project_id}/decisions")
def create_decision(project_id: str, data: DecisionCreate, db: Session = Depends(get_db)):
    decision = Decision(
        project_id=project_id,
        title=data.title,
        decision=data.decision,
        rationale=data.rationale,
        category=data.category or "Identity",
        decided_by=data.decided_by or "Consensus"
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision.to_dict()

# --- Creative Drafts ---
@router.post("/{project_id}/drafts")
def create_draft(project_id: str, data: DraftCreate, db: Session = Depends(get_db)):
    draft = CreativeDraft(
        project_id=project_id,
        title=data.title,
        draft_type=data.draft_type or "script",
        content=data.content,
        version=data.version or 1
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft.to_dict()

@router.patch("/drafts/{draft_id}")
def update_draft(draft_id: str, data: DraftUpdate, db: Session = Depends(get_db)):
    draft = db.query(CreativeDraft).filter(CreativeDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if data.title is not None:
        draft.title = data.title
    if data.draft_type is not None:
        draft.draft_type = data.draft_type
    if data.content is not None:
        draft.content = data.content
    if data.version is not None:
        draft.version = data.version

    draft.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(draft)
    return draft.to_dict()

# --- Chat Messages ---
@router.post("/{project_id}/messages")
def send_project_message(project_id: str, data: ChatMessageCreate, db: Session = Depends(get_db)):
    msg = ChatMessage(
        project_id=project_id,
        sender_type="human",
        sender_name=data.sender_name or "Alex (Creator)",
        content=data.content,
        platform=data.platform or "web",
        discord_thread_id=data.discord_thread_id
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg.to_dict()

# --- Project Completion Deliverables ---
@router.get("/{project_id}/summary")
def get_project_summary(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks_total = len(project.tasks)
    tasks_done = len([t for t in project.tasks if t.status == "done"])
    
    return {
        "project_id": project.id,
        "title": project.title,
        "concept": project.concept,
        "status": project.status,
        "progress_percentage": project.progress,
        "metrics": {
            "total_tasks": tasks_total,
            "completed_tasks": tasks_done,
            "completion_ratio": f"{tasks_done}/{tasks_total}" if tasks_total else "0/0",
            "strategic_decisions": len(project.decisions),
            "creative_deliverables": len(project.drafts),
            "collaboration_messages": len(project.messages)
        },
        "target_audience": project.target_audience,
        "visual_identity": project.visual_identity,
        "key_decisions": [d.to_dict() for d in project.decisions],
        "deliverables": [dr.to_dict() for dr in project.drafts],
        "export_ready": True
    }

