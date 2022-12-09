import subprocess


def main():
    subprocess.run(["niv", "update"])
    print("nivupdate")


if __name__ == "__main__":
    main()
