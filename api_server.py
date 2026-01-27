"""
FastAPI Server for Church Media Automation System
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from controller.event_manager import EventManager
from controller.workflow_controller import WorkflowController
from utils.dependency_manager import DependencyManager

app = FastAPI(
    title="Church Media Automation System",
    description="API for automated church media processing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
event_manager = EventManager()
workflow_controller = WorkflowController()
dependency_manager = DependencyManager()


# Pydantic models
class EventCreate(BaseModel):
    title: str
    speaker: str
    series: Optional[str] = None
    scripture: Optional[str] = None
    language: str = "auto"
    modules: Optional[Dict[str, Any]] = None


class VideoAttach(BaseModel):
    video_path: str


class WorkflowRun(BaseModel):
    force: bool = False


@app.get('/api/status')
async def get_status():
    """Get system status"""
    deps = dependency_manager.check_all()
    return {
        'status': 'ok',
        'dependencies': deps
    }


@app.get('/api/events')
async def list_events():
    """List all events"""
    event_ids = event_manager.list_events()
    events = []
    
    for event_id in event_ids:
        event = event_manager.load_event(event_id)
        if event:
            # Add status field (check workflow state)
            state = workflow_controller.state_store.get_workflow_state(event_id)
            event['status'] = state['overall_status'] if state else 'pending'
            events.append(event)
    
    return events


@app.get('/api/events/{event_id}')
async def get_event(event_id: str):
    """Get specific event"""
    event = event_manager.load_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    
    # Add workflow state
    state = workflow_controller.state_store.get_workflow_state(event_id)
    event['workflow_state'] = state
    
    return event


@app.post('/api/events', status_code=status.HTTP_201_CREATED)
async def create_event(event_data: EventCreate):
    """Create new event"""
    try:
        event_id = event_manager.create_event(
            title=event_data.title,
            speaker=event_data.speaker,
            series=event_data.series,
            scripture=event_data.scripture,
            language=event_data.language,
            modules=event_data.modules
        )
        
        event = event_manager.load_event(event_id)
        return event
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/api/events/{event_id}/run')
async def run_event_workflow(event_id: str, workflow_data: Optional[WorkflowRun] = None):
    """Run workflow for event"""
    force = workflow_data.force if workflow_data else False
    
    try:
        results = workflow_controller.run_event(event_id, force=force)
        return results
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/api/events/{event_id}/attach')
async def attach_video(event_id: str, video_data: VideoAttach):
    """Attach video to event"""
    success = event_manager.add_video_input(event_id, video_data.video_path)
    if success:
        return {'message': 'Video attached successfully'}
    else:
        raise HTTPException(status_code=400, detail='Failed to attach video')


@app.get('/api/dependencies')
async def check_dependencies():
    """Check all dependencies"""
    results = dependency_manager.check_all()
    return results


@app.post('/api/dependencies/{dep_key}/install')
async def install_dependency(dep_key: str):
    """Install a dependency"""
    try:
        success = dependency_manager.install_dependency(dep_key, auto_confirm=True)
        if success:
            return {'message': f'{dep_key} installed successfully'}
        else:
            raise HTTPException(status_code=400, detail='Installation failed')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/dependencies/{dep_key}')
async def check_dependency(dep_key: str):
    """Check specific dependency"""
    is_installed, version = dependency_manager.check_dependency(dep_key)
    
    dep_info = dependency_manager.DEPENDENCIES.get(dep_key)
    if not dep_info:
        raise HTTPException(status_code=404, detail='Unknown dependency')
    
    return {
        'name': dep_info['name'],
        'description': dep_info['description'],
        'required': dep_info['required'],
        'installed': is_installed,
        'version': version
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
