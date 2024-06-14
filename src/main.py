import sys, os
if not os.path.isdir("data"): os.mkdir("data")

import centralApp, nodeApp

PORT = 11380

def main():
    print("YesCoin Start..")
    if sys.argv > 1:
        if sys.argv[1] == "centralServer":
            centralApp.app.run(host='0.0.0.0', port=PORT)
            return
    nodeApp.registerWithCentralServers()
    nodeApp.app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()