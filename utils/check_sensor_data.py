import sqlite3

def main():
    db_path = 'data/wind_turbine.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sensor_readings LIMIT 5')
        rows = cursor.fetchall()
        print('First 5 rows in sensor_readings:')
        for row in rows:
            print(row)
        if not rows:
            print('No data found in sensor_readings.')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        try:
            conn.close()
        except:
            pass
    print('Script finished.')

if __name__ == '__main__':
    main() 