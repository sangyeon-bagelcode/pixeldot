"""CLI entry point: python -m pixeldot setup"""

from __future__ import annotations

import sys
from pathlib import Path

from ._skill_template import SKILL_CONTENT


# Map of platform -> (file_path, wrapper_function)
# Each wrapper takes the skill content and returns the final file content.
PLATFORMS = {
    "claude": {
        "paths": [
            ".claude/commands/pixel-art.md",
            "CLAUDE.md",
        ],
    },
    "codex": {
        "paths": ["AGENTS.md"],
    },
    "gemini": {
        "paths": ["GEMINI.md"],
    },
    "cursor": {
        "paths": [".cursor/rules/pixel-art.mdc"],
    },
    "copilot": {
        "paths": [".github/copilot-instructions.md"],
    },
    "windsurf": {
        "paths": [".windsurf/rules/pixel-art.md"],
    },
}


def _claude_md_content() -> str:
    return (
        "# Pixel Art\n\n"
        "Use `pixeldot` for all pixel art creation. "
        "See `.claude/commands/pixel-art.md` for the full guide, "
        "or run `/pixel-art`.\n"
    )


def _cursor_mdc_content(skill: str) -> str:
    return (
        "---\n"
        "description: Pixel art creation with pixeldot\n"
        'globs: ["**/*.py"]\n'
        "alwaysApply: false\n"
        "---\n\n"
        + skill
    )


def _write_file(path: Path, content: str, force: bool = False) -> bool:
    """Write file if it doesn't exist or force is True. Returns True if written."""
    if path.exists() and not force:
        # For CLAUDE.md/AGENTS.md/GEMINI.md, append instead of skip
        if path.name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md"):
            existing = path.read_text()
            if "pixeldot" in existing:
                print(f"  skip {path} (pixeldot already mentioned)")
                return False
            path.write_text(existing.rstrip() + "\n\n" + content)
            print(f"  append {path}")
            return True
        print(f"  skip {path} (already exists, use --force to overwrite)")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  create {path}")
    return True


def setup(force: bool = False) -> None:
    """Set up pixeldot skill files for all AI agent platforms."""
    print("pixeldot setup — registering skills for AI agents\n")

    written = 0

    # Claude Code: skill file + CLAUDE.md entry
    written += _write_file(
        Path(".claude/commands/pixel-art.md"), SKILL_CONTENT, force
    )
    written += _write_file(Path("CLAUDE.md"), _claude_md_content(), force)

    # Codex (OpenAI): AGENTS.md
    written += _write_file(Path("AGENTS.md"), SKILL_CONTENT, force)

    # Gemini CLI: GEMINI.md
    written += _write_file(Path("GEMINI.md"), SKILL_CONTENT, force)

    # Cursor: .cursor/rules/pixel-art.mdc
    written += _write_file(
        Path(".cursor/rules/pixel-art.mdc"),
        _cursor_mdc_content(SKILL_CONTENT),
        force,
    )

    # GitHub Copilot: .github/copilot-instructions.md
    written += _write_file(
        Path(".github/copilot-instructions.md"), SKILL_CONTENT, force
    )

    # Windsurf: .windsurf/rules/pixel-art.md
    written += _write_file(
        Path(".windsurf/rules/pixel-art.md"), SKILL_CONTENT, force
    )

    print(f"\nDone. {written} file(s) written.")
    print("All AI agents in this project can now use pixeldot for pixel art.")


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] == "help":
        print("Usage: python -m pixeldot <command>\n")
        print("Commands:")
        print("  setup          Register pixeldot skills for all AI agent platforms")
        print("  setup --force  Overwrite existing skill files")
        print("  help           Show this message")
        return

    if args[0] == "setup":
        force = "--force" in args
        setup(force)
    else:
        print(f"Unknown command: {args[0]}")
        print("Run 'python -m pixeldot help' for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
