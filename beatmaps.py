import struct
import requests
import os
import shutil
import http.client
import re
import sys
import pyperclip
from time import sleep
BEATMAPSET_REGEX = re.compile(rb"BeatmapSetID:(\d+)\r\n")


def Download_beatmapset(bid):
    conn = http.client.HTTPSConnection("catboy.best")

    headers = {
        'User-Agent': 'BEATMAP DOWNLOADED /1.0 (discord: ifyk)'
    }

    print("starting download of",bid)
    conn.request("GET", f"/d/{bid}", headers=headers)

    res = conn.getresponse()
    data = res.read()
    print("finished beatmap download",bid)
    conn.close()
    return(data)

def get_drain_time_seconds(osu_bytes: bytes) -> float:
    text = osu_bytes.decode("utf-8", errors="ignore")

    if "[HitObjects]" not in text:
        return 0.0

    section = text.split("[HitObjects]", 1)[1]

    times = []
    for line in section.splitlines():
        if not line or line.startswith("//"):
            continue
        parts = line.split(",")
        if len(parts) >= 3 and parts[2].isdigit():
            times.append(int(parts[2]))

    if not times:
        return 0.0

    return (max(times) - min(times)) / 1000.0


def create_mappack(maps, name: int):
    base_dir = "bpacks"
    os.makedirs(base_dir, exist_ok=True)

    download_folder = os.path.join(base_dir, f"{name} - mappack")
    os.makedirs(download_folder, exist_ok=True)

    for beatmap in maps:
        # print(beatmap)
        try:
            url = f"https://osu.ppy.sh/osu/{beatmap}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.content
            start = data.find(b"BeatmapSetID:")

            if start == -1:
                print("BeatmapSetID not found")
                continue
            drain_time = get_drain_time_seconds(data)

            if drain_time > 1800:
                print(f"Skipping {beatmap}: drain time {drain_time/60:.2f} min")
                continue
            # print(drain_time)
            i = start + len(b"BeatmapSetID:")
            m = BEATMAPSET_REGEX.search(data)
            if not m:
                print("BeatmapSetID not found")
                continue

            bmp_id = int(m.group(1))
            # print(bmp_id)



            data = Download_beatmapset(bmp_id)
            file_path = os.path.join(download_folder, f"{beatmap}.osz")
            with open(file_path, "wb") as f_out:
                f_out.write(data)

            print(f"Downloaded beatmap {beatmap} | {file_path}")

        except Exception as e:
            print(f"Failed to download beatmap {beatmap}: {e}")

    try:
        zip_name = os.path.join(base_dir, f"{name} mappack")
        zip_path = shutil.make_archive(zip_name, "zip", download_folder)

        shutil.rmtree(download_folder)
        print("file created:",zip_path)
        print("Exiting in 1 minute")
        sleep(60)
        exit()

    except Exception as e:
        print(e, "went wrong")
        return None


if __name__ == "__main__":
    print("Reading clipboard..")
    beatmap_ids = pyperclip.paste()
    try:
        print(f"Current text saved on clipboard: {beatmap_ids.split()}")
    except:
        print("something went wrong trying to read clipboard.. exiting in 5 seconds")
        sleep(5)
        exit()
    try:
        answer = str(input("are these the ids? that you want to create into a mappack? (y(es) /n(o) ")).lower()
    except:
        print("something went wrong with your answer")
        sleep(5)
        exit()
    while answer not in ["y","yes","ye"]:
        print("Reading clipboard in 5 seconds..")
        sleep(5)
        print("Reading clipboard..")
        beatmap_ids = pyperclip.paste()
        try:
            print(f"Current text saved on clipboard: {beatmap_ids.split()}")
        except:
            print("something went wrong trying to read clipboard.. exiting in 5 seconds")
            sleep(5)
            exit()
        try:
            answer = str(input("are these the ids? that you want to create into a mappack? (y(es) /n(o) ")).lower()
        except:
            print("something went wrong with your answer")
            sleep(5)
            exit()
    name = str(input("Enter an name: "))
    create_mappack(beatmap_ids.split(), name)