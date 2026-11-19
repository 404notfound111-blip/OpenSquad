# Liest die Spieldaten-CSV-Dateien aus dem Ordner GameData im Projektordner.
# Speicherort: Classes/Utilities/GameData.py
import csv, os

_BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "GameData"))
_cache: dict = {}

MILESTONE_BASE = 4700000  # Meilenstein-ID = 4700000 + Zeile in exp_milestones.csv


def _rows(name: str) -> list:
    if name in _cache:
        return _cache[name]
    rows = []
    try:
        with open(os.path.join(_BASE, name), encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))[1:]  # erste Zeile nach der Kopfzeile ist die Typzeile
    except OSError:
        print(f"[GameData::] {name} nicht gefunden in {_BASE}")
    _cache[name] = rows
    return rows


def _indexByName(csvName: str, name: str):
    for i, row in enumerate(_rows(csvName)):
        if row.get("Name") == name:
            return i
    return None


def resourceIdByName(name: str):
    return _indexByName("resources.csv", name)


def characterIdByName(name: str):
    return _indexByName("characters.csv", name)


def characterNameById(characterID: int):
    rows = _rows("characters.csv")
    if 0 <= characterID < len(rows):
        return rows[characterID].get("Name")
    return None


def resourceCap(resourceID: int):
    rows = _rows("resources.csv")
    if 0 <= resourceID < len(rows):
        value = rows[resourceID].get("MaxCapacity")
        if value:
            try:
                return int(value)
            except ValueError:
                return None
    return None


def milestoneReward(milestoneID: int):
    """Gibt {"resource": Name, "amount": int, "character": Name} zurück (Felder können leer sein)."""
    rows = _rows("exp_milestones.csv")
    i = milestoneID - MILESTONE_BASE
    if not 0 <= i < len(rows):
        return None
    row = rows[i]
    amount = row.get("ResourceAmount") or "0"
    return {
        "resource": row.get("Resource") or "",
        "amount": int(amount) if amount.isdigit() else 0,
        "character": row.get("Character") or "",
    }


def namedRows(csvName: str) -> list:
    """[(Index, Zeile)] nur für Zeilen mit Namen. Zeilen ohne Namen sind Fortsetzungen
    der Zeile davor und zählen nicht mit (außer RewardConfig.COUNT_BLANK_ROWS = True)."""
    from Classes.Utilities import RewardConfig as R
    result, count = [], 0
    for raw, row in enumerate(_rows(csvName)):
        if row.get("Name"):
            result.append((raw if R.COUNT_BLANK_ROWS else count, row))
            count += 1
    return result


def dealIndex(dealName: str) -> int:
    for idx, row in namedRows("deals.csv"):
        if row.get("Name") == dealName:
            return idx
    return 0


def dealRow(dealName: str) -> dict:
    for idx, row in namedRows("deals.csv"):
        if row.get("Name") == dealName:
            return row
    return {}


# ---- XP-Stufen (exp_levels.csv: Name = Stufe, ExpToNextLevel) ----
def expToNextLevel(level: int) -> int:
    for row in _rows("exp_levels.csv"):
        if row.get("Name") == str(level):
            try:
                return int(row.get("ExpToNextLevel") or 0)
            except ValueError:
                return 500
    return 500


def maxExpLevel() -> int:
    levels = [int(r["Name"]) for r in _rows("exp_levels.csv") if (r.get("Name") or "").isdigit()]
    return max(levels) if levels else 100


# ---- Skinpreis ----
def skinPrice(skinIdx: int) -> int:
    for idx, row in namedRows("skins.csv"):
        if idx == skinIdx:
            if row.get("CosmeticPrice"):
                try:
                    return int(row["CosmeticPrice"])
                except ValueError:
                    pass
            return {"1": 1500, "2": 2000}.get(row.get("Rarity"), 1000)
    return 1000
