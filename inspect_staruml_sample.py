import json
from collections import Counter
from pathlib import Path

p = Path(r"C:\Users\user\Documents\pfe project\UMLExample.mdj")
data = json.loads(p.read_text(encoding="utf-8"))


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


seq = next(o for o in walk(data) if o.get("_type") == "UMLSequenceDiagram")
act = next(o for o in walk(data) if o.get("_type") == "UMLActivityDiagram")
print("seq", seq.get("name"), Counter(v.get("_type") for v in seq.get("ownedViews", [])))
print("act", act.get("name"), Counter(v.get("_type") for v in act.get("ownedViews", [])))
for t in [
    "UMLLifeline",
    "UMLMessage",
    "UMLAction",
    "UMLInitialNode",
    "UMLActivityFinalNode",
    "UMLDecisionNode",
    "UMLControlFlow",
]:
    xs = [o for o in walk(data) if o.get("_type") == t]
    print(t, len(xs), [(x.get("name"), x.get("_id")) for x in xs[:10]])
