# Universal Update Engine (v1.1.0)

A local-first, standalone desktop utility designed to execute a comprehensive, single-click maintenance sweep of both the Windows Operating System and installed third-party applications. 

## Key Features
- **Phase 1: Windows OS Updates** – Automatically checks for, downloads, and stages pending Windows cumulative updates and security patches using the `PSWindowsUpdate` framework.
- **Phase 2: Application Core Sweep** – Interrogates the Windows Package Manager (`winget`) to silently upgrade all compatible third-party software, bypassing license agreements and package prompts.
- **Automated Dependency Resolution** – Silently configures missing package providers (like NuGet) and handles execution policies seamlessly in the background to ensure a zero-prompt workflow.
- **Multi-Threaded UI** – Features a responsive Tkinter graphical interface that handles intensive background terminal operations without freezing or locking up the window.

## System Prerequisites
- **Operating System:** Windows 10 or Windows 11
- **Privileges:** Administrator access is required, as the engine modifies core system directories and executes low-level Windows Update routines.

## Deployment
This application is compiled into a standalone, portable executable binary (`UniversalUpdateEngine.exe`) with all necessary runtime assets embedded. No local Python installation or environment configuration is required for end-users.