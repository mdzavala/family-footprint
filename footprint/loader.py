"""Load the synthetic 'internet' (world) and family files.

A world directory can hold any number of *.json files; their lists are merged.
This is how organizers add the hidden holdout data at judging time.
"""
import json
import pathlib

WORLD_KEYS = ["places", "breaches", "profiles", "posts", "photos", "brokers"]


def load_world(*dirs):
    world = {k: [] for k in WORLD_KEYS}
    for d in dirs:
        for path in sorted(pathlib.Path(d).glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            for k in WORLD_KEYS:
                world[k].extend(data.get(k, []))
    world["index"] = {rec["id"]: rec for k in WORLD_KEYS for rec in world[k]}
    return world


def load_family(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
