#!/usr/bin/env python3
"""
Diablo 4 Overlay - Main Application
Displays build data from maxroll.gg in a Tkinter overlay window.
"""

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

# Constants
BUILDS_FILE = Path("builds.json")
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
OVERLAY_TITLE = "Diablo 4 Build Overlay"

# Colors
BG_COLOR = "#1a1a1a"
FG_COLOR = "#ffffff"
ACCENT_COLOR = "#d4a017"  # Diablo gold
SECONDARY_BG = "#2a2a2a"
BORDER_COLOR = "#444444"

class BuildOverlay:
    """Tkinter-based overlay for displaying Diablo 4 build data."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.build_data = {}
        self.current_version = "Endgame"

        self.setup_window()
        self.load_build_data()
        self.create_widgets()

    def setup_window(self):
        """Configure the overlay window."""
        self.root.title(OVERLAY_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)

        # Make window always on top
        self.root.attributes("-topmost", True)

        # Set window to be click-through (optional)
        self.root.attributes("-toolwindow", True)  # No taskbar icon

    def load_build_data(self):
        """Load build data from JSON file."""
        try:
            if BUILDS_FILE.exists():
                with BUILDS_FILE.open("r", encoding="utf-8") as f:
                    self.build_data = json.load(f)

                # Get available versions
                self.versions = list(self.build_data.get("versions", {}).keys())
                if self.versions:
                    self.current_version = self.versions[0]  # Default to first version
                else:
                    self.versions = ["Default"]
                    self.current_version = "Default"
            else:
                self.versions = ["No data"]
                self.current_version = "No data"

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load build data: {e}")
            self.versions = ["Error"]
            self.current_version = "Error"

    def create_widgets(self):
        """Create all UI widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header with version selector
        header_frame = tk.Frame(main_frame, bg=SECONDARY_BG)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Version selector
        version_label = tk.Label(
            header_frame,
            text="Version:",
            bg=SECONDARY_BG,
            fg=FG_COLOR,
            font=("Arial", 10, "bold")
        )
        version_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.version_combo = ttk.Combobox(
            header_frame,
            values=self.versions,
            state="readonly",
            width=20
        )
        self.version_combo.set(self.current_version)
        self.version_combo.bind("<<ComboboxSelected>>", self.on_version_change)
        self.version_combo.pack(side=tk.LEFT, padx=5, pady=5)

        # Build name
        build_name = self.build_data.get("build_name", "Unknown Build")
        build_label = tk.Label(
            header_frame,
            text=build_name,
            bg=SECONDARY_BG,
            fg=ACCENT_COLOR,
            font=("Arial", 12, "bold")
        )
        build_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Create tabs for different sections
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Equipment tab
        self.equipment_frame = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.equipment_frame, text="Equipment")

        # Skills tab
        self.skills_frame = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.skills_frame, text="Skills")

        # Gems tab
        self.gems_frame = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.gems_frame, text="Gems")

        # Paragon tab
        self.paragon_frame = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.paragon_frame, text="Paragon")

        # Update content
        self.update_content()

    def on_version_change(self, event=None):
        """Handle version selection change."""
        self.current_version = self.version_combo.get()
        self.update_content()

    def update_content(self):
        """Update all tabs with current version data."""
        version_data = self.build_data.get("versions", {}).get(self.current_version, {})

        # Clear existing content
        for frame in [self.equipment_frame, self.skills_frame, self.gems_frame, self.paragon_frame]:
            for widget in frame.winfo_children():
                widget.destroy()

        # Update equipment tab
        self.update_equipment_tab(version_data.get("equipment", {}))

        # Update skills tab
        self.update_skills_tab(version_data.get("skills", {}))

        # Update gems tab
        self.update_gems_tab(version_data.get("gems", {}))

        # Update paragon tab
        self.update_paragon_tab(version_data.get("paragon", []))

    def update_equipment_tab(self, equipment: Dict[str, Dict[str, str]]):
        """Update the equipment tab with equipment data."""
        if not equipment:
            tk.Label(
                self.equipment_frame,
                text="No equipment data available",
                bg=BG_COLOR,
                fg=FG_COLOR
            ).pack(pady=20)
            return

        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.equipment_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.equipment_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add equipment items
        for slot, item in equipment.items():
            item_frame = tk.Frame(scrollable_frame, bg=SECONDARY_BG)
            item_frame.pack(fill=tk.X, pady=2, padx=5)

            # Slot name
            slot_label = tk.Label(
                item_frame,
                text=f"{slot}:",
                bg=SECONDARY_BG,
                fg=ACCENT_COLOR,
                font=("Arial", 9, "bold"),
                width=12,
                anchor=tk.W
            )
            slot_label.pack(side=tk.LEFT, padx=5, pady=2)

            # Item name
            name_label = tk.Label(
                item_frame,
                text=item.get("name", "Unknown"),
                bg=SECONDARY_BG,
                fg=FG_COLOR,
                font=("Arial", 9),
                width=25,
                anchor=tk.W
            )
            name_label.pack(side=tk.LEFT, padx=5, pady=2)

            # Aspect
            aspect = item.get("aspect", "")
            if aspect:
                aspect_label = tk.Label(
                    item_frame,
                    text=f"[{aspect}]",
                    bg=SECONDARY_BG,
                    fg="#00ff00",  # Green for aspects
                    font=("Arial", 9, "italic"),
                    anchor=tk.W
                )
                aspect_label.pack(side=tk.LEFT, padx=5, pady=2)

    def update_skills_tab(self, skills: Dict[str, Dict[str, Any]]):
        """Update the skills tab with skills data."""
        if not skills:
            tk.Label(
                self.skills_frame,
                text="No skills data available",
                bg=BG_COLOR,
                fg=FG_COLOR
            ).pack(pady=20)
            return

        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.skills_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.skills_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add skills
        for slot, skill in skills.items():
            skill_frame = tk.Frame(scrollable_frame, bg=SECONDARY_BG)
            skill_frame.pack(fill=tk.X, pady=2, padx=5)

            # Slot
            slot_label = tk.Label(
                skill_frame,
                text=f"{slot}:",
                bg=SECONDARY_BG,
                fg=ACCENT_COLOR,
                font=("Arial", 9, "bold"),
                width=8,
                anchor=tk.W
            )
            slot_label.pack(side=tk.LEFT, padx=5, pady=2)

            # Skill name
            name_label = tk.Label(
                skill_frame,
                text=skill.get("name", "Unknown"),
                bg=SECONDARY_BG,
                fg=FG_COLOR,
                font=("Arial", 9),
                width=20,
                anchor=tk.W
            )
            name_label.pack(side=tk.LEFT, padx=5, pady=2)

            # Rank
            rank = skill.get("rank", 0)
            if rank:
                rank_label = tk.Label(
                    skill_frame,
                    text=f"Rank {rank}",
                    bg=SECONDARY_BG,
                    fg="#ffcc00",
                    font=("Arial", 9),
                    anchor=tk.W
                )
                rank_label.pack(side=tk.LEFT, padx=5, pady=2)

            # Glyph
            glyph = skill.get("glyph", "")
            if glyph:
                glyph_label = tk.Label(
                    skill_frame,
                    text=f"({glyph})",
                    bg=SECONDARY_BG,
                    fg="#00ffff",
                    font=("Arial", 9, "italic"),
                    anchor=tk.W
                )
                glyph_label.pack(side=tk.LEFT, padx=5, pady=2)

    def update_gems_tab(self, gems: Dict[str, Dict[str, Any]]):
        """Update the gems tab with gems data."""
        if not gems:
            tk.Label(
                self.gems_frame,
                text="No gems data available",
                bg=BG_COLOR,
                fg=FG_COLOR
            ).pack(pady=20)
            return

        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.gems_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.gems_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add gems
        for slot, gem in gems.items():
            gem_frame = tk.Frame(scrollable_frame, bg=SECONDARY_BG)
            gem_frame.pack(fill=tk.X, pady=2, padx=5)

            # Slot
            slot_label = tk.Label(
                gem_frame,
                text=f"{slot}:",
                bg=SECONDARY_BG,
                fg=ACCENT_COLOR,
                font=("Arial", 9, "bold"),
                width=15,
                anchor=tk.W
            )
            slot_label.pack(side=tk.LEFT, padx=5, pady=2)

            # Gem name
            name_label = tk.Label(
                gem_frame,
                text=gem.get("name", "Unknown"),
                bg=SECONDARY_BG,
                fg="#ff66ff",  # Purple for gems
                font=("Arial", 9),
                anchor=tk.W
            )
            name_label.pack(side=tk.LEFT, padx=5, pady=2)

            # Type and rank
            gem_type = gem.get("type", "")
            rank = gem.get("rank", 0)
            if gem_type or rank:
                info_label = tk.Label(
                    gem_frame,
                    text=f"{gem_type} {rank}".strip(),
                    bg=SECONDARY_BG,
                    fg=FG_COLOR,
                    font=("Arial", 9),
                    anchor=tk.W
                )
                info_label.pack(side=tk.LEFT, padx=5, pady=2)

    def update_paragon_tab(self, paragon_boards: List[Dict[str, Any]]):
        """Update the paragon tab with paragon board data."""
        if not paragon_boards:
            tk.Label(
                self.paragon_frame,
                text="No paragon data available",
                bg=BG_COLOR,
                fg=FG_COLOR
            ).pack(pady=20)
            return

        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.paragon_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.paragon_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add paragon boards
        for board in paragon_boards:
            board_frame = tk.Frame(scrollable_frame, bg=SECONDARY_BG)
            board_frame.pack(fill=tk.X, pady=5, padx=5)

            # Board name
            name_label = tk.Label(
                board_frame,
                text=board.get("name", "Unknown Board"),
                bg=SECONDARY_BG,
                fg=ACCENT_COLOR,
                font=("Arial", 10, "bold"),
                anchor=tk.W
            )
            name_label.pack(fill=tk.X, padx=5, pady=2)

            # Glyphs
            glyphs = board.get("glyphs", [])
            if glyphs:
                glyph_frame = tk.Frame(board_frame, bg=SECONDARY_BG)
                glyph_frame.pack(fill=tk.X, padx=5, pady=2)

                glyph_label = tk.Label(
                    glyph_frame,
                    text="Glyphs:",
                    bg=SECONDARY_BG,
                    fg=FG_COLOR,
                    font=("Arial", 9, "bold"),
                    anchor=tk.W
                )
                glyph_label.pack(side=tk.LEFT, padx=5, pady=2)

                for glyph in glyphs:
                    if isinstance(glyph, dict):
                        glyph_text = f"{glyph.get('name', '?')} (Lv{glyph.get('level', 0)})"
                        glyph_item = tk.Label(
                            glyph_frame,
                            text=glyph_text,
                            bg=SECONDARY_BG,
                            fg="#00ffff",
                            font=("Arial", 9),
                            anchor=tk.W
                        )
                        glyph_item.pack(side=tk.LEFT, padx=5, pady=2)

            # Stats
            stats = board.get("stats", {})
            if stats:
                stats_frame = tk.Frame(board_frame, bg=SECONDARY_BG)
                stats_frame.pack(fill=tk.X, padx=5, pady=2)

                stats_label = tk.Label(
                    stats_frame,
                    text="Stats:",
                    bg=SECONDARY_BG,
                    fg=FG_COLOR,
                    font=("Arial", 9, "bold"),
                    anchor=tk.W
                )
                stats_label.pack(side=tk.LEFT, padx=5, pady=2)

                for stat_id, stat_info in stats.items():
                    if isinstance(stat_info, dict):
                        stat_text = f"{stat_id}: {stat_info.get('value', 0)}"
                    else:
                        stat_text = f"{stat_id}: {stat_info}"

                    stat_item = tk.Label(
                        stats_frame,
                        text=stat_text,
                        bg=SECONDARY_BG,
                        fg="#00ff00",
                        font=("Arial", 9),
                        anchor=tk.W
                    )
                    stat_item.pack(side=tk.LEFT, padx=5, pady=2)

def main():
    """Main entry point for the overlay application."""
    root = tk.Tk()
    app = BuildOverlay(root)
    root.mainloop()

if __name__ == "__main__":
    main()