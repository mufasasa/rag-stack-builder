#!/usr/bin/env bash
# Ensure the library database is up in every session (containers recycle).
service postgresql start >/dev/null 2>&1 || true
