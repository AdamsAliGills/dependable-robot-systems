'''
camera calibration for distorted images with chess board samples
reads distorted images, calculates the calibration and write undistorted images

Original code is from: https://github.com/IBM/opencv-power/blob/master/samples/python/calibrate.py
Simplfy the input and output
Save the results as a .yaml file.
'''


import numpy as np
import cv2 as cv


# built-in modules
import os

if __name__ == '__main__':
    import sys
    import getopt
    from glob import glob

#Original Code: Input the images path via command line
    #args, img_mask = getopt.getopt(sys.argv[1:], '', ['debug=', 'square_size=', 'threads='])
    #args = dict(args)
    #args.setdefault('--debug', './output/')
    #args.setdefault('--square_size', 1.0)
    #args.setdefault('--threads', 4)
    #if not img_mask:
    #    img_mask = '../data/left??.jpg'  # default
    #else:
    #    img_mask = img_mask[0]
    #img_names = glob(img_mask)
    #debug_dir = args.get('--debug')
    #if debug_dir and not os.path.isdir(debug_dir):
    #    os.mkdir(debug_dir)
    #square_size = float(args.get('--square_size'))

#Modified: Input the images path directly via variables
#Input the images path
    img_mask = "/*.jpg"   
#Selce the square size of Calibration paper
    square_size = 25.0
#The size of vertices
    pattern_size = (9, 6)
#The folder to save the processed images 
    debug_dir = './Calibration_record/'
#Create 4 threads to accelerate the program           
    threads_num = 4


    img_names = glob(img_mask)
    
    if not img_names:
        print(f"Error：Can't find any images in path: {img_mask}")
        sys.exit(1)

    if debug_dir and not os.path.isdir(debug_dir):
        os.mkdir(debug_dir)


    
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= square_size

    obj_points = []
    img_points = []
    h, w = cv.imread(img_names[0], 0).shape[:2]  # TODO: use imquery call to retrieve results

    def processImage(fn):
        print('processing %s... ' % fn)
        img = cv.imread(fn, 0)
        if img is None:
            print("Failed to load", fn)
            return None

        assert w == img.shape[1] and h == img.shape[0], ("size: %d x %d ... " % (img.shape[1], img.shape[0]))
        found, corners = cv.findChessboardCorners(img, pattern_size)
        if found:
            term = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_COUNT, 30, 0.1)
            cv.cornerSubPix(img, corners, (5, 5), (-1, -1), term)

        if debug_dir:
            vis = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
            cv.drawChessboardCorners(vis, pattern_size, corners, found)
            name = os.path.splitext(os.path.basename(fn))[0]
            outfile = os.path.join(debug_dir, name + '_chess.png')
            cv.imwrite(outfile, vis)

        if not found:
            print('chessboard not found')
            return None

        print('           %s... OK' % fn)
        return (corners.reshape(-1, 2), pattern_points)

    #threads_num = int(args.get('--threads'))
    if threads_num <= 1:
        chessboards = [processImage(fn) for fn in img_names]
    else:
        print("Run with %d threads..." % threads_num)
        from multiprocessing.dummy import Pool as ThreadPool
        pool = ThreadPool(threads_num)
        chessboards = pool.map(processImage, img_names)

    chessboards = [x for x in chessboards if x is not None]
    for (corners, pattern_points) in chessboards:
        img_points.append(corners)
        obj_points.append(pattern_points)

    # calculate camera distortion
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv.calibrateCamera(obj_points, img_points, (w, h), None, None)

    print("\nRMS:", rms)
    print("camera matrix:\n", camera_matrix)
    print("distortion coefficients: ", dist_coefs.ravel())

    #Save the result as a .yaml file
    yaml_filename = "calibration_data.yaml"
    fs = cv.FileStorage(yaml_filename, cv.FILE_STORAGE_WRITE)
    fs.write("rms", rms)
    fs.write("camera_matrix", camera_matrix)
    fs.write("dist_coeffs", dist_coefs)
    fs.release()


    # undistort the image with the calibration
    #Save the processed images in folder--Calibration_record
    print('')
    for fn in img_names if debug_dir else []:
        name = os.path.splitext(os.path.basename(fn))[0]
        img_found = os.path.join(debug_dir, name + '_chess.png')
        outfile = os.path.join(debug_dir, name + '_undistorted.png')

        img = cv.imread(img_found)
        if img is None:
            continue

        h, w = img.shape[:2]
        newcameramtx, roi = cv.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

        dst = cv.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)

        # crop and save the image
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]

        print('Undistorted image written to: %s' % outfile)
        cv.imwrite(outfile, dst)

    cv.destroyAllWindows()