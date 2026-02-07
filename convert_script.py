import json
import re
import os

def load_privacy_badger_json(path):
    """
    Loads Privacy Badger's exported JSON file.
    Extracts only domains where:
      heuristicAction == "block"
      OR userAction == "block"
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
    """
    Convert a domain into a Pi-hole Adblock-style rule:
    ||example.com^
    """
    return rf"||{domain}^"


def load_list_file(path):
    """
    Loads a list file (regex list or whitelist).
    Removes comments and blank lines.
    """
    if not os.path.exists(path):
        return set()

    entries = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            entries.add(line)

    return entries


def convert_json_to_pihole(input_path, output_path, whitelist_path):
    # Load PB domains
    pb_domains = load_privacy_badger_json(input_path)
    pb_regexes = {domain_to_pihole_regex(d) for d in pb_domains}

    # Load existing Pi-hole list
    existing_regexes = load_list_file(output_path)

    # Load whitelist
    whitelist = load_list_file(whitelist_path)

    # --- FULL SYNC LOGIC ---
    still_blocked = existing_regexes.intersection(pb_regexes)
    new_entries = pb_regexes - existing_regexes

    merged = still_blocked.union(new_entries)

    # --- APPLY WHITELIST ---
    cleaned = merged - whitelist

    # Write back sorted
    with open(output_path, "w", encoding="utf-8") as f:
        for r in sorted(cleaned):
            f.write(r + "\n")

    print(f"Existing entries kept: {len(still_blocked)}")
    print(f"New entries added: {len(new_entries)}")
    print(f"Removed (no longer blocked): {len(existing_regexes - pb_regexes)}")
    print(f"Whitelist removals: {len(merged - cleaned)}")
    print(f"Total entries written: {len(cleaned)} → {output_path}")


if __name__ == "__main__":
    convert_json_to_pihole(
        "privacy_badger.json",
        "pihole_regex_list.txt",
        "whitelist.txt"
    )
