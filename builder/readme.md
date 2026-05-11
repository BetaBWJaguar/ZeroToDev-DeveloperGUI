# 🧠 Internal Build Documentation — ZeroToDev Developer GUI

This document is intended **for internal use only**.  
It explains how to build, package, and archive the project executables for distribution using the custom `build.py` script.  
End users **should not** run or modify this process — it is strictly for development and release management.

---

## 📦 Build Script Overview

**File:** `build.py`  
**Purpose:** Automates PyInstaller builds, cleanup, and packaging for the ZeroToDev Developer GUI.

This script is designed to be used **only by the project maintainer (Tuna Ocak)**.  
It ensures consistency in release builds across environments and enforces controlled naming, versioning, and structure.

---

## ⚙️ Current Configuration

| Parameter | Value                                |
|------------|--------------------------------------|
| **App Name** | `ZeroToDev-DeveloperGUI`             |
| **Version** | `1.4`                                |
| **Supported Platform(s)** | Windows (`win`)                      |
| **Spec Suffix Format** | `build_win.spec`                     |
| **Default Output Archive** | `ZeroToDev-DeveloperGUI-1.4-win.zip` |

---
