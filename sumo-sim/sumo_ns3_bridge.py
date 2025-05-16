# sumo_ns3_bridge.py — Python middleware with SUMO auto-launch

import traci
import socket
import time
import subprocess
import os

SUMO_BINARY = "sumo-gui"  # atau "sumo-gui" jika ingin GUI
this_dir = os.path.dirname(os.path.abspath(__file__))
SUMO_CONFIG = os.path.join(this_dir, "osm.sumocfg")
SUMO_PORT = 8813
NS3_HOST = '127.0.0.1'
NS3_PORT = 9999

# Jalankan SUMO secara otomatis dengan opsi --remote-port dan --start
sumo_cmd = [SUMO_BINARY, "-c", SUMO_CONFIG, "--remote-port", str(SUMO_PORT), "--start"]
sumo_process = subprocess.Popen(sumo_cmd)
time.sleep(1.0)  # Tunggu TraCI server siap

try:
    # Koneksi ke SUMO TraCI
    traci.connect(port=SUMO_PORT)
    print("Connected to SUMO TraCI server")

    # Koneksi ke NS-3 TCP socket
    ns3_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ns3_sock.connect((NS3_HOST, NS3_PORT))
    print("Connected to NS-3 socket")

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()
        for vid in vehicle_ids:
            pos = traci.vehicle.getPosition(vid)
            data = f'{vid},{pos[0]},{pos[1]}\n'
            ns3_sock.sendall(data.encode('utf-8'))
        time.sleep(0.1)  # sinkronisasi waktu

except traci.exceptions.FatalTraCIError as e:
    print("TraCI connection error:", e)

finally:
    try:
        ns3_sock.close()
    except:
        pass
    try:
        traci.close()
    except:
        pass
    sumo_process.terminate()
    print("Connections closed and SUMO terminated")
