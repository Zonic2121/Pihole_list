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
    print(f"New entries in EFF list: {len(pb_regexes)}")
    # Load existing Pi-hole list
    existing_regexes = load_list_file(output_path)
    print(f"Existing entries in list: {len(existing_regexes)}")

    # Load whitelist
    whitelist = load_list_file(whitelist_path)

    # --- FULL SYNC LOGIC ---
    still_blocked = existing_regexes.intersection(pb_regexes)
    print(f"New entries already in block list: {len(still_blocked)}")
    new_entries = pb_regexes - existing_regexes
    print(f"New entries to add to list: {len(new_entries)}")
    merged = existing_regexes.union(new_entries)
    print(f"Total entries before whitelist: {len(merged)}")
    # --- APPLY WHITELIST ---
    cleaned = merged - whitelist
    print(f"Whitelist entries: {len(whitelist)}")
    print(f"Whitelist removals from list: {len(merged - cleaned)}")

    # Write back sorted
    with open(output_path, "w", encoding="utf-8") as f:
        for r in sorted(cleaned):
            f.write(r + "\n")

    print(f"Total entries written: {len(cleaned)} → {output_path}")


if __name__ == "__main__":
    convert_json_to_pihole(
        "privacy_badger.json",
        "local_list.txt",
        "whitelist.txt"
    )
