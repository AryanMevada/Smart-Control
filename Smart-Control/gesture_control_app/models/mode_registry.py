from mouse.mouse_controller import run_mouse
from keyboard.keyboard_controller import run_keyboard
from media_controller.media_controller import run_media
from volume.volume_controller import run_volume
from presentation.presentation_controller import run_presentation


MODE_REGISTRY = {
    "Mouse": run_mouse,
    "Keyboard": run_keyboard,
    "Media": run_media,
    "Volume": run_volume,
    "Presentation": run_presentation
}