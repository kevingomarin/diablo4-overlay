#!/usr/bin/env python3
"""
Maxroll.gg Scraper for Diablo 4 Builds
Extracts equipment, aspects, skills, gems, and paragon boards from maxroll.gg build guides.
Uses the embedded plannerProfile JSON instead of Selenium for reliability.
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

# Constants
MAXROLL_URL = "https://maxroll.gg/d4/build-guides/dance-of-knives-rogue-guide"
OUTPUT_FILE = Path("builds.json")
TIMEOUT = 30  # seconds

# Gear slot mapping for better readability
SLOT_NAME_MAP = {
    4: "Helm",
    5: "Chest Armor",
    8: "Main Hand",
    9: "Off Hand",
    10: "Two-Handed Weapon",
    11: "Weapon (Ranged)",
    12: "Weapon (Alternate)",
    13: "Gloves",
    14: "Pants",
    15: "Boots",
    16: "Ring 1",
    17: "Ring 2",
    18: "Amulet"
}

def fetch_page(url: str) -> Optional[str]:
    """Fetch HTML content from URL with error handling."""
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

def extract_planner_profile(html: str) -> Optional[Dict[str, Any]]:
    """
    Extract the plannerProfile JSON from maxroll.gg HTML.
    The data is embedded in window.__remixContext as a JSON object.
    """
    soup = BeautifulSoup(html, "html.parser")

    for script in soup.find_all("script"):
        script_content = script.string
        if not script_content or "plannerProfile" not in script_content:
            continue

        # Find the remix context JSON
        match = re.search(r"window\.__remixContext\s*=\s*({.+?});", script_content, re.DOTALL)
        if not match:
            continue

        try:
            remix_context = json.loads(match.group(1))
            # Navigate to plannerProfile
            loader_data = remix_context.get("state", {}).get("loaderData", {})
            branch_posts = loader_data.get("branch-posts", {})
            post = branch_posts.get("post", {})
            gutenberg_blocks = post.get("gutenbergBlock", [])

            if gutenberg_blocks and isinstance(gutenberg_blocks, list):
                planner_profile = gutenberg_blocks[0].get("plannerProfile")
                if planner_profile:
                    return planner_profile

        except json.JSONDecodeError as e:
            logging.warning(f"Failed to parse JSON: {e}")
            continue

    logging.error("plannerProfile not found in HTML")
    return None

def get_profile_by_name(profiles: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    """Find a profile by name (case-insensitive)."""
    for profile in profiles:
        profile_name = profile.get("name", "").lower()
        if name.lower() in profile_name:
            return profile
    return None

def extract_equipment(profile: Dict[str, Any], items_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Extract equipment with aspects from profile."""
    equipment = {}
    profile_items = profile.get("items", {})

    for slot_str, item_idx in profile_items.items():
        slot_num = int(slot_str)

        # Skip non-equipment slots (talismans, etc.)
        if slot_num >= 20:
            continue

        item = items_map.get(str(item_idx), {})
        if not item:
            continue

        item_id = item.get("id", "")
        item_name = item.get("name", "Unknown")

        # Get slot name
        slot_name = SLOT_NAME_MAP.get(slot_num, f"Slot {slot_num}")

        # Get aspect
        aspect = item.get("aspect", {})
        aspect_name = ""
        if isinstance(aspect, dict):
            aspect_name = aspect.get("name", "") or aspect.get("id", "")

        # Collect affixes (for reference)
        affixes = []
        for affix in item.get("explicits", []):
            if isinstance(affix, dict):
                affixes.append(affix.get("name", "") or affix.get("nid", ""))

        equipment[slot_name] = {
            "name": item_name,
            "id": item_id,
            "aspect": aspect_name,
            "affixes": affixes
        }

    return equipment

def extract_skills(profile: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extract skills from profile."""
    skills = {}

    # Try different possible keys for skills
    skill_sources = [
        "skills",
        "activeSkills",
        "skillTrees",
        "activeSkillTrees"
    ]

    for source in skill_sources:
        skill_data = profile.get(source, {})
        if skill_data:
            break

    if isinstance(skill_data, dict):
        for slot, skill_info in skill_data.items():
            if isinstance(skill_info, dict):
                skills[slot] = {
                    "name": skill_info.get("name", ""),
                    "id": skill_info.get("id", ""),
                    "rank": skill_info.get("rank", 0),
                    "glyph": skill_info.get("glyph", "")
                }
            elif isinstance(skill_info, list):
                # Handle array of skills
                for skill in skill_info:
                    if isinstance(skill, dict):
                        skills[slot] = {
                            "name": skill.get("name", ""),
                            "id": skill.get("id", ""),
                            "rank": skill.get("rank", 0)
                        }

    return skills

def extract_gems(profile: Dict[str, Any], items_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Extract gems from profile and items."""
    gems = {}

    # Check profile-level gems
    profile_gems = profile.get("gems", {})
    if isinstance(profile_gems, dict):
        for slot, gem_info in profile_gems.items():
            if isinstance(gem_info, dict):
                gems[f"Gem {slot}"] = {
                    "name": gem_info.get("name", ""),
                    "type": gem_info.get("type", ""),
                    "rank": gem_info.get("rank", 0)
                }

    # Check gems in items (socketed gems)
    profile_items = profile.get("items", {})
    for slot_str, item_idx in profile_items.items():
        item = items_map.get(str(item_idx), {})
        item_gems = item.get("gems", [])

        for i, gem in enumerate(item_gems):
            if isinstance(gem, dict):
                slot_name = f"{SLOT_NAME_MAP.get(int(slot_str), slot_str)} Gem {i+1}"
                gems[slot_name] = {
                    "name": gem.get("name", ""),
                    "type": gem.get("type", ""),
                    "rank": gem.get("rank", 0)
                }

    return gems

def extract_paragon(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract paragon board data from profile."""
    paragon_data = profile.get("paragon", {})
    boards = []

    # Try different possible structures
    if isinstance(paragon_data, dict):
        # Structure 1: paragon.boards
        raw_boards = paragon_data.get("boards", [])

        # Structure 2: paragon.board
        if not raw_boards:
            raw_board = paragon_data.get("board", {})
            if raw_board:
                raw_boards = [raw_board]

        for board in raw_boards:
            if not isinstance(board, dict):
                continue

            board_info = {
                "name": board.get("name", "Unknown Board"),
                "glyphs": [],
                "nodes": [],
                "stats": {}
            }

            # Extract glyphs
            glyphs = board.get("glyphs", [])
            for glyph in glyphs:
                if isinstance(glyph, dict):
                    board_info["glyphs"].append({
                        "name": glyph.get("name", ""),
                        "id": glyph.get("id", ""),
                        "level": glyph.get("level", 0)
                    })

            # Extract nodes (for board visualization)
            nodes = board.get("nodes", [])
            for node in nodes:
                if isinstance(node, dict):
                    board_info["nodes"].append({
                        "id": node.get("id", ""),
                        "name": node.get("name", ""),
                        "type": node.get("type", ""),
                        "x": node.get("x", 0),
                        "y": node.get("y", 0)
                    })

            # Extract stats
            stats = board.get("stats", {})
            if isinstance(stats, dict):
                board_info["stats"] = {
                    stat_id: {
                        "value": value,
                        "name": stat_id  # Will be mapped later if needed
                    }
                    for stat_id, value in stats.items()
                }

            boards.append(board_info)

    return boards

def extract_build_version(profile: Dict[str, Any], items_map: Dict[str, Any]) -> Dict[str, Any]:
    """Extract all data for a single build version."""
    return {
        "name": profile.get("name", "Unknown"),
        "equipment": extract_equipment(profile, items_map),
        "aspects": {
            slot: info["aspect"]
            for slot, info in extract_equipment(profile, items_map).items()
            if info.get("aspect")
        },
        "skills": extract_skills(profile),
        "gems": extract_gems(profile, items_map),
        "paragon": extract_paragon(profile)
    }

def scrape_build(url: str) -> Dict[str, Any]:
    """
    Main scraping function.
    Extracts all build versions from a maxroll.gg guide.
    """
    logging.info(f"Scraping build from: {url}")

    # Fetch HTML
    html = fetch_page(url)
    if not html:
        return {"error": "Failed to fetch page"}

    # Extract planner profile
    planner_profile = extract_planner_profile(html)
    if not planner_profile:
        return {"error": "plannerProfile not found"}

    # Get data and items
    data = planner_profile.get("data", {})
    if isinstance(data, str):
        data = json.loads(data)

    items_map = data.get("items", {})
    profiles = data.get("profiles", [])

    # Define target versions (in order of priority)
    target_versions = [
        "Starter",
        "Midgame",
        "Endgame",
        "Endgame Mythic Seal"
    ]

    builds = {}

    # Extract all available profiles
    for profile in profiles:
        profile_name = profile.get("name", "")

        # Check if this profile matches any target version
        matched_version = None
        for version in target_versions:
            if version.lower() in profile_name.lower():
                matched_version = version
                break

        # If no specific version matched, use the profile name
        if not matched_version:
            matched_version = profile_name or f"Profile_{len(builds) + 1}"

        # Extract build data for this version
        build_data = extract_build_version(profile, items_map)
        builds[matched_version] = build_data

        logging.info(f"Extracted version: {matched_version} ({profile_name})")

    # If no profiles found, try to use the first one as default
    if not builds and profiles:
        build_data = extract_build_version(profiles[0], items_map)
        builds["Default"] = build_data
        logging.warning("No version names matched, using default profile")

    return {
        "url": url,
        "build_name": url.split("/")[-1].replace("-guide", "").replace("-build", ""),
        "versions": builds
    }

def save_to_json(data: Dict[str, Any], output_path: Path) -> None:
    """Save scraped data to JSON file."""
    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Data saved to {output_path}")
    except Exception as e:
        logging.error(f"Failed to save data: {e}")

def main():
    """Main entry point."""
    # Scrape the build
    build_data = scrape_build(MAXROLL_URL)

    # Save to file
    save_to_json(build_data, OUTPUT_FILE)

    # Print summary
    print("\n" + "="*50)
    print("SCRAPING COMPLETE")
    print("="*50)
    print(f"Build: {build_data.get('build_name', 'Unknown')}")
    print(f"Versions found: {list(build_data.get('versions', {}).keys())}")

    for version, data in build_data.get("versions", {}).items():
        print(f"\n--- {version} ---")
        print(f"Equipment: {len(data.get('equipment', {}))} items")
        print(f"Aspects: {len(data.get('aspects', {}))} items")
        print(f"Skills: {len(data.get('skills', {}))} skills")
        print(f"Gems: {len(data.get('gems', {}))} gems")
        print(f"Paragon boards: {len(data.get('paragon', []))} boards")

if __name__ == "__main__":
    main()