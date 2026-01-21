from __future__ import annotations

from pathlib import Path
import sys
import types

# Ensure the sources/ directory is on sys.path for unit tests.
ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
if str(SOURCES) not in sys.path:
    sys.path.insert(0, str(SOURCES))

# Provide a minimal pygame stub for environments without pygame installed.
if "pygame" not in sys.modules:
    pygame_stub = types.SimpleNamespace()
    pygame_stub.image = types.SimpleNamespace(load=lambda *args, **kwargs: None)
    pygame_stub.font = types.SimpleNamespace(
        Font=lambda *args, **kwargs: None, SysFont=lambda *args, **kwargs: None
    )
    pygame_stub.mixer = types.SimpleNamespace(Sound=lambda *args, **kwargs: None)
    pygame_stub.Surface = type("Surface", (), {})
    pygame_stub.K_SPACE = 32
    pygame_stub.K_RETURN = 13
    pygame_stub.K_ESCAPE = 27
    pygame_stub.K_LSHIFT = 304
    pygame_stub.K_RSHIFT = 303
    pygame_stub.K_LCTRL = 306
    pygame_stub.K_RCTRL = 305
    pygame_stub.K_LALT = 308
    pygame_stub.K_RALT = 307
    pygame_stub.K_UP = 273
    pygame_stub.K_DOWN = 274
    pygame_stub.K_LEFT = 276
    pygame_stub.K_RIGHT = 275
    pygame_stub.K_TAB = 9
    pygame_stub.K_BACKSPACE = 8
    pygame_stub.K_DELETE = 127
    pygame_stub.K_HOME = 278
    pygame_stub.K_END = 279
    pygame_stub.K_PAGEUP = 280
    pygame_stub.K_PAGEDOWN = 281
    pygame_stub.K_PLUS = 43
    pygame_stub.K_MINUS = 45
    pygame_stub.K_EQUALS = 61
    pygame_stub.MOUSEWHEEL = 1027
    sys.modules["pygame"] = pygame_stub
