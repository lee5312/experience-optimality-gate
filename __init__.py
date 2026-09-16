"""Hermes native plugin entrypoint; implementation stays in the thin adapter."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_spec = spec_from_file_location("paralloff_eog_hermes", Path(__file__).parent / "adapters" / "hermes.py")
if _spec is None or _spec.loader is None:
    raise ImportError("EOG Hermes adapter unavailable")
_adapter = module_from_spec(_spec)
_spec.loader.exec_module(_adapter)
register = _adapter.register
