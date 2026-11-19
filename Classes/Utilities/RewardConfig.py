# Einstellungen für Belohnungen und Shop.
# Speicherort: Classes/Utilities/RewardConfig.py

# ---------------- Belohnung nach jedem Kampf ----------------
EXP_PER_BATTLE = 300         # XP für den Weltenpfad (Stufen: exp_levels.csv)
TROPHIES_PER_BATTLE = 20     # Trophäen für die Trophy League
GEMS_PER_BATTLE = 100        # Diamanten (resources[0])

COINS_RESOURCE_ID = 1        # Gold (resources.csv), Obergrenze 500000
COINS_PER_BATTLE = 1000

ORBS_RESOURCE_ID = 4         # "UnlockTokens" = Orbs, Obergrenze 150
ORBS_PER_BATTLE = 10

COSMETIC_RESOURCE_ID = 12    # Skins und Pins kosten Cosmetic
COSMETIC_PER_BATTLE = 500    # 0 = aus

# Notfall-Obergrenzen, falls resources.csv nicht gefunden wird
RESOURCE_CAPS = {1: 500000, 4: 150}

# Charaktere = Zeilennummer in characters.csv: Witch 6, Medic 19, Barbarian King 52
BONUS_MEMBER_IDS = [6, 19, 52]

# ---------------- Shop ----------------
SHOP_ENABLED = True          # False = der alte Shop aus offers.json
SHOP_REFRESH_HOURS = 24      # Angebote wechseln alle X Stunden
SHOP_SKINS_TOTAL = 6         # Skin-Plätze insgesamt
SHOP_SKINS_TOP = 2           # davon für die meistgespielten Charaktere (Rest zufällig)
SHOP_COIN_SLOTS = 3          # Münz-Angebote (Gold, gratis)
SHOP_ELIXIR_SLOTS = 3        # Elixir-Angebote (kosten Diamanten), Feld "Elixir"
SHOP_PIN_SLOTS = 4           # Pins

SHOP_PIN_CATEGORY = "special"  # in welchem Shop-Bereich die Pins erscheinen: special / i / e / s

SKIN_CLASS_BASE = 5500000    # bestätigt durch Command 535 im Log
EMOTE_CLASS_BASE = 4200000   # bestätigt durch Command 536 im Log (Pins)
COUNT_BLANK_ROWS = False     # bestätigt: Zeilen ohne Namen zählen nicht
