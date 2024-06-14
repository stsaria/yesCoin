import platform, shutil, os
if not os.path.isdir("data"): os.mkdir("data")

from app import app

def main():
    print("YesCoin Start..")
    app.run(host="0.0.0.0", port=11380)

if __name__ == "__main__":
    main()