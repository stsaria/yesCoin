import threading, sys, os
if not os.path.isdir("data"): os.mkdir("data")

import centralApp, nodeApp

PORT = 11380

def main():
    print("YesCoin Start..")
    # 定期的に同期するためにスレッドを作る
    if len(sys.argv) > 1:
        if sys.argv[1] == "centralServer":
            centralApp.reigsterSelfCentralServer()
            syncThread = threading.Thread(target=centralApp.syncPeriodically)
            syncThread.daemon = True
            syncThread.start()
            centralApp.app.run(host='0.0.0.0', port=PORT)
            return
    syncThread = threading.Thread(target=nodeApp.syncPeriodically)
    syncThread.daemon = True
    syncThread.start()
    nodeApp.app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()