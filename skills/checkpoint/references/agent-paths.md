# Agent memory & config path reference

Different agent platforms keep their memory system and project config files in different places. When doing the first-step inventory, check the table for whichever platform you're currently running on.

## Claude Code

| Purpose | Path |
|---|---|
| Cross-session memory (global) | `~/.claude/projects/<encoded-project-path>/memory/` |
| Memory index file | `~/.claude/projects/<...>/memory/MEMORY.md` |
| Global instructions | `~/.claude/CLAUDE.md` |
| Project-level instructions | project-root `CLAUDE.md` (can nest hierarchically) |
| Skills directory | `~/.claude/skills/<name>/SKILL.md` |

Memory files use YAML frontmatter: `name`, `description`, `type` (user / feedback / project / reference).

## OpenAI Codex

| Purpose | Path |
|---|---|
| Cross-session instructions (global) | `~/.codex/AGENTS.md` or `$CODEX_HOME/AGENTS.md` |
| Project-level instructions | project-root `AGENTS.md` (can nest hierarchically) |
| Project-level override | `AGENTS.override.md` (if present, overrides the AGENTS.md in the same directory) |
| Skills directory | `~/.agents/skills/<name>/SKILL.md` or `.agents/skills/<name>/` inside the project |

Codex has no separate "memory file + index" mechanism — all cross-session information lives directly in `AGENTS.md`. When syncing, put the "project facts" portion of the content into AGENTS.md.

Also check for a `TEAM_GUIDE.md` or `.agents.md` in the project — these are Codex's fallback filenames.

## OpenClaw

| Purpose | Path |
|---|---|
| User-level skills | `~/.openclaw/skills/<name>/SKILL.md` (auto-created on first run) |
| Project-level skills | `.openclaw/skills/<name>/SKILL.md` (under the repo root) |
| Workspace skills | the current workspace's `skills/` directory |

**Load priority**: workspace > project-agent > personal-agent > managed/local > bundled > extra dirs. A same-named skill at a higher priority overrides a lower one.

OpenClaw has no separate "memory file + index" mechanism either; cross-session information can go in a project-root markdown file (CLAUDE.md / AGENTS.md / equivalent), mirroring the Codex approach. Frontmatter supports a `metadata.openclaw` field for load-time gating (filtering by OS, environment variable, or binary dependency), but checkpoint doesn't need it.

## OpenCode

| Purpose | Path |
|---|---|
| Global config | `~/.config/opencode/` |
| Project config | `.opencode/` |
| Skills directory (project) | `.opencode/skills/`, `.claude/skills/`, `.codex/skills/` are all scanned |
| Skills directory (global) | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.codex/skills/` |

OpenCode reads both Claude Code's and Codex's directories, so a skill installed under `~/.claude/skills/` is recognized by all three tools. OpenClaw uses its own `~/.openclaw/skills/` and needs a separate install (or a symlink).

## If the current agent has no dedicated memory system

Skip the "memory" layer and put all the effort into:
- project-root markdown (CLAUDE.md / AGENTS.md / this platform's equivalent)
- README.md
- docs/

This is still an effective sync — memory is a nice-to-have; docs are the baseline guarantee of project knowledge.

## Cross-platform coexistence strategy

If a project is used by both Claude Code users and Codex users, the recommended approach is:

- **Keep both `CLAUDE.md` and `AGENTS.md` in the project root**, either symlinked to each other or maintained in parallel
- Or one file as the primary content, with the other reduced to a one-line "See CLAUDE.md" pointer
- docs/ and README are platform-neutral and don't need to be duplicated
