import zmq, json, psycopg2, os
from datetime import datetime, timezone, timedelta

print("Starting server")
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:36513")
time = 0
print("Ready to receive")

try:
    while True:
        data = socket.recv_string()
        print("\aRaw data:", data)
        try:
            parsed_data = json.loads(data)
            print("Parsed data:", json.dumps(parsed_data, indent=2))
            loc = parsed_data
            cell = parsed_data
            ident = parsed_data.get("cellIdentity", {})
            sig = parsed_data

            ts_ms = loc.get("timestamp")
            NSK = timezone(timedelta(hours=7))
            ts = datetime.fromtimestamp(ts_ms / 1000, tz=NSK)
            time = ts
            values = (
                loc.get("latitude"),
                loc.get("longitude"),
                loc.get("altitude"),
                ts,
                loc.get("speed"),
                loc.get("accuracy"),
                ident.get("pci"),
                ident.get("tac"),
                ident.get("earfcn"),
                ident.get("mcc"),
                ident.get("mnc"),
                sig.get("band"),
                sig.get("rsrp"),
                sig.get("rsrq"),
                sig.get("rssnr"),
                sig.get("rssi"),
                sig.get("cqi"),
                sig.get("asuLevel"),
                sig.get("timing_advance")
            )

            print("Values to insert:", values)

            with get_connection() as connect:
                with connect.cursor() as cur:
                    try:
                        cur.execute("""
                            INSERT INTO data (
                                latitude, longitude, altitude, timestamp, speed, accuracy,
                                pci, tac, earfcn, mcc, mnc, band, rsrp, rsrq, rssnr, rssi, cqi, asu_level, timing_advance
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, values)
                        connect.commit()
                    except psycopg2.errors.UniqueViolation:
                        connect.rollback()
                        print("Запись с таким timestamp уже существует, пропускаем")

        except Exception as e:
            print("Ошибка парса:", e)

        socket.send_string(f"\nПринял: {time.strftime("%H:%M:%S\n%d.%m.%Y")}")

except KeyboardInterrupt:
    socket.close()
    context.term()
    print("\nGracefully shutdown\n")