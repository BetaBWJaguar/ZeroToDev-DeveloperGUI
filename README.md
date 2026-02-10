# Zero to Dev - Developer GUI

<div align="center">

![Version](https://img.shields.io/badge/version-1.3.1-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![TTS](https://img.shields.io/badge/TTS-Enabled-orange)
![STT](https://img.shields.io/badge/STT-Enabled-blueviolet)
![AI Powered](https://img.shields.io/badge/AI-Powered-brightgreen)

**A comprehensive Text-to-Speech (TTS) and Speech-to-Text (STT) application with AI-powered features**

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Usage](#usage)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Building](#building)
- [Contact](#contact)

---

## Overview

**Zero to Dev - Developer GUI** is a powerful desktop application built with Python and Tkinter that provides comprehensive Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities. The application features a modern, responsive GUI with support for multiple languages, user authentication, AI-powered recommendations, and extensive audio processing capabilities.

### Key Technologies

- **GUI Framework**: Tkinter with custom styling
- **TTS Services**: Microsoft Edge TTS, Google TTS (gTTS)
- **STT Engines**: Whisper, Vosk
- **AI Integration**: DeepInfra, custom AI recommendation system
- **Database**: MongoDB (user management), SQLite (logging)
- **Audio Processing**: FFmpeg, PyDub, SoundFile
- **Authentication**: bcrypt, Two-Factor Authentication (2FA)
- **Web Server**: FastAPI (for email verification)

---

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Text-to-Speech** | Convert text to speech using multiple TTS services (Edge TTS, Google TTS) |
| **Speech-to-Text** | Transcribe audio files using Whisper or Vosk models |
| **Multiple Audio Formats** | Export audio in MP3, WAV, WEBM, FLAC, AAC formats |
| **Voice Effects** | Apply pitch, speed, volume adjustments, echo, reverb, and robot effects |
| **Markup Support** | Use SSML-like tags for emphasis, breaks, prosody, and more |
| **Multi-language** | Support for English, Turkish, and German UI languages |
| **User Management** | Complete authentication system with registration, login, and password reset |

### Advanced Features

- **AI-Powered Recommendations**: Smart suggestions based on user behavior and context
- **ZIP Package Export**: Export TTS output as structured packages with metadata, transcripts, and segments
- **Real-time Preview**: Listen to audio before full conversion
- **Theme System**: Light, dark, and default color themes
- **Logging System**: Comprehensive logging with file and SQLite database options
- **Auto-updater**: Built-in update checker and installer
- **System Monitoring**: Real-time CPU, memory, and disk usage monitoring
- **Statistics Dashboard**: User activity tracking and visualization
- **Two-Factor Authentication**: Enhanced security with TOTP-based 2FA

### Developer Features

- **AI Monitoring GUI**: Track AI provider performance and latency (This Modules for just Admin Users)
- **Debug Mode**: Detailed logging for troubleshooting
- **Single Instance Lock**: Prevent multiple application instances
- **Startup Optimizer**: Fast application startup with background initialization
- **Modular Architecture**: Well-organized code structure for easy maintenance

---

## Screenshots

> *Note: Screenshots will be added in future updates*

---

## Usage

### First-Time Setup

1. **Launch the Application**: Run Program
2. **Register an Account**: Create a new user account
3. **Verify Email**: Verify your email address
4. **Configure Settings**: Set up your preferred TTS service, voice, and language

### Basic Text-to-Speech Conversion

1. **Enter Text**: Type or paste your text in the text area
2. **Select Service**: Choose between Edge TTS or Google TTS
3. **Select Voice**: Choose male or female voice (Edge TTS only)
4. **Select Format**: Choose output format (MP3, WAV, WEBM, FLAC, AAC)
5. **Select Language**: Choose the target language for TTS
6. **Preview**: Click "Preview" to hear a 20-second sample
7. **Convert**: Click "Convert" to generate the full audio file

### Using Markup Tags

Enable markup support in Config Settings and use tags like:

```xml
Hello <emphasis level="strong">world</emphasis>!
<break time="500ms"/>
I sound like a <style type="radio">professional radio host</style> today!
<prosody rate="1.2" pitch="3">This is faster and higher pitched</prosody>
<say-as interpret-as="digits">1234</say-as>
```

### Speech-to-Text Transcription

1. Open the STT GUI
2. Select your preferred STT model (Whisper or Vosk)
3. Load an audio file
4. Click "Transcribe" to convert speech to text

### ZIP Package Export

Enable ZIP export in Package Settings to create structured packages containing:

- Audio segments
- Transcript (TXT, MD, DOCX, PDF, or JSON)
- Metadata
- Preview audio
- Project configuration

---

## Configuration

### Application Settings

Settings are stored in memory and can be configured through:

- **Config Settings**: Log mode, log handler, markup support
- **Voice Settings**: Pitch, speed, volume, effects
- **Language Settings**: UI language selection
- **Theme Settings**: Light, dark, or default theme
- **ZIP Settings**: Export options and password protection

### AI Configuration

Edit [`ai_system/config/AIConfig.py`](ai_system/config/AIConfig.py:1) to configure AI providers:

```python
AI_PROVIDERS = {
    "deepinfra": {
        "api_key": "your-api-key",
        "model": "ai-model"
    }
}
```

### Language Files

UI translations are located in the [`langs/`](langs/) directory:

- [`english.json`](langs/english.json:1)
- [`turkish.json`](langs/turkish.json:1)
- [`german.json`](langs/german.json:1)

### Theme Configuration

Theme files are located in the [`utils/`](utils/) directory:

- [`Colors_default.json`](utils/Colors_default.json:1)
- [`Colors_light.json`](utils/Colors_light.json:1)
- [`Colors_dark.json`](utils/Colors_dark.json:1)

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        GUI Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Main GUI   │  │  Auth GUI    │  │  Settings    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   TTS Engine │  │  STT Engine  │  │  AI Engine   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ User Manager │  │ Lang Manager │  │ Logs Manager │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   MongoDB    │  │   SQLite     │  │  File System │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Key Modules

| Module | Description |
|--------|-------------|
| [`GUI.py`](GUI.py:1) | Main application window and UI components |
| [`main.py`](main.py:1) | Application entry point and initialization |
| [`auth_gui/`](auth_gui/) | Authentication system (login, register, 2FA) |
| [`tts/`](tts/) | Text-to-Speech services (Edge TTS, Google TTS) |
| [`stt/`](stt/) | Speech-to-Text engines (Whisper, Vosk) |
| [`ai_system/`](ai_system/) | AI integration and recommendations |
| [`usermanager/`](usermanager/) | User management and authentication |
| [`language_manager/`](language_manager/) | Multi-language support |
| [`logs_manager/`](logs_manager/) | Logging and debugging |
| [`markup/`](markup/) | SSML-like markup processing |
| [`media_formats/`](media_formats/) | Audio format handlers |
| [`updater/`](updater/) | Auto-update system |

---

## Project Structure

```
zero-to-dev-gui/
├── app.py                          # FastAPI server for email verification
├── main.py                         # Application entry point
├── GUI.py                          # Main GUI window
├── requirements.txt                # Python dependencies
├── client-version.txt              # Current version
├── .gitignore                      # Git ignore rules
│
├── ai_system/                      # AI integration module
│   ├── AI.py                       # AI engine
│   ├── AI_Model.py                 # AI model wrapper
│   ├── AI_Utils.py                 # AI utilities
│   ├── PromptBuilder.py            # AI prompt builder
│   ├── config/                     # AI configuration
│   │   └── AIConfig.py
│   ├── monitoring/                 # AI monitoring GUI
│   │   ├── AIMonitoringGUI.py
│   │   └── LatencyTracker.py
│   ├── providers/                  # AI providers
│   │   ├── BaseProvider.py
│   │   ├── ProviderRegistry.py
│   │   ├── TimedProviders.py
│   │   └── prov/
│   │       └── DeepInfraProvider.py
│   └── data_collection/            # AI data collection
│       ├── DataCollection.py
│       ├── DataCollectionDatabase.py
│       └── DataCollectionDatabaseManager.py
│
├── auth_gui/                       # Authentication GUI
│   ├── MainAuthGUI.py              # Main auth window
│   ├── LoginGUI.py                 # Login window
│   ├── RegisterGUI.py              # Registration window
│   ├── ResetPasswordGUI.py         # Password reset window
│   ├── auth_factory.py             # Auth factory pattern
│   └── snapshot_service.py         # Snapshot service
│
├── builder/                        # Build scripts
│   ├── build.py                    # Build script
│   ├── build_win.spec              # Windows build spec
│   ├── build_linux.spec            # Linux build spec
│   └── readme.md                   # Builder documentation
│
├── data_manager/                   # Data management
│   ├── DataManager.py              # Data manager
│   └── MemoryManager.py           # Memory manager
│
├── fragments/                      # UI fragments
│   └── UIFragments.py
│
├── gui_listener/                   # GUI event listeners
│   └── GUIListener.py
│
├── language_manager/               # Language management
│   └── LangManager.py
│
├── langs/                          # Language files
│   ├── english.json
│   ├── turkish.json
│   └── german.json
│
├── logs/                           # Log files
│   ├── app.log
│   ├── debug.log
│   ├── errors.log
│   ├── warnings.log
│   └── json/
│       └── logs.jsonl
│
├── logs_manager/                   # Logging system
│   ├── LogsManager.py
│   ├── LogsHelperManager.py
│   └── SQLite_Handler.py
│
├── markup/                         # Markup processing
│   ├── MarkupManager.py
│   ├── MarkupManagerTags.py
│   ├── MarkupManagerUtility.py
│   ├── VoiceCharacterManager.py
│   └── utils/
│       ├── SayAsTagManager.py
│       └── sayaslangmanager/
│           ├── Phone_formats.json
│           ├── PhoneFormatter.py
│           ├── SayAsEN.py
│           └── SayAsTR.py
│
├── media_formats/                  # Audio format handlers
│   ├── BaseFormat.py
│   ├── MP3.py
│   ├── WAV.py
│   ├── WEBM.py
│   ├── FLAC.py
│   └── AAC.py
│
├── mode_selector/                  # App mode selector
│   └── AppModeSelectorGUI.py
│
├── output/                         # Output directory
│   └── tts_*.mp3                   # Generated audio files
│
├── stt/                            # Speech-to-Text
│   ├── STTEngine.py                # STT engine base
│   ├── MediaFormats.py             # STT media formats
│   ├── stt-config.json             # STT configuration
│   ├── factory/
│   │   └── STTFactory.py
│   └── stt__models/
│       ├── WhisperSTT.py           # Whisper STT model
│       └── VoskSTT.py              # Vosk STT model
│
├── system/                         # System utilities
│   └── SystemUsageGUI.py           # System usage monitor
│
├── tts/                            # Text-to-Speech
│   ├── GTTS.py                     # Google TTS
│   ├── MicrosoftEdgeTTS.py         # Edge TTS
│   └── utility/
│       ├── TTSHelper.py            # TTS utilities
│       └── sounds/
│           └── ding.wav            # Notification sound
│
├── updater/                        # Auto-updater
│   ├── Updater.py                  # Updater main
│   ├── UpdaterGUI.py               # Updater GUI
│   ├── Updater_Utils.py            # Updater utilities
│   ├── Update_Checker.py           # Update checker
│   ├── update_info.json            # Update info
│   └── Updater.spec                # Updater build spec
│
├── usermanager/                    # User management
│   ├── UserManager.py             # User manager
│   ├── UserManagerUtils.py         # User utilities
│   ├── ActivityManager.py          # Activity manager
│   ├── database_config.json        # Database config
│   ├── smtp_config.json            # SMTP config
│   ├── user/
│   │   ├── User.py                 # User model
│   │   ├── UserRole.py             # User roles
│   │   └── UserStatus.py           # User statuses
│   └── verfiy_manager/             # Verification manager
│       ├── VerifyController.py     # Verify controller
│       ├── VerifyUtils.py          # Verify utilities
│       ├── templates/
│       │   ├── verify_email.html
│       │   └── reset_pass.html
│       └── twofa_manager/
│           ├── TwoFA.py            # 2FA manager
│           ├── TwoFAUtils.py       # 2FA utilities
│           └── TwoFAVerifyGUI.py   # 2FA verification GUI
│
├── utils/                          # Utilities
│   ├── Colors_default.json         # Default theme
│   ├── Colors_light.json           # Light theme
│   ├── Colors_dark.json            # Dark theme
│   ├── Fonts.json                  # Font configuration
│   ├── Languages.json              # Supported languages
│   ├── DevInfo.json                # Developer info
│   └── Preset-Default.json        # Default presets
│
├── voicegui/                       # Voice settings GUI
│   └── VoiceGUI.py
│
├── zip/                            # ZIP export
│   └── ZIPConvertor.py             # ZIP converter
│
├── AppMode.py                      # Application mode
├── GUIError.py                     # GUI error handler
├── GUIHelper.py                    # GUI helper functions
├── GuideLabel.py                   # Guide label widget
│
├── PathHelper.py                   # Path helper
├── ScrollBar.py                    # Custom scrollbar
├── SingleInstance.py               # Single instance lock
├── StartupOptimizer.py             # Startup optimizer
├── STTGUI.py                       # STT GUI
│
├── theme_config.py                 # Theme configuration
│
├── TwoFAGUI.py                     # 2FA GUI
│
└── VoiceProcessor.py               # Voice processor
```

---

## Dependencies

### Core Dependencies

| Package | Version | Description |
|---------|---------|-------------|
| `tkinter` | Built-in | GUI framework |
| `edge-tts` | 7.2.3 | Microsoft Edge TTS |
| `gTTS` | 2.5.4 | Google Text-to-Speech |
| `vosk` | 0.3.45 | Vosk Speech Recognition |
| `openai-whisper` | - | OpenAI Whisper STT |
| `fastapi` | 0.121.0 | Web framework for verification |
| `uvicorn` | - | ASGI server |
| `pymongo` | 4.15.3 | MongoDB driver |
| `bcrypt` | 5.0.0 | Password hashing |
| `pyotp` | 2.9.0 | Two-Factor Authentication |
| `qrcode` | 8.2 | QR code generation |
| `pydub` | 0.25.1 | Audio processing |
| `soundfile` | 0.12.1 | Audio file I/O |
| `simpleaudio` | 1.0.4 | Audio playback |
| `matplotlib` | 3.10.7 | Plotting for statistics |
| `requests` | 2.32.5 | HTTP requests |
| `aiohttp` | 3.12.15 | Async HTTP client |
| `cryptography` | 46.0.3 | Cryptographic primitives |
| `python-docx` | 1.2.0 | DOCX file handling |
| `reportlab` | 4.4.4 | PDF generation |

### Full Dependency List

See [`requirements.txt`](requirements.txt:1) for the complete list of dependencies.  
Some dependencies may not be listed yet and will be added in future updates.

---

### Debugging

Enable debug mode in Config Settings:

1. Open **Config Settings** from the Help menu
2. Set **Log Mode** to `DEBUG`
3. Set **Log Handler** to `both` (file + SQLite)
4. Check logs in the `logs/` directory

---

## Building

### Building for Windows

```bash
cd builder
python build.py --clean --cython
```

---

## Contact

- **Developer**: Tuna Rasim OCAK
- **Project**: Zero to Dev - Developer GUI
- **Version**: 1.3.1
- **Email**: [tunarasimocak@gmail.com]

---

<div align="center">

[Back to Top](#zero-to-dev---developer-gui)

</div>
