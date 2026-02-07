#!/usr/bin/env python3
"""
📋 Planning Tools - Project & Task Planning
Break down complex tasks, create plans, track progress
"""

from typing import List, Dict
from datetime import datetime
import json


class PlanningEngine:
    """Advanced planning and task management"""
    
    def __init__(self):
        self.plans = {}
        print("📋 Planning Engine initialized")
    
    def create_plan(self, goal: str, complexity: str = 'medium') -> Dict:
        """Create a project plan"""
        plan_id = f"plan_{len(self.plans) + 1}"
        
        # Break down into phases
        phases = self._identify_phases(goal, complexity)
        
        # Break phases into tasks
        tasks = []
        for phase in phases:
            phase_tasks = self._break_into_tasks(phase, complexity)
            tasks.extend(phase_tasks)
        
        plan = {
            'plan_id': plan_id,
            'goal': goal,
            'complexity': complexity,
            'created_at': datetime.now().isoformat(),
            'phases': phases,
            'tasks': tasks,
            'progress': 0
        }
        
        self.plans[plan_id] = plan
        return plan
    
    def _identify_phases(self, goal: str, complexity: str) -> List[str]:
        """Identify project phases"""
        if complexity == 'simple':
            return ['Research', 'Implementation', 'Testing']
        elif complexity == 'medium':
            return ['Research', 'Design', 'Implementation', 'Testing', 'Documentation']
        else:  # complex
            return ['Research', 'Analysis', 'Design', 'Architecture', 'Implementation', 
                   'Testing', 'Optimization', 'Documentation', 'Deployment']
    
    def _break_into_tasks(self, phase: str, complexity: str) -> List[Dict]:
        """Break phase into tasks"""
        task_count = {'simple': 2, 'medium': 3, 'complex': 5}[complexity]
        
        tasks = []
        for i in range(task_count):
            tasks.append({
                'phase': phase,
                'task': f"{phase} task {i+1}",
                'status': 'pending',
                'priority': 'normal'
            })
        
        return tasks
    
    def get_plan(self, plan_id: str) -> Dict:
        """Get a specific plan"""
        return self.plans.get(plan_id, {})
    
    def update_task_status(self, plan_id: str, task_index: int, status: str):
        """Update task status"""
        if plan_id in self.plans:
            self.plans[plan_id]['tasks'][task_index]['status'] = status
            
            # Update progress
            completed = sum(1 for t in self.plans[plan_id]['tasks'] if t['status'] == 'completed')
            total = len(self.plans[plan_id]['tasks'])
            self.plans[plan_id]['progress'] = int((completed / total) * 100)
        
        return self.plans[plan_id]


def create_project_plan(goal: str, complexity: str = 'medium'):
    """Tool: Create a project plan"""
    engine = PlanningEngine()
    plan = engine.create_plan(goal, complexity)
    
    return {
        'success': True,
        'plan': plan,
        'message': f'Created plan with {len(plan["phases"])} phases and {len(plan["tasks"])} tasks'
    }


def break_down_task(task: str):
    """Tool: Break down a complex task"""
    subtasks = [
        f"1. Research {task}",
        f"2. Plan approach for {task}",
        f"3. Implement {task}",
        f"4. Test {task}",
        f"5. Document {task}"
    ]
    
    return {
        'success': True,
        'task': task,
        'subtasks': subtasks,
        'count': len(subtasks),
        'message': f'Broke down "{task}" into {len(subtasks)} subtasks'
    }
