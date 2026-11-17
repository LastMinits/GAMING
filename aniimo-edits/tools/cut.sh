#!/bin/bash
# usage: cut.sh SRC OUTDIR name start end [name start end ...]
# crops the gameplay window (1080x608 @ y=463) from the vertical stream, 30fps H.264
SRC=$1; OUT=$2; shift 2; mkdir -p $OUT
while [ $# -ge 3 ]; do n=$1; s=$2; e=$3; shift 3
  ffmpeg -v error -y -ss $s -to $e -i "$SRC" -vf "crop=1080:608:0:463,fps=30" \
    -c:v libx264 -preset veryfast -crf 19 -pix_fmt yuv420p -c:a aac -b:a 160k -ar 48000 -movflags +faststart "$OUT/$n.mp4" && echo "ok $n"
done
