import json
import re

def load_privacy_badger_json(path):
    """
    Loads Privacy Badger's exported JSON file.
    Extracts only domains where heuristicAction == "block".
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    action_map = data.get("action_map", {})

    # Filter only domains with heuristicAction == "block"
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



def convert_json_to_pihole(input_path, output_path):
    domains = load_privacy_badger_json(input_path)
    regexes = [domain_to_pihole_regex(d) for d in domains]

    with open(output_path, "w", encoding="utf-8") as f:
        for r in regexes:
            f.write(r + "\n")

    print(f"Converted {len(domains)} blocked domains → {output_path}")


if __name__ == "__main__":
    convert_json_to_pihole("privacy_badger.json", "pihole_regex_list.txt")

