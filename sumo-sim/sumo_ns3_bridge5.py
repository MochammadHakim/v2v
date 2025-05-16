import traci
import socket
import time
import os
from sumolib import checkBinary
import subprocess

#SUMO_CFG = "osm.sumocfg"
this_dir = os.path.dirname(os.path.abspath(__file__))
SUMO_CONFIG = os.path.join(this_dir, "osm.sumocfg")
SUMO_PORT = 8813
NS3_HOST = '127.0.0.1'
NS3_PORT = 9999

# Pastikan environment variable SUMO_HOME ada
if 'SUMO_HOME' not in os.environ:
    os.environ['SUMO_HOME'] = "/usr/share/sumo"  # Ganti sesuai sistem Anda

sumoBinary = checkBinary('sumo-gui')  # JANGAN gunakan 'sumo-gui' untuk bridge otomatis
sumoCmd = [sumoBinary, "-c", SUMO_CONFIG, "--remote-port", str(SUMO_PORT)]

# Jalankan SUMO via subprocess
print("🚀 Starting SUMO (CLI)...")
sumoProcess = subprocess.Popen(sumoCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Tunggu SUMO ready
time.sleep(1)

try:
    traci.init(SUMO_PORT)
    print("✅ Connected to SUMO TraCI")

    # Koneksi ke NS-3 socket
    ns3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ns3_socket.connect((NS3_HOST, NS3_PORT))
    print(f"✅ Connected to NS-3 at {NS3_HOST}:{NS3_PORT}")

    # Jalankan simulasi
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        for veh_id in traci.vehicle.getIDList():
            pos = traci.vehicle.getPosition(veh_id)
            x, y = pos
            data = f"{veh_id},{x},{y}\n"
            ns3_socket.sendall(data.encode())

        time.sleep(0.1)

    traci.close()
    ns3_socket.close()
    print("✅ Simulation ended.")

except Exception as e:
    print(f"❌ Error during simulation: {e}")
    try:
        traci.close()
    except:
        pass
    sumoProcess.kill()

finally:
    sumoProcess.kill()
