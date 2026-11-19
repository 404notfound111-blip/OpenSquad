# Einstellungen für Belohnungen nach einem Kampf.
# Speicherort: Classes/Utilities/RewardConfig.py

# XP für den Weltenpfad (Meilensteine brauchen Exp 2, 3, 4 ... 100 laut exp_milestones.csv)
EXP_PER_BATTLE = 3

# Diamanten ("Diamonds Count" im Home-Paket = resources[0])
GEMS_PER_BATTLE = 100

# Gold: Resource-ID 1 (laut resources.csv, Obergrenze 500000)
COINS_RESOURCE_ID = 1
COINS_PER_BATTLE = 1000

# Orbs = "UnlockTokens": Resource-ID 4 (laut resources.csv, Obergrenze 150)
ORBS_RESOURCE_ID = 4
ORBS_PER_BATTLE = 10

# Obergrenzen aus resources.csv (MaxCapacity). Diamanten haben keine.
RESOURCE_CAPS = {1: 500000, 4: 150}

# Charaktere = Zeilennummer in characters.csv: Witch 6, Medic 19, Barbarian King 52
BONUS_MEMBER_IDS = [6, 19, 52]

# ---------------- Shop ----------------
SHOP_ENABLED = True          # False = der alte Shop aus offers.json
SHOP_REFRESH_HOURS = 24      # Angebote wechseln alle X Stunden
SHOP_SKINS_TOTAL = 6         # Skin-Plätze insgesamt
SHOP_SKINS_TOP = 2           # davon für die meistgespielten Charaktere (Rest zufällig)
SHOP_COIN_SLOTS = 3          # Münz-Angebote (Gold, gratis)
SHOP_PIN_SLOTS = 4           # Pins (Emotes); nur aktiv, wenn EMOTE_CLASS_BASE gesetzt ist

SKIN_CLASS_BASE = 5500000    # aus dem vorhandenen Code (LogicCharacterEntry)
EMOTE_CLASS_BASE = None      # UNBEKANNT: erst eintragen, wenn die Pin-Basis-ID bekannt ist
COUNT_BLANK_ROWS = False     # True = Zeilen ohne Namen in den CSVs mitzählen (nur zum Testen)

# Skins und Pins kosten "Cosmetic" (resources.csv, ID 12)
COSMETIC_RESOURCE_ID = 12
COSMETIC_PER_BATTLE = 500    # damit du dir etwas kaufen kannst; 0 = aus
