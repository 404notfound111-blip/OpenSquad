import sqlite3, json, traceback
from threading import Lock
from typing import Union


class SQLiteManager:
    def __init__(self):
        """Creates an instance of SQLiteManager and prepares the database"""
        self.connection: sqlite3.Connection = sqlite3.connect("Classes/DataBase/players.sqlite", check_same_thread=False)
        self.cursor: sqlite3.Cursor = self.connection.cursor()
        self.mutex: Lock = Lock()
        try:
            self.connection.execute(f"CREATE TABLE IF NOT EXISTS playerTable (high integer, low integer, accountToken text, data json)")
        except (sqlite3.ProgrammingError, Exception) as e:
            print(f"An exception has occurred while trying to set up the playerTable database. Error: {e}")
        self.currentID: list = self.incrementID()

    def createEntry(self, auth: str, data: dict):
        """Creates an entry to the database and updates it"""
        self.mutex.acquire()
        try:
            self.cursor.execute(f"INSERT INTO playerTable (high, low, accountToken, data) VALUES (?, ?, ?, ?)",
                                (*data["id"], auth, json.dumps(data, ensure_ascii=False)))
            self.connection.commit()
        except (sqlite3.ProgrammingError, Exception) as e:
            print(f"An exception has occurred while trying to create an entry. Error: {e}")
        finally:
            self.mutex.release()

    def getEntry(self, auth: str, acMutex: bool = True) -> dict:
        if acMutex: self.mutex.acquire()
        try:
            self.cursor.execute("SELECT data FROM playerTable WHERE accountToken = ?", (auth,))
            row = self.cursor.fetchone()
            return json.loads(row[0]) if row else None
        except (sqlite3.ProgrammingError, Exception) as e:
            print(f"An exception has occurred while trying to get an entry. Error: {e}")
        finally:
            if acMutex: self.mutex.release()

    def updateEntry(self, item: Union[list[str], str], value, auth: str = None, data: dict = None):
        """Updates an entry on a specific item with the updated value and saves it into the database"""
        with self.mutex:
            try:
                if data is None: entry = self.getEntry(auth, False)
                else:
                    entry = data
                    auth = data["token"]

                if entry is None:
                    print(f"[SQLiteManager::] updateEntry: no entry found for token {auth}")
                    return

                if isinstance(item, list):
                    for i, key in enumerate(item): entry[key] = value[i]  # war: enumerate(list) -> Bug
                else:
                    entry[item] = value

                # Nur None entfernen. Vorher wurden auch 0, [], False usw. gelöscht,
                # dadurch gingen z.B. leere Listen/Nullwerte beim Speichern verloren.
                entry = {k: v for k, v in entry.items() if v is not None}

                self.cursor.execute("UPDATE playerTable SET data = ? WHERE accountToken = ?", (json.dumps(entry, ensure_ascii=False), auth,))
                self.connection.commit()
            except (sqlite3.ProgrammingError, Exception) as e:
                traceback.print_exc()
                print(f"An exception has occurred while trying to save an entry. Error: {e}")

    def savePlayer(self, player):
        """Schreibt den kompletten Spielstand. Legt den Eintrag an, falls es noch keinen gibt."""
        if not player.accountToken or not player.accountID:
            return
        data = player.toDict()
        with self.mutex:
            try:
                payload = json.dumps(data, ensure_ascii=False)
                self.cursor.execute("UPDATE playerTable SET data = ? WHERE accountToken = ?", (payload, player.accountToken))
                if self.cursor.rowcount == 0:
                    self.cursor.execute("INSERT INTO playerTable (high, low, accountToken, data) VALUES (?, ?, ?, ?)",
                                        (*data["id"], player.accountToken, payload))
                self.connection.commit()
            except Exception as e:
                traceback.print_exc()
                print(f"An exception has occurred while trying to save the player. Error: {e}")

    def incrementID(self):
        with self.mutex:
            try:
                self.cursor.execute("SELECT high, low FROM playerTable ORDER BY high DESC, low DESC")
                HighID, LowID = self.cursor.fetchone()
                return [HighID, LowID]
            except:
                return [0, 1]
