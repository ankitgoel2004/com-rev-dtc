from .dashboard import show as show_dashboard
from .metrics import show as show_metrics
from .ratings import show as show_ratings

# Explicitly expose the page functions
__all__ = ['show_dashboard', 'show_metrics', 'show_ratings']