#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    try:
        from django.core.management import execute_from_command_line
        from django.conf import settings

        if settings.DEBUG and settings.USE_VSCODE_DEBUGGER:
            import ptvsd
            ptvsd.enable_attach('debugger-local-secret',
                                address=('0.0.0.0', 8010))
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)
