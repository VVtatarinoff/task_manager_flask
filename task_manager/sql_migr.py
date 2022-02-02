import os.path
from pathlib import Path
import sqlite3

DATABASE = Path(__file__).resolve().parent / 'tm.db'
print(DATABASE)
#db = sqlite3.connect(DATABASE)
# SCRIPT = 'ALTER TABLE users ADD COLUMN password varchar(200)'
SCRIPT=''
with sqlite3.connect(DATABASE) as db:
    db.cursor().executescript(SCRIPT)
    db.commit()
    db.close

