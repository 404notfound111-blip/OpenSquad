# Einstellungen für Belohnungen nach einem Kampf.
# Speicherort: Classes/Utilities/RewardConfig.py

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
