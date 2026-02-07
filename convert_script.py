""" This code is built with help of Microsoft Copilot. """

import json
import re
import os

def load_privacy_badger_json(path):
    """
    Loads Privacy Badger's exported JSON file.
    Extracts only domains where:
      heuristicAction == "block"
      AND userAction == "block"
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    action_map = data.get("action_map", {})

    blocked_domains = [
        domain
        for domain, info in action_map.items()
        if info.get("heuristicAction") == "block"
        or info.get("userAction") == "block"
    ]

    return blocked_domains


def domain_to_pihole_regex(domain):
    r"""
    Convert a domain into a Pi-hole regex:
    (^|\.)(example\.com)$
    """
    escaped = re.escape(domain)
    return rf"(^|\.){escaped}$"


def load_existing_pihole_list(path):
    """
    Loads an existing Pi-hole regex list.
    Removes comments and blank lines.
    """
    if not os.path.exists(path):
        return []

    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            entries.append(line)

    return entries


def convert_json_to_pihole(input_path, output_path):
    # Load PB domains
    pb_domains = load_privacy_badger_json(input_path)
    pb_regexes = {domain_to_pihole_regex(d) for d in pb_domains}

    # Load existing Pi-hole list
    existing_regexes = set(load_existing_pihole_list(output_path))

    # --- FULL SYNC LOGIC ---
    # 1. Keep entries that are still blocked
    still_blocked = existing_regexes.intersection(pb_regexes)

    # 2. Add new entries
    new_entries = pb_regexes - existing_regexes

    # 3. Remove entries no longer blocked (implicitly done by not including them)
    merged = still_blocked.union(new_entries)

    # Write back sorted
    with open(output_path, "w", encoding="utf-8") as f:
        for r in sorted(merged):
            f.write(r + "\n")

    print(f"Existing entries kept: {len(still_blocked)}")
    print(f"New entries added: {len(new_entries)}")
    print(f"Removed (no longer blocked): {len(existing_regexes - pb_regexes)}")
    print(f"Total entries written: {len(merged)} → {output_path}")


if __name__ == "__main__":
    convert_json_to_pihole("privacy_badger.json", "pihole_regex_list.txt")
