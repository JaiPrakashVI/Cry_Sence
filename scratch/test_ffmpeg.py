import os
import shutil
import static_ffmpeg

print("Before add_paths:", shutil.which("ffmpeg"))
static_ffmpeg.add_paths()
print("After add_paths:", shutil.which("ffmpeg"))

# Let's run a quick ffmpeg test using os.system
if shutil.which("ffmpeg"):
    print("FFmpeg is available! Testing execution:")
    os.system("ffmpeg -version")
else:
    print("FFmpeg could not be added.")
