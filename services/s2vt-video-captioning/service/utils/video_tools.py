import logging
import cv2

logging.basicConfig(level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger("video_tools")

# Get the length of 'video_path' in seconds
def get_video_length(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    return int(frame_count / fps)

# Gets a video and returns a list of frames extracted within start and stop interval.
def get_video_frames(video_path, frames_path, start_time_ms, stop_time_ms, pace):
    try:
        cap = cv2.VideoCapture(video_path)
        # Set start position
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time_ms)

        fps = cap.get(cv2.CAP_PROP_FPS)

        # If stop_time_ms == 0, get the entire video
        if stop_time_ms == 0:
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            stop_time_ms = int(frame_count/fps)*1000

        # If pace == 0, get 1 image every FPS/10
        if pace == 0:
            pace = int(1000/(fps/10))

        frames_list = []
        ok = True
        current_frame = 1
        while ok and cap.get(cv2.CAP_PROP_POS_MSEC) <= stop_time_ms:
            ok, frame = cap.read()
            if not ok:
                break
            frame_path = '{}/frame_{:03}.jpg'.format(frames_path, current_frame)
            log.debug('Storing: {}'.format(frame_path))
            cv2.imwrite(frame_path, frame)
            frames_list.append(frame_path)
            current_frame += 1
            cap.set(cv2.CAP_PROP_POS_MSEC, cap.get(cv2.CAP_PROP_POS_MSEC) + pace)

        cap.release()
        cv2.destroyAllWindows()
        return True, frames_list
    except Exception:
        return False, []
