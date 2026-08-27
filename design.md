# KRONOS Design Document

## Overview

KRONOS is an AI-powered criminal network analysis system. The frontend is a Streamlit dashboard with a professional dark sci-fi aesthetic (Minority Report-inspired, restrained). Target audience: makeathon judges. The UI must look visually striking, convey the concept instantly, and support a smooth demo flow.

## Core User Story

An investigator searches for or is shown suspicious individuals. The system surfaces everything related — identity, connections, financial history, risk scores. The network graph reveals hidden relationships between entities. ARIA Copilot answers natural-language queries with structured intel reports.

## Design Philosophy

**"Every glow is earned."** A border glows because it signals risk. An animation plays because data arrived. Nothing decorative without function. Professional first, sci-fi second.

---

## Design System

### Colors

| Token | Value | Usage |
|-------|-------|-------|
| `bg-main` | `#0A0D12` | Page background |
| `bg-surface` | `#111827` | Card backgrounds |
| `bg-surface-elevated` | `#1A2130` | Elevated panels, headers |
| `border-subtle` | `#1F2937` | Default card borders |
| `border-active` | `#06B6D4` | Active/focused element borders (cyan glow) |
| `text-primary` | `#F1F5F9` | Main text |
| `text-secondary` | `#94A3B8` | Labels, descriptions |
| `text-muted` | `#64748B` | Timestamps, metadata |
| `accent-cyan` | `#06B6D4` | Primary system accent (active, links) |
| `accent-blue` | `#3B82F6` | Secondary accent (buttons, focus) |
| `risk-critical` | `#EF4444` | Critical severity |
| `risk-high` | `#F97316` | High severity |
| `risk-medium` | `#F59E0B` | Medium severity |
| `risk-low` | `#10B981` | Low severity |

### Typography

- **Headers**: System sans-serif (Inter if available), tight letter-spacing, uppercase for section labels
- **Data/IDs**: JetBrains Mono — monospace for entity IDs, confidence scores, timestamps
- **Body**: Clean sans-serif, 0.85-0.9rem for readability

### Sci-Fi Elements (Restrained)

- **HUD corner brackets**: Subtle `[ ]` framing on hero cards — thin, low-opacity
- **Scan-line loading**: A thin cyan horizontal line sweeps across on data fetch
- **Pulsing live dot**: Green dot with soft pulse on live/connected indicators
- **Gradient glow borders**: Active entity or high-risk cards get a subtle border glow (not full-card glow — just the border)
- **Classification bar**: Top of page, monospace uppercase, amber text — "LAW ENFORCEMENT SENSITIVE"

### Component Patterns

- **Metric Card**: Fixed-height tile, monospace value, uppercase label, subtle subtext
- **Intel Table**: Dark header row, subtle row hover, risk badges inline, monospace IDs
- **Risk Badge**: Pill-shaped, colored border + faded background, uppercase monospace text
- **Status Pill**: Dot + label, dot color indicates state (live/offline/warning)
- **ID Pill**: Cyan monospace text on dark background, thin border — for entity/case IDs

---

## Page Designs

### 1. Dashboard (Hero Page) — "Command Center"

**Layout**: Full-width, dense but scannable.

```
┌─────────────────────────────────────────────────────────┐
│ CLASSIFICATION BAR                                       │
├─────────────────────────────────────────────────────────┤
│ KRONOS header + API status indicator                     │
├────────┬────────┬────────┬────────┬────────────────────┤
│ Metric │ Metric │ Metric │ Metric │ Metric              │
│ Card   │ Card   │ Card   │ Card   │ Card                │
├────────┴────────┴────────┴────────┴────────────────────┤
│                                                          │
│  ┌─ Flagged Individuals ──────┐  ┌─ Activity Feed ────┐ │
│  │ Top 5 suspects w/ risk     │  │ Scrolling events   │ │
│  │ scores, entity type,       │  │ "Entity flagged"   │ │
│  │ one-line reason            │  │ "Pattern detected" │ │
│  │ Click → Entity Profile     │  │ "Case opened"      │ │
│  └────────────────────────────┘  └────────────────────┘ │
│                                                          │
│  ┌─ Network Intelligence Canvas (full width) ──────────┐ │
│  │ Mini graph preview / integration container           │ │
│  │ Height: ~350px                                       │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Metrics**: Total Entities, Active Cases, Flagged Suspects, Patterns Detected, Network Nodes

**Flagged Individuals**: Top 3-5 suspects — risk badge, entity type icon placeholder, name/alias, one-line reason ("Multiple SARs filed", "3 shell company connections")

**Activity Feed**: Timestamped event list — newest at top, auto-scrolling feel, each entry has severity dot + description

**Network Canvas**: Integration container for friend's graph. Styled with HUD corners, dashed border when empty, solid when graph loads.

---

### 2. Search Entities

**Layout**:

```
┌─────────────────────────────────────────────────────────┐
│ Page title + subtitle                                    │
├─────────────────────────────────────────────────────────┤
│ [ ████████████ Search Input ████████████ ] [Execute]     │
├─────────────────────────────────────────────────────────┤
│ Filter chips: [Person] [Phone] [Vehicle] [Org] [...]    │
│               Risk: [All] [HIGH] [MED] [LOW]            │
├─────────────────────────────────────────────────────────┤
│ Results count + case scope indicator                     │
│ ┌───────────────────────────────────────────────────┐   │
│ │ Intel Table: Name | Type | Risk | Confidence | ID │   │
│ │ Row 1 (clickable → Entity Profile)                │   │
│ │ Row 2                                             │   │
│ │ ...                                               │   │
│ └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

- Search bar: Large, prominent, monospace placeholder text
- Filters: Chip/pill style toggles
- Table: Clean, sortable, clickable rows navigate to Entity Profile

---

### 3. Entity Profile

**Layout**:

```
┌─────────────────────────────────────────────────────────┐
│ Breadcrumb: Search > Entity Profile                      │
├──────────────────────────┬──────────────────────────────┤
│ Identity Card            │ Connections & Activity        │
│ ┌──────────────────┐     │ ┌──────────────────────────┐ │
│ │ Name/Alias       │     │ │ Linked entities (count)  │ │
│ │ Entity Type      │     │ │ Quick connection list     │ │
│ │ RISK: [BADGE]    │     │ │ Connected cases          │ │
│ │ Key attributes   │     │ └──────────────────────────┘ │
│ │ (phone, address, │     │ ┌──────────────────────────┐ │
│ │  financial IDs)  │     │ │ Financial Timeline       │ │
│ └──────────────────┘     │ │ Recent transactions      │ │
│                          │ │ Flagged activity          │ │
│                          │ └──────────────────────────┘ │
├──────────────────────────┴──────────────────────────────┤
│ Evidence / Notes / Raw Data                              │
└─────────────────────────────────────────────────────────┘
```

- Identity card gets a subtle glow border if risk is HIGH/CRITICAL
- Connections show count + entity type breakdown
- Financial timeline: chronological list with flagged items highlighted

---

### 4. Investigations

**Layout**: Table or card grid of active cases.

Each card:
- Case ID (monospace, cyan)
- Status badge (OPEN/CLOSED/ACTIVE)
- Title/description
- Entity count involved
- Last activity timestamp
- Priority/severity indicator

Click → expands or navigates to investigation detail view.

---

### 5. Suspicious Patterns

**Layout**: Intel table of AI-detected anomalies.

Columns: Pattern Type | Severity | Involved Entities | Confidence % | Detected At

- Severity color-coded with risk badges
- Confidence shown as monospace percentage
- Expandable rows: clicking reveals pattern detail, involved entity list, reasoning

---

### 6. Network Summary (Hero Page)

**Layout**: Near full-page graph container.

```
┌─────────────────────────────────────────────────────────┐
│ Page title (minimal)                                     │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │                                                     │ │
│ │          NETWORK GRAPH CONTAINER                    │ │
│ │          (Friend's integration)                     │ │
│ │          Full width, ~600px+ height                 │ │
│ │                                                     │ │
│ │  Overlay controls:                                  │ │
│ │  [Zoom +/-] [Filter: type] [Highlight paths]       │ │
│ │                                                     │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ Optional: Stats bar below (nodes, edges, clusters)       │
└─────────────────────────────────────────────────────────┘
```

- Container styled with HUD corners, solid border
- When empty/loading: dashed border with "Awaiting network data" message
- Overlay controls positioned absolute over the graph
- Stats bar: monospace numbers — "247 NODES | 891 EDGES | 12 CLUSTERS"

---

### 7. ARIA Copilot (Hero Page) — Terminal/Command Style

**Layout**:

```
┌─────────────────────────────────────────────────────────┐
│ ARIA // Intelligence Query Interface                     │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ QUERY LOG (scrollable)                              │ │
│ │                                                     │ │
│ │ > user query here                                   │ │
│ │ ┌─ ARIA RESPONSE ─────────────────────────────────┐ │ │
│ │ │ CONFIDENCE: [92%]  SOURCES: 4                   │ │ │
│ │ │                                                  │ │ │
│ │ │ Structured answer text...                        │ │ │
│ │ │                                                  │ │ │
│ │ │ SUPPORTING EVIDENCE:                             │ │ │
│ │ │ [1] Source description — entity link             │ │ │
│ │ │ [2] Source description — entity link             │ │ │
│ │ └──────────────────────────────────────────────────┘ │ │
│ │                                                     │ │
│ │ > another query...                                  │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ Suggested: [Who connects X to Y?] [Show SARs for...]    │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ARIA> [input field]                     [EXECUTE]   │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

- **Input**: Monospace, terminal-style with "ARIA>" prompt prefix
- **User queries**: Prefixed with `>`, right-aligned or left with distinct styling
- **ARIA responses**: Structured cards with:
  - Confidence score (monospace badge)
  - Source count
  - Answer text (clean, readable)
  - Supporting evidence as numbered references with entity links
- **Suggested queries**: Chip buttons above input for common questions
- **Loading state**: "PROCESSING..." with scan-line animation
- **No chat bubbles** — everything feels like a system terminal log

---

## Navigation & Sidebar

- **Sidebar**: Streamlit native navigation only — page links, no extra controls
- **Header**: Classification bar + KRONOS branding + API connection status (live dot)
- **Breadcrumbs**: On sub-pages (Entity Profile) to show navigation path

---

## Data Strategy

- **Backend-dependent**: All data fetched from FastAPI backend
- **Offline states**: Clean empty states when backend unavailable (styled, not broken-looking)
- **No fallback dummy data**: If backend is down, show "Backend Offline" indicator

---

## Integration Points

### Network Graph (Friend's Component)
- Container div with fixed dimensions and ID for mounting
- Accepts: entity data, relationship data, highlight/filter state
- The frontend provides: styled container, loading state, empty state, overlay controls shell
- The friend provides: actual graph rendering logic

### ARIA Copilot Backend
- POST queries to backend endpoint
- Expects response: `{ answer, confidence, sources[], intent, entities_referenced[] }`
- Frontend handles: rendering structured responses, loading state, error state, conversation history

---

## Demo Flow (Recommended)

1. **Open Dashboard** — judges see the command center: metrics, flagged suspects, live activity
2. **Click a flagged individual** — navigates to Entity Profile showing their full dossier
3. **Open Network Summary** — reveal their hidden connections in the graph
4. **Open ARIA Copilot** — ask "Who connects [Person A] to [Person B]?" — get structured intel report
5. **Show Search** — demonstrate filtering by entity type, risk level

This flow tells the story: "The system flags suspects → you drill into them → the graph reveals hidden networks → the AI explains what it found."
