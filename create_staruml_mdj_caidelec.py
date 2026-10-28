import json
import shutil
import uuid
from pathlib import Path


BASE = Path(r"C:\Users\user\Documents\pfe project")
OUT = BASE / "staruml_caidelec"
OUT.mkdir(exist_ok=True)

CLASS_SOURCE = Path(r"C:\Users\user\Desktop\UML CAIDELAC\CAIDELEC_Class_Diagram_StarUML.mdj")
USECASE_SOURCE = Path(r"C:\Users\user\Downloads\CAIDELEC_Use_Case_StarUML_FINAL_ARRANGE.mdj")


def sid(prefix):
    return f"{prefix}_{uuid.uuid4().hex}"


def ref(x):
    return {"$ref": x}


def edge_label(parent, model, text, x, y, visible=True):
    label_id = sid("label")
    return {
        "_type": "EdgeLabelView",
        "_id": label_id,
        "_parent": ref(parent),
        "model": ref(model),
        "visible": visible,
        "font": "Arial;13;0",
        "left": x,
        "top": y,
        "width": max(30, len(text) * 7),
        "height": 16,
        "alpha": 1.5707963267948966,
        "distance": 10,
        "edgePosition": 1,
        "text": text,
    }


def line_view(parent, model, x, top, h):
    lid = sid("line")
    return {
        "_type": "UMLLinePartView",
        "_id": lid,
        "_parent": ref(parent),
        "model": ref(model),
        "font": "Arial;13;0",
        "left": x,
        "top": top,
        "width": 1,
        "height": h,
    }


def name_comp(parent, model, text, x, y, w):
    comp = sid("namecomp")
    labels = []
    for name, visible, yy, value in [
        ("stereotypeLabel", False, y - 14, ""),
        ("nameLabel", True, y + 8, text),
        ("namespaceLabel", False, y + 24, ""),
        ("propertyLabel", False, y + 24, ""),
    ]:
        lid = sid("label")
        labels.append((name, lid, {
            "_type": "LabelView",
            "_id": lid,
            "_parent": ref(comp),
            "model": ref(model),
            "visible": visible,
            "font": "Arial;13;1" if name == "nameLabel" else "Arial;13;0",
            "left": x,
            "top": yy,
            "width": w,
            "height": 16,
            "text": value,
            "horizontalAlignment": 2,
            "verticalAlignment": 5,
        }))
    obj = {
        "_type": "UMLNameCompartmentView",
        "_id": comp,
        "_parent": ref(parent),
        "model": ref(model),
        "subViews": [v for _, _, v in labels],
        "font": "Arial;13;0",
        "left": x,
        "top": y,
        "width": w,
        "height": 40,
    }
    for name, lid, _ in labels:
        obj[name] = ref(lid)
    return obj


def sequence_mdj():
    project = sid("project")
    model = sid("model")
    interaction = sid("interaction")
    diagram = sid("diagram")

    lifeline_specs = [
        ("Employe", 120),
        ("Frontend React", 360),
        ("API FastAPI", 630),
        ("Service Frais", 900),
        ("SQLite", 1170),
        ("Admin", 1440),
    ]
    lifelines = []
    views = []
    line_ids = {}
    for name, x in lifeline_specs:
        life = sid("lifeline")
        lifelines.append({"_type": "UMLLifeline", "_id": life, "_parent": ref(interaction), "name": name})
        view = sid("lifelineview")
        comp = name_comp(view, life, name, x - 70, 40, 140)
        line = line_view(view, life, x, 80, 860)
        line_ids[name] = line["_id"]
        views.append({
            "_type": "UMLSeqLifelineView",
            "_id": view,
            "_parent": ref(diagram),
            "model": ref(life),
            "subViews": [comp, line],
            "font": "Arial;13;0",
            "left": x - 70,
            "top": 40,
            "width": 140,
            "height": 900,
            "nameCompartment": ref(comp["_id"]),
            "linePart": ref(line["_id"]),
        })

    messages = [
        ("Employe", "Frontend React", "Saisir frais + justificatif", 160, "synchCall"),
        ("Frontend React", "API FastAPI", "POST /expenses", 230, "synchCall"),
        ("API FastAPI", "Service Frais", "Verifier droits", 300, "synchCall"),
        ("Service Frais", "SQLite", "Chercher intervention", 370, "synchCall"),
        ("SQLite", "Service Frais", "employee_id", 440, "reply"),
        ("Service Frais", "SQLite", "Enregistrer frais", 520, "synchCall"),
        ("SQLite", "Service Frais", "Frais cree", 590, "reply"),
        ("Service Frais", "API FastAPI", "201 Created / 403 Forbidden", 660, "reply"),
        ("API FastAPI", "Frontend React", "Confirmation ou erreur", 730, "reply"),
        ("Frontend React", "Employe", "Afficher statut", 800, "reply"),
        ("Admin", "Frontend React", "Consulter frais", 870, "synchCall"),
    ]
    msg_models = []
    for src, dst, name, y, kind in messages:
        mid = sid("message")
        msg_models.append({
            "_type": "UMLMessage",
            "_id": mid,
            "_parent": ref(interaction),
            "name": name,
            "source": ref(next(l["_id"] for l in lifelines if l["name"] == src)),
            "target": ref(next(l["_id"] for l in lifelines if l["name"] == dst)),
            "messageSort": kind,
        })
        view_id = sid("messageview")
        x1 = dict(lifeline_specs)[src]
        x2 = dict(lifeline_specs)[dst]
        lbl = edge_label(view_id, mid, name, min(x1, x2) + 12, y - 24)
        views.append({
            "_type": "UMLSeqMessageView",
            "_id": view_id,
            "_parent": ref(diagram),
            "model": ref(mid),
            "subViews": [lbl],
            "font": "Arial;13;0",
            "head": ref(line_ids[dst]),
            "tail": ref(line_ids[src]),
            "points": f"{x1}:{y};{x2}:{y}",
            "nameLabel": ref(lbl["_id"]),
        })

    diagram_obj = {
        "_type": "UMLSequenceDiagram",
        "_id": diagram,
        "_parent": ref(interaction),
        "name": "03 - Sequence - Declaration et verification des frais",
        "visible": True,
        "defaultDiagram": True,
        "ownedViews": views,
    }
    interaction_obj = {
        "_type": "UMLInteraction",
        "_id": interaction,
        "_parent": ref(model),
        "name": "Declaration et verification des frais",
        "participants": lifelines,
        "messages": msg_models,
        "ownedElements": [diagram_obj],
    }
    return {
        "_type": "Project",
        "_id": project,
        "name": "CAIDELEC - Sequence Diagram",
        "ownedElements": [{
            "_type": "UMLModel",
            "_id": model,
            "_parent": ref(project),
            "name": "CAIDELEC",
            "ownedElements": [interaction_obj],
        }],
    }


def activity_node(node_type, parent, name):
    return {"_type": node_type, "_id": sid("node"), "_parent": ref(parent), "name": name}


def activity_view(view_type, diagram, model, x, y, w=260, h=60):
    view = sid("view")
    comp = name_comp(view, model, "", x, y, w)
    comp["subViews"][1]["text"] = ""
    obj = {
        "_type": view_type,
        "_id": view,
        "_parent": ref(diagram),
        "model": ref(model),
        "font": "Arial;13;0",
        "left": x,
        "top": y,
        "width": w,
        "height": h,
    }
    if view_type == "UMLActionView":
        comp = name_comp(view, model, "", x, y + 18, w)
        obj["subViews"] = [comp]
        obj["nameCompartment"] = ref(comp["_id"])
    return obj


def activity_mdj():
    project = sid("project")
    model = sid("model")
    activity = sid("activity")
    diagram = sid("diagram")
    specs = [
        ("UMLInitialNode", "Debut", 740, 60, "UMLInitialNodeView"),
        ("UMLAction", "Ouvrir application", 600, 160, "UMLActionView"),
        ("UMLAction", "Saisir identifiants", 600, 260, "UMLActionView"),
        ("UMLAction", "Verifier login", 600, 360, "UMLActionView"),
        ("UMLDecisionNode", "Identifiants valides ?", 640, 470, "UMLDecisionNodeView"),
        ("UMLAction", "Afficher erreur", 260, 470, "UMLActionView"),
        ("UMLDecisionNode", "Role admin ?", 640, 610, "UMLDecisionNodeView"),
        ("UMLAction", "Afficher dashboard", 250, 760, "UMLActionView"),
        ("UMLAction", "Gerer employes", 250, 860, "UMLActionView"),
        ("UMLAction", "Planifier interventions", 250, 960, "UMLActionView"),
        ("UMLAction", "Observer / verifier frais", 250, 1060, "UMLActionView"),
        ("UMLAction", "Exporter Excel", 250, 1160, "UMLActionView"),
        ("UMLAction", "Afficher espace employe", 980, 760, "UMLActionView"),
        ("UMLAction", "Consulter mes interventions", 980, 860, "UMLActionView"),
        ("UMLAction", "Declarer frais", 980, 960, "UMLActionView"),
        ("UMLAction", "Ajouter justificatif photo", 980, 1060, "UMLActionView"),
        ("UMLAction", "Consulter mes frais", 980, 1160, "UMLActionView"),
        ("UMLActivityFinalNode", "Fin", 740, 1340, "UMLActivityFinalNodeView"),
    ]
    nodes = []
    views = []
    for typ, name, x, y, vtyp in specs:
        n = activity_node(typ, activity, name)
        nodes.append(n)
        w, h = (280, 70)
        if "Initial" in typ or "Final" in typ:
            w, h = (60, 60)
        elif "Decision" in typ:
            w, h = (300, 90)
        views.append(activity_view(vtyp, diagram, n["_id"], x, y, w, h))

    diagram_obj = {
        "_type": "UMLActivityDiagram",
        "_id": diagram,
        "_parent": ref(activity),
        "name": "04 - Activite - Parcours utilisateur",
        "visible": True,
        "defaultDiagram": True,
        "ownedViews": views,
    }
    activity_obj = {
        "_type": "UMLActivity",
        "_id": activity,
        "_parent": ref(model),
        "name": "Parcours utilisateur CAIDELEC",
        "nodes": nodes,
        "ownedElements": [diagram_obj],
    }
    return {
        "_type": "Project",
        "_id": project,
        "name": "CAIDELEC - Activity Diagram",
        "ownedElements": [{
            "_type": "UMLModel",
            "_id": model,
            "_parent": ref(project),
            "name": "CAIDELEC",
            "ownedElements": [activity_obj],
        }],
    }


def main():
    if CLASS_SOURCE.exists():
        shutil.copy2(CLASS_SOURCE, OUT / "02_CAIDELEC_Class_Diagram_StarUML.mdj")
    if USECASE_SOURCE.exists():
        shutil.copy2(USECASE_SOURCE, OUT / "01_CAIDELEC_Use_Case_Diagram_StarUML.mdj")
    (OUT / "03_CAIDELEC_Sequence_Diagram_StarUML.mdj").write_text(
        json.dumps(sequence_mdj(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (OUT / "04_CAIDELEC_Activity_Diagram_StarUML.mdj").write_text(
        json.dumps(activity_mdj(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(OUT)


if __name__ == "__main__":
    main()
