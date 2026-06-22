#!/usr/bin/env bash
set -euo pipefail

.venv/bin/python manage.py test hospital.tests.e2e
