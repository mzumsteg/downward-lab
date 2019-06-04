# -*- coding: utf-8 -*-

DOMAIN_GROUPS = {
    "airport": ["airport"],
    "barman": ["barman-opt11-strips", "barman-opt14-strips"],
    "blocks": ["blocks"],
    "childsnack": ["childsnack-opt14-strips"],
    "depot": ["depot"],
    "driverlog": ["driverlog"],
    "elevators": ["elevators-opt08-strips", "elevators-opt11-strips"],
    "floortile": ["floortile-opt11-strips", "floortile-opt14-strips"],
    "freecell": ["freecell"],
    "ged": ["ged-opt14-strips"],
    "grid": ["grid"],
    "gripper": ["gripper"],
    "hiking": ["hiking-opt14-strips"],
    "logistics": ["logistics98", "logistics00"],
    "miconic": ["miconic"],
    "movie": ["movie"],
    "mprime": ["mprime"],
    "mystery": ["mystery"],
    "nomystery": ["nomystery-opt11-strips"],
    "openstacks": ["openstacks-strips", "openstacks-opt08-strips", "openstacks-opt11-strips", "openstacks-opt14-strips"],
    "parcprinter": ["parcprinter-08-strips", "parcprinter-opt11-strips"],
    "parking": ["parking-opt11-strips", "parking-opt14-strips"],
    "pathways": ["pathways-noneg"],
    "pegsol": ["pegsol-08-strips", "pegsol-opt11-strips"],
    "pipes-nt": ["pipesworld-notankage"],
    "pipes-t": ["pipesworld-tankage"],
    "psr-small": ["psr-small"],
    "rovers": ["rovers"],
    "satellite": ["satellite"],
    "scanalyzer": ["scanalyzer-08-strips", "scanalyzer-opt11-strips"],
    "sokoban": ["sokoban-opt08-strips", "sokoban-opt11-strips"],
    "storage": ["storage"],
    "tetris": ["tetris-opt14-strips"],
    "tidybot": ["tidybot-opt11-strips", "tidybot-opt14-strips"],
    "tpp": ["tpp"],
    "transport": ["transport-opt08-strips", "transport-opt11-strips", "transport-opt14-strips"],
    "trucks": ["trucks-strips"],
    "visitall": ["visitall-opt11-strips", "visitall-opt14-strips"],
    "woodwork": ["woodworking-opt08-strips", "woodworking-opt11-strips"],
    "zenotravel": ["zenotravel"],
    # IPC 2018:
    "agricola": ["agricola", "agricola-opt18-strips"],
    "data-network": ["data-network", "data-network-opt18-strips"],
    "organic-split": ["organic-synthesis-split", "organic-synthesis-split-opt18-strips"],
    "organic" : ["organic-synthesis", "organic-synthesis-opt18-strips"],
    "petri-net": ["petri-net-alignment", "petri-net-alignment-opt18-strips"],
    "snake": ["snake", "snake-opt18-strips"],
    "spider": ["spider", "spider-opt18-strips"],
    "termes": ["termes", "termes-opt18-strips"],
}

DOMAIN_RENAMINGS = {}
for group_name, domains in DOMAIN_GROUPS.items():
    for domain in domains:
        DOMAIN_RENAMINGS[domain] = group_name

def group_domains(run):
    old_domain = run["domain"]
    run["domain"] = DOMAIN_RENAMINGS[old_domain]
    run["problem"] = old_domain + "-" + run["problem"]
    return run
