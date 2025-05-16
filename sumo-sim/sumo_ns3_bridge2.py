import traci
import socket
import time
import subprocess
import os

SUMO_BINARY = "sumo-gui"  # Gunakan "sumo" jika tidak ingin GUI
this_dir = os.path.dirname(os.path.abspath(__file__))
SUMO_CONFIG = os.path.join(this_dir, "osm.sumocfg")
SUMO_PORT = 8813
NS3_HOST = '127.0.0.1'
NS3_PORT = 9999

# Jalankan SUMO secara otomatis
sumo_cmd = [SUMO_BINARY, "-c", SUMO_CONFIG, "--remote-port", str(SUMO_PORT), "--start"]
sumo_process = subprocess.Popen(sumo_cmd)
print("📤 Waiting for SUMO to start...")

# Perpanjang waktu tunggu agar SUMO lebih stabil
time.sleep(3)  # Tunggu lebih lama (3 detik) untuk memastikan SUMO siap

# Debug apakah port sudah terbuka
print(f"🖥 Checking if SUMO is listening on port {SUMO_PORT}...")
is_sumo_ready = False
for _ in range(10):  # Coba 10 kali
    try:
        traci.connect(port=SUMO_PORT)
        is_sumo_ready = True
        break
    except Exception as e:
        print(f"❌ Error connecting to SUMO: {e}")
        time.sleep(1)  # Tunggu 1 detik dan coba lagi

if not is_sumo_ready:
    print("❌ SUMO did not become ready in time. Exiting...")
    sumo_process.terminate()
    exit(1)

try:
    # Koneksi ke SUMO
    traci.connect(port=SUMO_PORT)
    print("✅ Connected to SUMO TraCI server")

    # Debug awal
    print("📋 Vehicles at start:", traci.vehicle.getIDList())
    print("⏱ Simulation end time:", traci.simulation.getEndTime())

    # Koneksi ke NS-3
    ns3_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ns3_sock.connect((NS3_HOST, NS3_PORT))
    print("✅ Connected to NS-3 socket")

    # Jalankan simulasi dalam loop tetap (misalnya 1000 langkah)
    for step in range(1000):  # 1000 langkah (dengan time.sleep 0.1 = 100 detik)
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()
        print(f"🚗 Step {step}: vehicles = {vehicle_ids}")

        for vid in vehicle_ids:
            pos = traci.vehicle.getPosition(vid)
            data = f'{vid},{pos[0]},{pos[1]}\n'
            ns3_sock.sendall(data.encode('utf-8'))

        time.sleep(0.1)  # sinkronisasi waktu dengan NS-3

except traci.exceptions.FatalTraCIError as e:
    print("❌ TraCI connection error:", e)

except ConnectionRefusedError as e:
    print("❌ NS-3 socket connection error:", e)

finally:
    try:
        ns3_sock.close()
    except Exception:
        pass
    try:
        traci.close()
    except Exception:
        pass
    sumo_process.terminate()
    print("🛑 Connections closed and SUMO terminated")
