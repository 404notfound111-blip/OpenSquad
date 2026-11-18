# Baut den Shop pro Spieler: Skins (meistgespielte + zufällige), Münzen, Pins.
# Speicherort: Classes/Utilities/ShopGenerator.py
import random, time, traceback
from collections import defaultdict
from Classes.Utilities import GameData
from Classes.Utilities import RewardConfig as R

FREE_GOLD_DEALS = ["GoldSmallFree", "GoldMidFree", "GoldBigFree", "GoldHugeFree", "GoldEpicFree"]


def _rng(player) -> random.Random:
    """Gleicher Spieler + gleicher Zeitraum = gleiche Auswahl. Danach wechselt sie."""
    period = int(time.time() // (R.SHOP_REFRESH_HOURS * 3600))
    return random.Random(f"{player.accountID}:{period}")


def _ownedCharacterNames(player) -> set:
    names = set()
    for member in player.members:
        name = GameData.characterNameById(member.get("id", -1))
        if name:
            names.add(name)
    return names


def _topCharacterNames(player, rng) -> list:
    """Nach Spielhäufigkeit (used, lvl, pts). Bisher setzt nichts diese Werte,
    dann entscheidet bei Gleichstand der Zufall."""
    scored = []
    for member in player.members:
        name = GameData.characterNameById(member.get("id", -1))
        if name:
            score = (member.get("used", 0), member.get("lvl", 0), member.get("pts", 0))
            scored.append((score, rng.random(), name))
    scored.sort(reverse=True)
    return [name for _, _, name in scored]


def _skinOffer(index: int, skinIdx: int, row: dict) -> dict:
    rarity = row.get("Rarity")
    price = int(row["CosmeticPrice"]) if row.get("CosmeticPrice") else (1500 if rarity == "1" else 2000)
    return {
        "index": index, "cost": price, "amount": 1,
        "offerID": GameData.dealIndex("SkinRare" if rarity == "1" else "SkinEpic"),
        "itemID": R.SKIN_CLASS_BASE + skinIdx,
        "resourceID": R.COSMETIC_RESOURCE_ID,
    }


def _pickSkins(player, rng) -> list:
    ownedChars = _ownedCharacterNames(player)
    ownedSkins = set(player.skins) | {s - R.SKIN_CLASS_BASE for s in player.skins}
    candidates = [
        (idx, row) for idx, row in GameData.namedRows("skins.csv")
        if row.get("Rarity") in ("1", "2")
        and (row.get("Disabled") or "").upper() != "TRUE"
        and row.get("Character") in ownedChars
        and idx not in ownedSkins
    ]
    byChar = defaultdict(list)
    for idx, row in candidates:
        byChar[row["Character"]].append((idx, row))

    chosen = []
    for name in _topCharacterNames(player, rng):          # meistgespielte zuerst, je 1 Skin
        if len(chosen) >= R.SHOP_SKINS_TOP:
            break
        if byChar.get(name):
            chosen.append(rng.choice(byChar[name]))

    rest = [c for c in candidates if c not in chosen]       # der Rest zufällig
    rng.shuffle(rest)
    chosen += rest[: max(0, R.SHOP_SKINS_TOTAL - len(chosen))]
    return chosen


def _pickPins(player, rng) -> list:
    if R.EMOTE_CLASS_BASE is None:
        return []
    ownedChars = _ownedCharacterNames(player)
    ownedEmotes = {e.get("id") for e in player.emotes}
    candidates = [
        (idx, row) for idx, row in GameData.namedRows("emotes.csv")
        if row.get("Character") in ownedChars
        and (row.get("Disabled") or "").upper() != "TRUE"
        and idx not in ownedEmotes
    ]
    rng.shuffle(candidates)
    return candidates[: R.SHOP_PIN_SLOTS]


def _pickCoins(rng) -> list:
    deals = dict((row.get("Name"), (idx, row)) for idx, row in GameData.namedRows("deals.csv"))
    names = [n for n in FREE_GOLD_DEALS if n in deals]
    rng.shuffle(names)
    return [deals[n] for n in names[: R.SHOP_COIN_SLOTS]]


def buildOffers(player, fallback: dict) -> dict:
    """Gibt die Angebote für dieses Home-Paket zurück. Bei Fehlern der alte Shop (fallback)."""
    if not R.SHOP_ENABLED:
        return fallback
    try:
        rng = _rng(player)
        counter = 0
        coins, pins, skins = [], [], []

        for idx, row in _pickCoins(rng):                    # Reihenfolge wie in LogicShopEntry: i, e, s
            coins.append({"index": counter, "cost": 0, "amount": int(row.get("ValueForExpLeague") or 100),
                          "offerID": idx, "itemID": 0, "resourceID": 1})
            counter += 1

        for idx, row in _pickPins(player, rng):
            rare = row.get("Rarity") == "1"
            pins.append({"index": counter, "cost": 40 if rare else 20, "amount": 1,
                         "offerID": GameData.dealIndex("EmoteRare" if rare else "EmoteCommon"),
                         "itemID": R.EMOTE_CLASS_BASE + idx, "resourceID": R.COSMETIC_RESOURCE_ID})
            counter += 1

        for idx, row in _pickSkins(player, rng):
            skins.append(_skinOffer(counter, idx, row))
            counter += 1

        return {"special": [], "i": coins, "e": pins, "s": skins}
    except Exception:
        traceback.print_exc()
        print("[ShopGenerator::] Fehler, es wird der alte Shop benutzt")
        return fallback
