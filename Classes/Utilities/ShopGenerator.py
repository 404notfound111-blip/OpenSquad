# Baut den Shop pro Spieler: Skins (meistgespielte + zufällige), Münzen, Elixir, Pins.
# Speicherort: Classes/Utilities/ShopGenerator.py
import random, time, traceback
from collections import defaultdict
from Classes.Utilities import GameData
from Classes.Utilities import RewardConfig as R

FREE_GOLD_DEALS = ["GoldSmallFree", "GoldMidFree", "GoldBigFree", "GoldHugeFree", "GoldEpicFree"]
ELIXIR_DEALS = ["PowerPointsSmall", "PowerPointsMid", "PowerPointsBig", "PowerPointsHuge", "PowerPointsEpic"]


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
    """Nach Spielhäufigkeit/Level (used, lvl, pts). Der Server sieht nicht, welche Charaktere
    im Kampf gespielt werden; das Level aus den Upgrades ist der beste Hinweis, den er hat."""
    scored = []
    for member in player.members:
        name = GameData.characterNameById(member.get("id", -1))
        if name:
            score = (member.get("used", 0), member.get("lvl", 0), member.get("pts", 0))
            scored.append((score, rng.random(), name))
    scored.sort(reverse=True)
    return [name for _, _, name in scored]


def _skinOffer(index: int, skinIdx: int) -> dict:
    price = GameData.skinPrice(skinIdx)
    dealName = {1000: "SkinCommon", 1500: "SkinRare", 2000: "SkinEpic"}.get(price, "SkinCommon")
    return {
        "index": index, "cost": price, "amount": 1,
        "offerID": GameData.dealIndex(dealName),
        "itemID": R.SKIN_CLASS_BASE + skinIdx,
        "resourceID": R.COSMETIC_RESOURCE_ID,
    }


def _pickSkins(player, rng) -> list:
    ownedChars = _ownedCharacterNames(player)
    ownedSkins = set(player.skins) | {s - R.SKIN_CLASS_BASE for s in player.skins}
    candidates = [
        (idx, row) for idx, row in GameData.namedRows("skins.csv")
        if (row.get("CosmeticPrice") or row.get("Rarity") in ("1", "2"))   # Standard-Skins haben keinen Preis
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
    ownedPins = set(player.pins) | {p - R.EMOTE_CLASS_BASE for p in player.pins}
    candidates = [
        (idx, row) for idx, row in GameData.namedRows("emotes.csv")
        if row.get("Character") in ownedChars
        and (row.get("Disabled") or "").upper() != "TRUE"
        and idx not in ownedPins
    ]
    rng.shuffle(candidates)
    return candidates[: R.SHOP_PIN_SLOTS]


def _pickCoins(rng) -> list:
    deals = dict((row.get("Name"), (idx, row)) for idx, row in GameData.namedRows("deals.csv"))
    names = [n for n in FREE_GOLD_DEALS if n in deals]
    rng.shuffle(names)
    return [deals[n] for n in names[: R.SHOP_COIN_SLOTS]]


def _pickElixir(rng) -> list:
    deals = dict((row.get("Name"), (idx, row)) for idx, row in GameData.namedRows("deals.csv"))
    names = [n for n in ELIXIR_DEALS if n in deals]
    rng.shuffle(names)
    return [deals[n] for n in names[: R.SHOP_ELIXIR_SLOTS]]


def buildOffers(player, fallback: dict) -> dict:
    """Gibt die Angebote für dieses Home-Paket zurück. Bei Fehlern der alte Shop (fallback)."""
    if not R.SHOP_ENABLED:
        return fallback
    try:
        rng = _rng(player)
        shop = {"special": [], "i": [], "e": [], "s": []}
        pinCategory = getattr(R, "SHOP_PIN_CATEGORY", "special")
        counter = 0
        offers = []   # (Kategorie, Angebot) in der Reihenfolge, in der LogicShopEntry sie schreibt

        for idx, row in _pickPins(player, rng):
            rare = row.get("Rarity") == "1"
            offers.append((pinCategory, {"cost": 40 if rare else 20, "amount": 1,
                                         "offerID": GameData.dealIndex("EmoteRare" if rare else "EmoteCommon"),
                                         "itemID": R.EMOTE_CLASS_BASE + idx, "resourceID": R.COSMETIC_RESOURCE_ID}))

        for idx, row in _pickCoins(rng):
            offers.append(("i", {"cost": 0, "amount": int(row.get("ValueForExpLeague") or 100),
                                 "offerID": idx, "itemID": 0, "resourceID": 1}))

        for idx, row in _pickElixir(rng):
            offers.append(("e", {"cost": int(row.get("CostAmount") or 0),
                                 "amount": int(row.get("ValueForExpLeague") or 10),
                                 "offerID": idx, "itemID": 0, "resourceID": 0}))   # bezahlt mit Diamanten

        for idx, row in _pickSkins(player, rng):
            offers.append(("s", _skinOffer(0, idx)))

        order = {"special": 0, "i": 1, "e": 2, "s": 3}
        for category, offer in sorted(offers, key=lambda t: order.get(t[0], 9)):
            offer["index"] = counter
            counter += 1
            shop[category].append(offer)
        return shop
    except Exception:
        traceback.print_exc()
        print("[ShopGenerator::] Fehler, es wird der alte Shop benutzt")
        return fallback
