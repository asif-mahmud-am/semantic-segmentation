

numpy_image = np.array(resized_im) 
object_mapping = deepcopy(numpy_image)
object_mapping[seg_map==label_number] = 255
object_mapping[seg_map != label_number] = 0
original_img = Image.open(org_img)
original_img = np.array(original_img)
mapping_resized = cv2.resize(object_mapping, 
                             (original_img.shape[1],
                              original_img.shape[0]),
                             Image.ANTIALIAS)
gray = cv2.cvtColor(mapping_resized, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray,(15,15),0)
ret3,thresholded_img = cv2.threshold(blurred,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
mapping = cv2.cvtColor(thresholded_img, cv2.COLOR_GRAY2RGB)
blurred_original_image = cv2.GaussianBlur(original_img,
                                          (251,251), 
                                          0)
plt.imshow(blurred_original_image)
layered_image = np.where(mapping != (0,0,0), 
                         original_img, 
                         blurred_original_image)
plt.imshow(layered_image)