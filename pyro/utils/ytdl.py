import os
import shutil
import time
import asyncio
import youtube_dl
import humanfriendly
import humanreadable as hr
from pyro.utils.common import botCommon

progress_status_time = {}
cl = None


class yt_dl:
    @staticmethod
    async def upload_progress_update(upload, total, chat_id, message_id, start_time):
        global cl
        global progress_status_time

        diff = time.time() - start_time if time.time() == start_time else 1
        up_speed_converted_raw = hr.BitPerSecond(str(upload / diff), default_unit=hr.BitPerSecond.Unit.BPS).mega_bps
        up_speed_split = str(up_speed_converted_raw).split(".")[0]

        if time.time() - int(progress_status_time[f"{chat_id}+{message_id}"]["last_updated"]) > 3:
            await cl.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"<code>Progress: Uploading \n"
                     f"Uploaded: {humanfriendly.format_size(int(upload), binary=True)} of "
                     f"{humanfriendly.format_size(int(total), binary=True)}\n"
                     f"Speed: {up_speed_split} MiBps</code>"
            )
            job_update_timing = {
                f"{chat_id}+{message_id}": {
                    "last_updated": time.time()
                }
            }
            progress_status_time.update(job_update_timing)

    @staticmethod
    async def upload_file_to_tg(chat_id, message_id, file):
        global cl
        global progress_status_time

        start_time = time.time()
        await cl.send_video(
            chat_id=chat_id,
            video=file,
            progress=yt_dl().upload_progress_update,
            progress_args=[chat_id, message_id, start_time]
        )

        await cl.delete_messages(
            chat_id=chat_id,
            message_ids=message_id
        )

        del progress_status_time[f"{chat_id}+{message_id}"]

        try:
            shutil.rmtree(os.path.dirname(file))

        except Exception as e:
            print(str(e))

    @staticmethod
    async def update_dl_progress(chat_id, message_id, d):
        global cl
        global progress_status_time

        if time.time() - int(progress_status_time[f"{chat_id}+{message_id}"]["last_updated"]) > 3:
            dl_speed_raw = d['speed'] if d['speed'] else 0
            dl_speed_converted_raw = hr.BitPerSecond(str(dl_speed_raw), default_unit=hr.BitPerSecond.Unit.BPS).mega_bps
            dl_speed_split = str(dl_speed_converted_raw).split(".")[0]
            await cl.edit_message_text(
                chat_id=int(chat_id),
                message_id=int(message_id),
                text=f"<code>Progress: Downloading \n"
                     f"Downloaded: {humanfriendly.format_size(int(d['downloaded_bytes']), binary=True)} \n"
                     f"Speed: {dl_speed_split} MiBps</code>"
            )
            job_update_timing = {
                f"{chat_id}+{message_id}": {
                    "last_updated": time.time()
                }
            }
            progress_status_time.update(job_update_timing)

    @staticmethod
    def progress_hooks(d):
        tmp_dir = os.path.basename(os.path.dirname(d["filename"]))
        vid_id, chat_id, message_id = tmp_dir.split("+")
        if d["status"] == "downloading":
            loop = asyncio.get_event_loop()
            loop.run_until_complete(yt_dl().update_dl_progress(int(chat_id), int(message_id), d))
        elif d["status"] == "finished":
            loop = asyncio.get_event_loop()
            loop.run_until_complete(yt_dl().upload_file_to_tg(int(chat_id), int(message_id), d["filename"]))

    @staticmethod
    async def dl_initiator(vid_id, chat_id, message_id, client):
        global cl
        cl = client

        tmp_dir = os.path.join(botCommon.tmp_dir, f"{vid_id}+{chat_id}+{message_id}")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        global progress_status_time

        job_update_timing = {
            f"{chat_id}+{message_id}": {
                "last_updated": time.time()
            }
        }
        progress_status_time.update(job_update_timing)

        ydlOpts = {
            'format': "bestvideo[height<=480]+bestaudio/best",
            'progress_hooks': [yt_dl().progress_hooks],
            'noplaylist': 'true',
            'outtmpl': f'{tmp_dir}/%(title)s.%(ext)s',
            'ignoreerrors': 'true'
        }
        with youtube_dl.YoutubeDL(ydlOpts) as yt:
            yt.download([f'http://www.youtube.com/watch?v={vid_id}'])
