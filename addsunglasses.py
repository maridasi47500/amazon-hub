import cv2
import os
import numpy as np
from sys import argv

def detect_face(image_path):
    # Load the face detection classifier
    #face_cascade = cv2.CascadeClassifier()
    #face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier('./' + 'haarcascade_frontalface_default.xml')

    # Read the input image
    image = cv2.imread(image_path)

    # Convert the image to grayscale (face detection requires grayscale)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)

    # Assuming there's only one face in the image, return its coordinates
    if len(faces) == 1:
        return faces[0]
    else:
        return None

def hellomain(mypic):
    # Path to the input photo
    image_path = mypic#'path_to_your_photo.jpg'

    # Load the photo
    image = cv2.imread(image_path)

    # Detect the face in the photo
    face_coords = detect_face(image_path)
    if face_coords is None:
        print("No face found in the photo.")
        return

    # Load the sunglass image with an alpha channel (transparency)
    sunglass_img = cv2.imread('lunette6.png', cv2.IMREAD_UNCHANGED)

    # Check if the sunglass image was successfully loaded
    if sunglass_img is None:
        print("Error: Could not read the sunglass image.")
        return

    # Resize the sunglass image to fit the detected face
    face_width, face_height = face_coords[2], face_coords[3]
    sunglass_img_resized = cv2.resize(sunglass_img, (face_width, face_height))

    # Get the region of interest (ROI) on the face where the sunglass will be placed
    roi = image[face_coords[1]:face_coords[1]+face_height, face_coords[0]:face_coords[0]+face_width]

    # Extract the alpha channel from the sunglass image and create a 3-channel alpha array
    alpha_sunglass = sunglass_img_resized[:, :, 3] / 255.0
    alpha_sunglass = np.stack([alpha_sunglass] * 3, axis=-1)

    # Remove the alpha channel from the sunglass image and convert it to BGR
    sunglass_bgr = sunglass_img_resized[:, :, :3]

    # Perform alpha blending to overlay the sunglass on the face
    overlay = (1 - alpha_sunglass) * roi + alpha_sunglass * sunglass_bgr

    # Replace the ROI in the original image with the sunglass overlay
    image[face_coords[1]:face_coords[1]+face_height, face_coords[0]:face_coords[0]+face_width] = overlay

    print(image_path)
    cv2.imwrite(image_path, image)
#cv2.imwrite(path,img_to_save)

    # Display the result
    cv2.imshow('Sunglass Overlay', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("./static/photos/"+argv[1])
    print(os.path.join("./static/photos",argv[1]))
    hellomain("./static/photos/"+argv[1])
