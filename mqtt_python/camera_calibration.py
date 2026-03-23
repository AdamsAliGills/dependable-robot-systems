import os.path
from pathlib import Path
import glob
import cv2
import numpy as np


class camera:
    def __init__(self, port):
        self.port = port

    def calibration(self, path):
        nb_horizontal = 9
        nb_vertical = 6

        objp = np.zeros((nb_horizontal * nb_vertical, 3), np.float32)
        objp[:, :2] = np.mgrid[0:nb_vertical, 0:nb_horizontal].T.reshape(-1, 2)

        objpoints = []
        imgpoints = []

        images = glob.glob(os.path.join(path, "*.png"))
        assert images

        for fname in images:
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            ret, corners = cv2.findChessboardCorners(
                gray, (nb_vertical, nb_horizontal), None
            )

            if ret:
                objpoints.append(objp)

                corners2 = cv2.cornerSubPix(
                    gray,
                    corners,
                    (11, 11),
                    (-1, -1),
                    criteria=(
                        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                        30,
                        0.001,
                    ),
                )
                imgpoints.append(corners2)

                img = cv2.drawChessboardCorners(
                    img, (nb_vertical, nb_horizontal), corners2, ret
                )
                cv2.imshow("img", img)
                cv2.waitKey(500)

        cv2.destroyAllWindows()
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None
        )
        imgs = cv2.imread(os.path.join(path, "board_frame_17.png"))
        h, w = imgs.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        return newcameramtx

    def capture_board(self, path):

        cam = cv2.VideoCapture(self.port)
        cv2.namedWindow("test")
        img_counter = 0

        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            cv2.imshow("test", frame)

            k = cv2.waitKey(1)
            if k % 256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            elif k % 256 == 32:
                # SPACE pressed
                img_name = "board_frame_{}.png".format(img_counter)
                cv2.imwrite(os.path.join(path, img_name), frame)
                print("{} captured".format(img_name))
                img_counter += 1

        cam.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    port = 0
    cwd = Path.cwd()
    imgs = Path("imgs")
    imgs.mkdir(parents=True, exist_ok=True)
    img_path = cwd / imgs
    print(cwd)
    cam = camera(port)
    # cam.capture_board(img_path)
    cam_matrix = cam.calibration(str(img_path))
    print(cam_matrix)
