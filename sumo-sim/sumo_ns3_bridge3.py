# sumo_ns3_bridge.py — bridge TraCI → NS-3 (port 9999)

import traci
import socket
import time
import subprocess
import os
import sys

# SUMO setup
SUMO_BINARY = "sumo-gui"  # untuk GUI, atau pakai "sumo" untuk headless
SUMO_PORT = 8813
#SUMO_CONFIG = "osm.sumocfg"  # pastikan path-nya benar
this_dir = os.path.dirname(os.path.abspath(__file__))
SUMO_CONFIG = os.path.join(this_dir, "osm.sumocfg")


# NS-3 setup
NS3_HOST = '127.0.0.1'
NS3_PORT = 9999

# Start SUMO with TraCI
sumo_cmd = [SUMO_BINARY, "-c", SUMO_CONFIG, "--remote-port", str(SUMO_PORT), "--start"]
print("🚀 Starting SUMO...")
sumo_process = subprocess.Popen(sumo_cmd)
time.sleep(2.0)  # beri waktu agar TraCI siap

try:
    # Connect to TraCI
    traci.connect(port=SUMO_PORT)
    print("✅ Connected to SUMO TraCI server")

    # Connect to NS-3 socket
    ns3_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ns3_sock.connect((NS3_HOST, NS3_PORT))
    print(f"✅ Connected to NS-3 socket at {NS3_HOST}:{NS3_PORT}")

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()
        for vid in vehicle_ids:
            pos = traci.vehicle.getPosition(vid)  # (x, y)
            data = f'{vid},{pos[0]},{pos[1]}\n'
            ns3_sock.sendall(data.encode('utf-8'))
            print(f"📤 Sent to NS-3: {data.strip()}")
        time.sleep(0.1)  # kecilkan jika sinkron terlalu lambat
        step += 1

    print("✅ SUMO simulation finished")

except (traci.exceptions.FatalTraCIError, ConnectionRefusedError) as e:
    print(f"❌ Error: {e}")

finally:
    try:
        ns3_sock.close()
        print("🔌 NS-3 socket closed")
    except:
        pass
    try:
        traci.close()
        print("🔌 TraCI connection closed")
    except:
        pass
    sumo_process.terminate()
    print("🛑 SUMO terminated")
