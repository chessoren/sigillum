#!/bin/sh
# Assemble scenes/<id>.webm + voice/<id>.mp3 into sigillum-demo.mp4 (H.264/AAC, 1920x1080).
set -e
cd "$(dirname "$0")"
mkdir -p build
: > build/list.txt
for v in voice/*.mp3; do
  id=$(basename "$v" .mp3)
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$v")
  len=$(python3 -c "print(round($d + 0.7, 2))")
  # skip the first 0.6 s of each recording (page load), start the voice 0.25 s in
  ffmpeg -y -v error -ss 0.6 -i "scenes/$id.webm" -i "$v" -t "$len" \
    -filter_complex "[0:v]fps=30,scale=1920:1080:flags=lanczos,format=yuv420p,tpad=stop_mode=clone:stop_duration=3[v];[1:a]adelay=250|250,apad,aresample=48000[a]" \
    -map "[v]" -map "[a]" -t "$len" -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 160k -ar 48000 "build/$id.mp4"
  echo "file '$id.mp4'" >> build/list.txt
done
ffmpeg -y -v error -f concat -safe 0 -i build/list.txt -c copy build/concat.mp4
ffmpeg -y -v error -i build/concat.mp4 -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:v copy -c:a aac -b:a 160k -movflags +faststart sigillum-demo.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 sigillum-demo.mp4
