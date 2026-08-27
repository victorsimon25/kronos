# KRONOS Frontend

Streamlit dashboard for a criminal network analysis system. Dark sci-fi intelligence theme.

## Cross-Platform AI

This project is developed using both **Gemini (via Antigravity)** and **Claude**. This file (`gemini.md`) is the instruction file for Gemini. An equivalent `CLAUDE.md` exists for Claude. Both files must stay in sync — if you update project context, rules, or structure here, mirror the changes in `CLAUDE.md` as well.

## Stack

- Streamlit (wide layout, native navigation)
- httpx for backend API calls
- Plotly for charts
- Pydantic models for data
- Custom CSS for theming

## Structure

```
app.py                  — entrypoint
config.py               — constants, palette, API config
navigation_registry.py  — st.Page objects
views/                  — page render functions (one per page)
components/             — reusable UI components
services/               — API client + domain services
models/                 — Pydantic data models
utils/                  — state management, formatting, navigation helpers
assets/styles.css       — global CSS theme
```

## Pages (7)

Dashboard, Search Entities, Entity Profile, Investigations, Suspicious Patterns, Network Summary, ARIA Copilot

Hero pages: Dashboard, Network Summary, ARIA Copilot

## Design Rules

- Professional dark sci-fi aesthetic. See design.md for full spec.
- Every visual flourish must be functional (glow = risk, pulse = live, animation = data arriving).
- Monospace (JetBrains Mono) for IDs, scores, timestamps. Sans-serif for everything else.
- Sidebar: navigation only. No extra controls.
- Data: backend-dependent. Show offline states when backend is down, no fallback dummy data.
- Network graph: container/integration point only — actual graph built by teammate.
- ARIA Copilot: terminal/command style, not chat bubbles. Structured intel reports with confidence + evidence.

## Backend

FastAPI at `localhost:8000` (configurable via `BACKEND_URL` env var). Frontend-first design — backend integration comes later.

## Running

```
streamlit run app.py
```
