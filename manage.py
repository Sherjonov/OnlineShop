#!/usr/bin/env python
"""Django'ning buyruq qatori utiliti — administrativ vazifalar uchun."""
import os
import sys


def main() -> None:
    """manage.py kirish nuqtasi."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django import qilib bo'lmadi. U o'rnatilganmi va "
            "PYTHONPATH muhit o'zgaruvchisida mavjudmi? "
            "Virtual environment-ni faollashtirishni unutmang."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
