# src/video_downloader/queue_manager.py
import threading
from queue import Queue
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any
from enum import Enum
import uuid


class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadTask:
    """Represents a single download task in the queue."""
    id: str
    url: str
    options: Dict[str, Any]
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    error_message: Optional[str] = None
    result_path: Optional[str] = None


class DownloadQueueManager:
    """Manages a queue of download tasks and processes them with multiple worker threads."""
    
    def __init__(self, download_function: Callable, max_workers: int = 3):
        self.download_function = download_function
        self.task_queue = Queue()
        self.active_tasks = {}  # id -> DownloadTask
        self.completed_tasks = []
        self.is_running = False
        self.worker_threads = []
        self.max_workers = max_workers
        self.lock = threading.Lock()
        
        # Callbacks
        self.on_task_started = None
        self.on_task_progress = None
        self.on_task_completed = None
        self.on_task_failed = None
        self.on_queue_empty = None
    
    def add_download(self, url: str, options: Dict[str, Any]) -> str:
        """Add a download task to the queue. Returns task ID."""
        print(f"DEBUG: add_download() called with URL='{url}', options={options}")
        
        task_id = str(uuid.uuid4())
        task = DownloadTask(id=task_id, url=url, options=options.copy())
        print(f"DEBUG: Created task with ID={task_id}")
        
        with self.lock:
            self.active_tasks[task_id] = task
            self.task_queue.put(task)
            print(f"DEBUG: Added task to queue, total tasks: {len(self.active_tasks)}")
        
        # Start processing if not already running
        if not self.is_running:
            print("DEBUG: Starting queue processing...")
            self.start_processing()
        else:
            print("DEBUG: Queue already running")
            
        print(f"DEBUG: add_download() completed, returning task_id={task_id}")
        return task_id
    
    def remove_download(self, task_id: str) -> bool:
        """Remove a pending download from the queue."""
        with self.lock:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                if task.status == DownloadStatus.PENDING:
                    task.status = DownloadStatus.CANCELLED
                    return True
        return False
    
    def get_task_status(self, task_id: str) -> Optional[DownloadTask]:
        """Get the current status of a task."""
        with self.lock:
            return self.active_tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, DownloadTask]:
        """Get all active and completed tasks."""
        with self.lock:
            return self.active_tasks.copy()
    
    def get_queue_info(self) -> Dict[str, Any]:
        """Get information about the current queue state."""
        with self.lock:
            pending_count = sum(1 for task in self.active_tasks.values() 
                              if task.status == DownloadStatus.PENDING)
            downloading_count = sum(1 for task in self.active_tasks.values() 
                                  if task.status == DownloadStatus.DOWNLOADING)
            completed_count = sum(1 for task in self.active_tasks.values() 
                                if task.status == DownloadStatus.COMPLETED)
            failed_count = sum(1 for task in self.active_tasks.values() 
                             if task.status == DownloadStatus.FAILED)
            
            return {
                "pending": pending_count,
                "downloading": downloading_count,
                "completed": completed_count,
                "failed": failed_count,
                "total": len(self.active_tasks),
                "is_processing": self.is_running
            }
    
    def start_processing(self):
        """Start processing the download queue with multiple worker threads."""
        print("DEBUG: start_processing() called")
        
        if self.is_running:
            print("DEBUG: Already running, returning")
            return
            
        print("DEBUG: Setting is_running=True")
        self.is_running = True
        
        # Create and start worker threads
        print(f"DEBUG: Creating {self.max_workers} worker threads")
        for i in range(self.max_workers):
            worker_thread = threading.Thread(
                target=self._process_queue, 
                daemon=True,
                name=f"DownloadWorker-{i+1}"
            )
            worker_thread.start()
            self.worker_threads.append(worker_thread)
            print(f"DEBUG: Started worker thread {i+1}")
        
        print("DEBUG: start_processing() completed")
    
    def stop_processing(self):
        """Stop processing the download queue."""
        self.is_running = False
        
        # Wait for all worker threads to finish
        for worker_thread in self.worker_threads:
            worker_thread.join()
        self.worker_threads.clear()
    
    def clear_completed(self):
        """Remove all completed and failed tasks from memory."""
        with self.lock:
            to_remove = [task_id for task_id, task in self.active_tasks.items() 
                        if task.status in [DownloadStatus.COMPLETED, DownloadStatus.FAILED, DownloadStatus.CANCELLED]]
            for task_id in to_remove:
                self.completed_tasks.append(self.active_tasks.pop(task_id))
    
    def _process_queue(self):
        """Main worker thread function that processes download tasks."""
        print(f"DEBUG: Worker thread {threading.current_thread().name} started")
        
        while self.is_running:
            try:
                print(f"DEBUG: Worker {threading.current_thread().name} waiting for task...")
                # Get next task from queue (blocks if queue is empty)
                task = self.task_queue.get(timeout=1.0)
                print(f"DEBUG: Worker {threading.current_thread().name} got task {task.id}")
                
                # Skip cancelled tasks
                if task.status == DownloadStatus.CANCELLED:
                    print(f"DEBUG: Task {task.id} was cancelled, skipping")
                    self.task_queue.task_done()
                    continue
                
                # Update task status
                with self.lock:
                    task.status = DownloadStatus.DOWNLOADING
                print(f"DEBUG: Task {task.id} status set to DOWNLOADING")
                
                # Notify task started
                if self.on_task_started:
                    print(f"DEBUG: Calling on_task_started for task {task.id}")
                    self.on_task_started(task)
                
                # Set up progress hook for this task
                def progress_hook(data):
                    if data.get("status") == "downloading":
                        total_bytes = data.get("total_bytes") or data.get("total_bytes_estimate", 0)
                        if total_bytes > 0:
                            task.progress = (data["downloaded_bytes"] / total_bytes) * 100
                            if self.on_task_progress:
                                self.on_task_progress(task)
                
                # Add progress hook to options
                options = task.options.copy()
                existing_hooks = options.get("progress_hooks", [])
                options["progress_hooks"] = existing_hooks + [progress_hook]
                
                try:
                    print(f"DEBUG: Worker {threading.current_thread().name} calling download_function for task {task.id}")
                    # Execute the download
                    self.download_function(task.url, **options)
                    print(f"DEBUG: Worker {threading.current_thread().name} download completed for task {task.id}")
                    
                    # Mark as completed
                    with self.lock:
                        task.status = DownloadStatus.COMPLETED
                        task.progress = 100.0
                    
                    if self.on_task_completed:
                        print(f"DEBUG: Calling on_task_completed for task {task.id}")
                        self.on_task_completed(task)
                        
                except Exception as e:
                    print(f"DEBUG: Worker {threading.current_thread().name} download failed for task {task.id}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Mark as failed
                    with self.lock:
                        task.status = DownloadStatus.FAILED
                        task.error_message = str(e)
                    
                    if self.on_task_failed:
                        print(f"DEBUG: Calling on_task_failed for task {task.id}")
                        self.on_task_failed(task)
                
                finally:
                    # Mark task as done
                    print(f"DEBUG: Worker {threading.current_thread().name} marking task {task.id} as done")
                    self.task_queue.task_done()
                        
            except Exception as e:
                print(f"DEBUG: Worker {threading.current_thread().name} exception in main loop: {e}")
                # Timeout or other error - continue processing
                continue
        
        print(f"DEBUG: Worker thread {threading.current_thread().name} exiting")
        
        # Notify queue is empty
        if self.on_queue_empty:
            print("DEBUG: Calling on_queue_empty")
            self.on_queue_empty()
