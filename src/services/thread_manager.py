import threading
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


class ThreadManager:
    """
    Tkinter-safe background task runner.
    
    Runs heavy work on a daemon thread and uses root.after() to
    safely deliver results/errors back to the UI thread.
    
    Usage:
        tm = ThreadManager(root)
        tm.run_in_background(
            task=lambda: expensive_calculation(),
            on_success=lambda result: update_ui(result),
            on_error=lambda e: show_error(e),
            on_start=lambda: show_spinner()
        )
    """

    def __init__(self, root):
        self.root = root

    def run_in_background(
        self,
        task: Callable[[], Any],
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_start: Optional[Callable[[], None]] = None,
    ):
        """
        Execute `task` on a background thread.
        Callbacks (on_success, on_error, on_start) run on the main/UI thread.
        """
        # Fire on_start on the UI thread immediately
        if on_start:
            on_start()

        def _worker():
            try:
                result = task()
                # Schedule success callback on the UI thread
                if on_success:
                    self.root.after(0, lambda: on_success(result))
            except Exception as e:
                logger.error(f"Background task failed: {e}", exc_info=True)
                if on_error:
                    self.root.after(0, lambda: on_error(e))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread
