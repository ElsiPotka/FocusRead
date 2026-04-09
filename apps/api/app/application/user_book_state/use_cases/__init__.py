from app.application.user_book_state.use_cases.get_user_book_state import (
    GetUserBookState,
)
from app.application.user_book_state.use_cases.toggle_archive import ToggleArchive
from app.application.user_book_state.use_cases.toggle_completed import ToggleCompleted
from app.application.user_book_state.use_cases.toggle_favorite import ToggleFavorite
from app.application.user_book_state.use_cases.update_preferences import (
    PreferencesUpdate,
    UpdatePreferences,
)

__all__ = [
    "GetUserBookState",
    "PreferencesUpdate",
    "ToggleArchive",
    "ToggleCompleted",
    "ToggleFavorite",
    "UpdatePreferences",
]
