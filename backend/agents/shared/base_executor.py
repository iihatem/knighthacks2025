"""Base Agent Executor for all specialist agents"""
import logging
from typing import Any, Dict
from abc import ABC, abstractmethod

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_agent_text_message, new_task, new_text_artifact

logger = logging.getLogger(__name__)


class BaseAgentExecutor(AgentExecutor, ABC):
    """Base class for all legal AI agent executors"""
    
    def __init__(self, agent_name: str):
        super().__init__()
        self.agent_name = agent_name
        logger.info(f"Initializing {agent_name} executor")
    
    @abstractmethod
    async def process_task(self, query: str, case_id: str, session_id: str) -> Dict[str, Any]:
        """
        Process the task and return a response.
        
        Args:
            query: User's query/request
            case_id: The case ID
            session_id: Session ID for context
        
        Returns:
            Dict with:
                - is_task_complete: bool
                - require_user_input: bool
                - content: str (the response text)
                - metadata: dict (optional additional data)
        """
        pass
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute the agent task using A2A protocol"""
        query = context.get_user_input()
        task = context.current_task
        
        if not context.message:
            raise Exception('No message provided')
        
        # Extract case_id from context metadata if available
        case_id = context.message.metadata.get('case_id', 'unknown') if context.message.metadata else 'unknown'
        
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        
        session_id = task.context_id
        
        try:
            # Process the task using the specialist agent
            result = await self.process_task(query, case_id, session_id)
            
            if result['is_task_complete']:
                # Task completed successfully
                await event_queue.enqueue_event(
                    TaskArtifactUpdateEvent(
                        append=False,
                        context_id=task.context_id,
                        task_id=task.id,
                        last_chunk=True,
                        artifact=new_text_artifact(
                            name='agent_response',
                            description=f'Response from {self.agent_name}',
                            text=result['content'],
                        ),
                    )
                )
                
                # Add metadata as additional artifact if present
                if result.get('metadata'):
                    await event_queue.enqueue_event(
                        TaskArtifactUpdateEvent(
                            append=False,
                            context_id=task.context_id,
                            task_id=task.id,
                            last_chunk=False,
                            artifact={
                                'artifactId': f'{task.id}_metadata',
                                'name': 'metadata',
                                'parts': [
                                    {
                                        'type': 'data',
                                        'data': result['metadata']
                                    }
                                ]
                            },
                        )
                    )
                
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(state=TaskState.completed),
                        final=True,
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )
            elif result['require_user_input']:
                # Task needs user input (e.g., approval)
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.input_required,
                            message=new_agent_text_message(
                                result['content'],
                                task.context_id,
                                task.id,
                            ),
                        ),
                        final=True,
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )
            else:
                # Task is still working
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.working,
                            message=new_agent_text_message(
                                result['content'],
                                task.context_id,
                                task.id,
                            ),
                        ),
                        final=False,
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )
        
        except Exception as e:
            logger.error(f"Error in {self.agent_name} executor: {e}", exc_info=True)
            # Send error as completed task with error message
            await event_queue.enqueue_event(
                TaskArtifactUpdateEvent(
                    append=False,
                    context_id=task.context_id,
                    task_id=task.id,
                    last_chunk=True,
                    artifact=new_text_artifact(
                        name='error_response',
                        description=f'Error from {self.agent_name}',
                        text=f'An error occurred: {str(e)}',
                    ),
                )
            )
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    status=TaskStatus(state=TaskState.completed),
                    final=True,
                    context_id=task.context_id,
                    task_id=task.id,
                )
            )
    
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel the task"""
        logger.info(f"Cancelling task in {self.agent_name}")
        raise Exception('cancel not supported')

