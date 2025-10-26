#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test if keyword matching works"""

msg = 'צור פרויקט Python חדש בשם myapp'
keywords = ['צור פרויקט', 'create project']

print("=" * 70)
print("Keyword Matching Test")
print("=" * 70)
print(f"Message: {msg}")
print(f"Message (lower): {msg.lower()}")
print(f"Keywords: {keywords}")
print()

for kw in keywords:
    found = kw in msg.lower()
    print(f"  '{kw}' in message.lower(): {found}")

match = any(kw in msg.lower() for kw in keywords)
print()
print(f"Overall match: {match}")
print("=" * 70)

