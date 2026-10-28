import json
import uuid
from pathlib import Path


BASE = Path(r"C:\Users\user\Documents\pfe project\staruml_caidelec_corrige_2026")


def sid(prefix):
    return f"{prefix}_{uuid.uuid4().hex}"


def ref(x):
    return {"$ref": x}


def patch_class():
    path = BASE / "02_CAIDELEC_Class_Diagram_StarUML.mdj"
    data = json.loads(path.read_text(encoding="utf-8"))
    model = data["ownedElements"][0]

    existing = {item.get("name") for item in model.get("ownedElements", [])}
    for class_name, attrs in [
        ("ReportService", [
            ("start_date", "date?"),
            ("end_date", "date?"),
            ("current_user", "User"),
        ]),
        ("ReportSummary", [
            ("total_expenses", "float"),
            ("interventions_count", "int"),
            ("expenses_by_employee", "list"),
            ("expenses_by_intervention", "list"),
        ]),
    ]:
        if class_name in existing:
            continue
        class_id = sid("class")
        model["ownedElements"].append({
            "_type": "UMLClass",
            "_id": class_id,
            "_parent": ref(model["_id"]),
            "name": class_name,
            "visibility": "public",
            "attributes": [
                {
                    "_type": "UMLAttribute",
                    "_id": sid("attr"),
                    "_parent": ref(class_id),
                    "name": name,
                    "visibility": "public",
                    "type": typ,
                    "isStatic": False,
                    "isLeaf": False,
                    "isReadOnly": False,
                    "isOrdered": False,
                    "isUnique": False,
                    "isDerived": False,
                    "aggregation": "none",
                    "isID": False,
                }
                for name, typ in attrs
            ],
            "isAbstract": False,
            "isFinalSpecialization": False,
            "isLeaf": False,
            "isActive": False,
        })

    data["name"] = "CAIDELEC - Class Diagram Corrige 2026"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def patch_usecase():
    path = BASE / "01_CAIDELEC_Use_Case_Diagram_StarUML.mdj"
    data = json.loads(path.read_text(encoding="utf-8"))
    model = data["ownedElements"][0]
    existing = {item.get("name") for item in model.get("ownedElements", [])}

    for name in ["Rapports statistiques", "Exporter CSV", "Mes rapports"]:
        if name not in existing:
            model["ownedElements"].append({
                "_type": "UMLUseCase",
                "_id": sid("usecase"),
                "_parent": ref(model["_id"]),
                "name": name,
                "visibility": "public",
            })

    data["name"] = "CAIDELEC - Use Case Diagram Corrige 2026"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    patch_class()
    patch_usecase()
    print(BASE)
