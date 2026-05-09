import time
from unittest.mock import MagicMock

import pytest

from src.video_downloader.queue_manager import (
    DownloadQueueManager,
    DownloadStatus,
    DownloadTask,
)


def _wait_for(predicate, timeout=2.0, interval=0.02):
    """Poll until predicate() is true or timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


class TestAddDownload:
    def test_returns_task_id(self):
        mgr = DownloadQueueManager(download_function=lambda url, **kw: None, max_workers=1)
        task_id = mgr.add_download("https://example.com/v", {})
        assert isinstance(task_id, str) and len(task_id) > 0
        mgr.is_running = False  # let workers exit

    def test_task_present_in_active_tasks(self):
        mgr = DownloadQueueManager(download_function=lambda url, **kw: None, max_workers=1)
        task_id = mgr.add_download("https://example.com/v", {"foo": "bar"})
        task = mgr.get_task_status(task_id)
        assert isinstance(task, DownloadTask)
        assert task.url == "https://example.com/v"
        assert task.options == {"foo": "bar"}
        mgr.is_running = False

    def test_starts_processing_on_first_add(self):
        mgr = DownloadQueueManager(download_function=lambda url, **kw: None, max_workers=1)
        assert mgr.is_running is False
        mgr.add_download("https://example.com/v", {})
        assert mgr.is_running is True
        mgr.is_running = False


class TestProcessing:
    def test_completes_a_successful_task(self):
        download = MagicMock()
        completed = []
        mgr = DownloadQueueManager(download_function=download, max_workers=1)
        mgr.on_task_completed = lambda t: completed.append(t)
        mgr.add_download("https://example.com/v", {})
        assert _wait_for(lambda: len(completed) == 1)
        assert completed[0].status == DownloadStatus.COMPLETED
        assert completed[0].progress == 100.0
        download.assert_called_once()
        mgr.is_running = False

    def test_marks_failed_when_download_raises(self):
        def boom(url, **kw):
            raise RuntimeError("network down")

        failed = []
        mgr = DownloadQueueManager(download_function=boom, max_workers=1)
        mgr.on_task_failed = lambda t: failed.append(t)
        mgr.add_download("https://example.com/v", {})
        assert _wait_for(lambda: len(failed) == 1)
        assert failed[0].status == DownloadStatus.FAILED
        assert "network down" in failed[0].error_message
        mgr.is_running = False

    def test_skips_cancelled_task(self):
        download = MagicMock()
        completed = []
        mgr = DownloadQueueManager(download_function=download, max_workers=1)
        mgr.on_task_completed = lambda t: completed.append(t)
        task_id = mgr.add_download("https://example.com/v", {})
        # Immediately cancel before worker picks it up; tight race but the
        # worker uses a 1s timeout per dequeue so we have a window.
        cancelled = mgr.remove_download(task_id)
        # If we cancelled in time, the task never completes
        if cancelled:
            time.sleep(0.3)
            assert completed == []
        mgr.is_running = False


class TestRemoveDownload:
    def test_returns_false_for_unknown_id(self):
        mgr = DownloadQueueManager(download_function=lambda url, **kw: None)
        assert mgr.remove_download("does-not-exist") is False

    def test_cancels_pending_task(self):
        # Use a download function that blocks so we can cancel before it runs
        block = MagicMock()
        mgr = DownloadQueueManager(download_function=block, max_workers=0)  # no workers
        task_id = mgr.add_download("https://example.com/v", {})
        # max_workers=0 means no workers were started, but is_running was set true
        result = mgr.remove_download(task_id)
        assert result is True
        assert mgr.get_task_status(task_id).status == DownloadStatus.CANCELLED
        mgr.is_running = False


class TestQueueInfo:
    def test_empty_queue(self):
        mgr = DownloadQueueManager(download_function=lambda url, **kw: None)
        info = mgr.get_queue_info()
        assert info == {
            "pending": 0,
            "downloading": 0,
            "completed": 0,
            "failed": 0,
            "total": 0,
            "is_processing": False,
        }

    def test_after_adding_pending_task(self):
        mgr = DownloadQueueManager(download_function=lambda url, **kw: None, max_workers=0)
        mgr.add_download("https://example.com/v", {})
        info = mgr.get_queue_info()
        assert info["total"] == 1
        assert info["pending"] == 1
        assert info["is_processing"] is True
        mgr.is_running = False


class TestClearCompleted:
    def test_moves_completed_into_completed_list(self):
        mgr = DownloadQueueManager(download_function=lambda url, **kw: None, max_workers=1)
        mgr.add_download("https://example.com/v", {})
        assert _wait_for(
            lambda: any(
                t.status == DownloadStatus.COMPLETED for t in mgr.active_tasks.values()
            )
        )
        mgr.clear_completed()
        assert mgr.active_tasks == {}
        assert any(t.status == DownloadStatus.COMPLETED for t in mgr.completed_tasks)
        mgr.is_running = False


class TestCallbacks:
    def test_on_task_started_invoked_before_completion(self):
        events = []
        mgr = DownloadQueueManager(download_function=lambda url, **kw: None, max_workers=1)
        mgr.on_task_started = lambda t: events.append(("started", t.id))
        mgr.on_task_completed = lambda t: events.append(("completed", t.id))
        mgr.add_download("https://example.com/v", {})
        assert _wait_for(lambda: len(events) == 2)
        assert events[0][0] == "started"
        assert events[1][0] == "completed"
        assert events[0][1] == events[1][1]
        mgr.is_running = False
