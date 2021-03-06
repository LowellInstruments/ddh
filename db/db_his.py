import sqlite3


class DBHis:

    def __init__(self, db_n='db_his.db'):
        self.dbfilename = db_n
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS records\
            ( \
            id              INTEGER PRIMARY KEY, \
            mac             TEXT, \
            name            TEXT, \
            lat             TEXT, \
            lon             TEXT, \
            sws_time        TEXT  \
            )"
        )
        db.commit()
        c.close()
        db.close()

    # v is a list which gets converted to string
    def add_record(self, m, n, lat, lon, t):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('INSERT INTO records('
                  'mac, name, lat, lon, sws_time) '
                  'VALUES(?,?,?,?,?)',
                  (m, n, lat, lon, t))
        db.commit()
        c.close()
        db.close()

    def update_record(self, m, n, lat, lon, t, i):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('UPDATE records set mac=?, name=?, \
                    lat=?, lon=?, sws_time=? \
                    WHERE id=?', (m, n, lat, lon, t, i))
        db.commit()
        c.close()
        db.close()

    def delete_record(self, record_id):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('DELETE FROM records where id=?', (record_id,))
        db.commit()
        c.close()
        db.close()

    def delete_all_records(self):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('DELETE FROM records')
        db.commit()
        c.close()
        db.close()

    def list_all_records(self):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('SELECT * from records')
        records = c.fetchall()
        c.close()
        db.close()
        return records

    def get_record(self, record_id):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('SELECT * from records WHERE id=?', (record_id, ))
        records = c.fetchall()
        c.close()
        db.close()
        return records[0]

    def get_record_id(self, m):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('SELECT id from records WHERE mac=?', (m, ))
        records = c.fetchall()
        c.close()
        db.close()
        return records[0][0]

    def does_record_exist(self, m):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('SELECT EXISTS(SELECT 1 from records WHERE mac=?)', (m, ))
        records = c.fetchall()
        c.close()
        db.close()
        return records[0][0]

    def count_records(self):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('SELECT Count(*) FROM records')
        r = c.fetchall()
        c.close()
        db.close()
        return r[0][0]

    def safe_update(self, m, n, lat, lon, t):
        if self.does_record_exist(m):
            i = self.get_record_id(m)
            self.delete_record(i)
        self.add_record(m, n, lat, lon, t)

    def get_recent_records(self):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('SELECT * from records ORDER BY sws_time DESC')
        records = c.fetchall()
        c.close()
        db.close()
        return records
