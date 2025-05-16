import traci
import subprocess
import socket
import time
import os
import sys

# Konfigurasi
SUMO_BINARY = "sumo-gui"
SUMO_PORT = 8813
NS3_HOST = "127.0.0.1"
NS3_PORT = 9999

# Lokasi konfigurasi
this_dir = os.path.dirname(os.path.abspath(__file__))
SUMO_CONFIG = os.path.join(this_dir, "osm.sumocfg")

# Jalankan SUMO GUI
sumo_cmd = [SUMO_BINARY, "-c", SUMO_CONFIG, "--remote-port", str(SUMO_PORT)]
print("🚀 Starting SUMO...")
sumo_process = subprocess.Popen(sumo_cmd)
time.sleep(2)

# Hubungkan ke TraCI
try:
    traci.connect(port=SUMO_PORT)
    print("✅ Connected to SUMO TraCI")
except Exception as e:
    print(f"❌ Failed to connect to SUMO: {e}")
    sumo_process.terminate()
    sys.exit(1)

# Hubungkan ke NS-3 socket server
try:
    ns3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ns3_socket.connect((NS3_HOST, NS3_PORT))
    print(f"✅ Connected to NS-3 at {NS3_HOST}:{NS3_PORT}")
except Exception as e:
    print(f"❌ Failed to connect to NS-3: {e}")
    traci.close()
    sumo_process.terminate()
    sys.exit(1)

# Loop simulasi
step = 0
try:
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()

        for veh_id in vehicle_ids:
            pos = traci.vehicle.getPosition(veh_id)
            speed = traci.vehicle.getSpeed(veh_id)
            message = f"{veh_id},{pos[0]},{pos[1]},{speed}\n"
            ns3_socket.sendall(message.encode())
            print(f"[{step}] Sent to NS-3: {message.strip()}")

        step += 1
        time.sleep(0.05)  # jangan terlalu cepat

except Exception as e:
    print(f"❌ Error during simulation: {e}")

finally:
    traci.close()
    ns3_socket.close()
    sumo_process.terminate()
    print("🛑 Simulation ended, connections closed.")
