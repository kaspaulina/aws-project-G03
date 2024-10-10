from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from PIL import Image
import boto3
import os
#teste2
# Set up the Flask app
app = Flask(__name__)

# Set up Flask environment variables
app.config['MAX_SIZE'] = 15 * 1024 * 1024 # 15MB
app.config['UPLOAD_EXTENSIONS'] = ['jpg', 'png', 'jpeg']
app.config['MAX_WIDTH_HEIGHT'] = 4096

# Set up the Amazon S3 client
s3 = boto3.client('s3', 
                  aws_access_key_id= os.environ.get('ACCESS_KEY'),
                  aws_secret_access_key=os.environ.get('SECRET_KEY'),
                  aws_session_token=os.environ.get('SESSION_TOKEN'),
                  region_name='us-east-1')

rekognition = boto3.client('rekognition', 
                        aws_access_key_id= os.environ.get('ACCESS_KEY'),
                        aws_secret_access_key=os.environ.get('SECRET_KEY'),
                        aws_session_token=os.environ.get('SESSION_TOKEN'),
                        region_name='us-east-1')

# AWS S3 bucket configuration
BUCKET_NAME = "cats-and-dogs-v2"
# AWS Rekognition model configuration
MODEL_ARN = "arn:aws:rekognition:us-east-1:014573712316:project/cats-and-dogs-v2/version/cats-and-dogs-v2.2024-10-09T21.11.38/1728519096459"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.')[-1].lower() in app.config['UPLOAD_EXTENSIONS']


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if "file" not in request.files:
            msg = "No file selected"
            return render_template("index.html", msg=msg)

        file = request.files["file"]

        if file.filename == "":
            msg = "No file selected"
            return render_template("index.html", msg=msg)

        if file and allowed_file(file.filename):
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            if file_size > app.config['MAX_SIZE']:
                msg = "File size must be less than 15MB"
                return render_template("index.html", msg=msg)
            file.seek(0)
            img = Image.open(file)
            if img.width > app.config['MAX_WIDTH_HEIGHT'] or img.height > app.config['MAX_WIDTH_HEIGHT']:
                msg = "Height and width must be less than 4096px"
                return render_template("index.html", msg=msg)
        else:
            msg = "File type not supported. Must be .jpg, .jpeg, or .png"
            return render_template("index.html", msg=msg)

        filename = secure_filename(file.filename)
        file.seek(0)
        s3.upload_fileobj(file, BUCKET_NAME, filename)

        labels = rekognition.detect_custom_labels(
            ProjectVersionArn=MODEL_ARN,
            Image={
                'S3Object': {
                    'Bucket': BUCKET_NAME,
                    'Name': filename,
                }
            }
        )['CustomLabels']
        return render_template("index.html", labels=labels, prediction=True)

    return render_template("index.html")

if __name__ == '__main__':
  app.run()