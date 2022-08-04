from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import cv2
from PIL import Image
import utils
from utils import segmentation_output
import os
from werkzeug.utils import secure_filename
 
app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
 
@app.route('/')
def home():
    return render_template('index.html')
 
@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file'] #file received here
    #image.save(b, format='jpg')
    

    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        #IMAGE_NAME = filename
        #resized_im, seg_map = run_visualization()
        #file = file.resize((200,100))
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        #read the image...
        fileread = cv2.imread(UPLOAD_FOLDER+'/'+filename)
        #process
        resized_im, seg_map = segmentation_output(UPLOAD_FOLDER+'/'+filename)
        seg_img = cv2.imread(seg_map)
        file.save(os.path.join(UPLOAD_FOLDER, "seg.jpg"),seg_img)
        #fileread = cv2.resize(fileread,(200,100))
        #cv2.imwrite(os.path.join(UPLOAD_FOLDER, "res.jpg"), fileread)
    
        
        flash('Image successfully uploaded and displayed below')
        return render_template('index.html', filename=filename, filename2="seg.jpg")
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
 
if __name__ == "__main__":
    app.run(debug=True)
