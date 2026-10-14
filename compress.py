import os
import shutil
from pathlib import Path
import subprocess


def check_ffmpeg():
  """檢查系統是否已安裝 FFmpeg"""
  if not shutil.which("ffmpeg"):
    print("錯誤：系統中找不到 FFmpeg！")
    return False
  return True


def batch_process_videos():
  """自動巡迴「待壓縮」資料夾內所有影片，進行變速與壓縮，完成後移至「壓縮完成」並刪除原檔"""
  base_dir = Path(r"C:\Users\VideoCompression")
  input_dir = base_dir / "input"
  output_dir = base_dir / "output"

  # 確保資料夾存在（若不存在則自動建立）
  input_dir.mkdir(parents=True, exist_ok=True)
  output_dir.mkdir(parents=True, exist_ok=True)

  # 定義支援的影片副檔名
  video_extensions = {".mp4", ".mov", ".mkv", ".avi", ".webm"}

  # 取得待壓縮資料夾內所有影片檔案
  video_files = [
      f
      for f in input_dir.iterdir()
      if f.is_file() and f.suffix.lower() in video_extensions
  ]

  if not video_files:
    print(f"「{input_dir}」資料夾中目前沒有找到任何待壓縮的影片檔案。")
    return

  print(f"找到 {len(video_files)} 個待壓縮的影片，開始批次處理...\n")

  for index, input_path in enumerate(video_files, 1):
    output_path = output_dir / input_path.name

    print(f"[{index}/{len(video_files)}] 正在處理：{input_path.name}")
    print("正在進行變速與壓縮，請稍候...")

    # FFmpeg 處理指令
    # FFmpeg 複合濾鏡說明：
    # 1. [0:v]setpts=2.0*PTS,scale=-2:720[v] -> 視訊時間戳放大 2 倍（變慢），並縮放到 720p
    # 2. [0:a]atempo=0.5[a] -> 音訊速度降為 0.5 倍（恢復正常語速，不變調）
    # 維持原速度:
    # -vf "scale=-2:720"：將高度縮放為 720p，寬度等比例自動調整
    # -preset fast：加快編碼速度

    command = [
        "ffmpeg",
        "-i",
        str(input_path),
        "-vf",
        "scale=-2:720",  
        "-vcodec",
        "libx264",
        "-preset",
        "fast", 
        "-crf",
        "24",
        "-r",
        "30",
        "-acodec",
        "aac",
        "-b:a",
        "128k",
        str(output_path),
    ]

    try:
      # 1. 執行壓縮與變速
      subprocess.run(command, check=True)
      print(f"  -> 壓縮成功！已儲存至：{output_path}")

      # 2. 刪除「待壓縮」資料夾中的原始檔案
      input_path.unlink()
      print(f"  -> 已刪除原始檔案：{input_path.name}\n")

    except subprocess.CalledProcessError as e:
      print(f"  -> ❌ 處理失敗，FFmpeg 執行錯誤：{e}\n")
    except Exception as e:
      print(f"  -> ❌ 發生未預期的錯誤：{e}\n")

  print("=" * 40)
  print("🎉 所有影片已全數處理完畢！")


if __name__ == "__main__":
  if check_ffmpeg():
    batch_process_videos()
