import os
import cv2
import numpy as np
import mediapipe as mp

def BGRemover(path):
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

    image_path = os.path.join(path, 'images')
    images = os.listdir(image_path)

    image_index= 0
    bg_image = cv2.imread(image_path+'/'+images[image_index])

    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        _, input_image = cap.read()
        if not _:
            break

        # flip the input_image to horizontal direction
        input_image = cv2.flip(input_image, 1)
        input_image1 = cv2.flip(input_image, 1)
        height , width, channel = input_image.shape

        RGB = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)

        # get the result 
        results = selfie_segmentation.process(RGB)

        # extract segmented mask
        mask = results.segmentation_mask

        # it returns true or false where the condition applies in the mask
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.6

        # resize the background image to the same size of the original input_image
        bg_image = cv2.resize(bg_image, (width, height))

        # combine input_image and background image using the condition
        output_image = np.where(condition, input_image, bg_image)

        cv2.putText(input_image, "Press b to change, s to save, q to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.imshow("input_image", input_image)
        cv2.imshow("Output", output_image)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite(path+"/input.png",input_image1)
            cv2.imwrite(path+"/bg.png",bg_image)
            cv2.imwrite(path+"/output.png",output_image)
        elif key == ord('b'):
            while True:
                if image_index != len(images)-1:
                    image_index += 1
                else:
                    image_index = 0
                bg_image = cv2.imread(image_path+'/'+images[image_index])
                if bg_image is not None:
                    break
    cap.release()
    cv2.destroyAllWindows()
