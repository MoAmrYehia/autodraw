from flask import Flask, request,jsonify, session
from flask_cors import CORS
from helper import resizing_vector
from code import perdict_img
import boto3

app = Flask(__name__)
CORS(app)

secret_key = "iuenp!m04*hu^@hieih" #secret_key for verifing backend requests
# (to be added to environment variables)

UPLOAD_FOLDER = 'static'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

tokens=[]

S3_BUCKET = 'autodraw'
folder = 'files/'
file_name = "stored_tokens.txt"
s3_access_key ='AKIAYHBCWEYTNPL6AYV4'
s3_secret_key='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'
s3_object= boto3.resource(
    's3',
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
    )
s3 = boto3.client('s3',
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key)

def upload_prev_tokens():
    obj = s3.get_object(Bucket= S3_BUCKET, Key= folder+ file_name)
    stored_tokens=obj['Body'].read()
    global tokens
    stored_tokens =stored_tokens.decode("utf-8")
    tokens = set(stored_tokens.split("\n")) #["2", "3"]
    # tokens =list(dict.fromkeys(tokens))



@app.route('/insert_token', methods=['POST'])
def insert_token():
    global tokens
    data = request.get_json(force=True)
    token = data['token']
    try:
        key = data['secret_key']
    except:
        key=""
    if key == secret_key or "secret_key" in session:

        session["secret_key"] = "secret_key"

        upload_prev_tokens()
        tokens.add(token)
        tokens=list(tokens)
        # s3_object.Object(S3_BUCKET,'files/stored_tokens.txt').put(Body=tokens)
        s3.put_object(Body='\n'.join(tokens), Bucket=S3_BUCKET, Key='files/stored_tokens.txt')

        return jsonify(tokens), 201
    else:
        return jsonify({"response": "UNAUTHORIZED"}), 401 # UNAUTHORIZED



@app.route('/delete_token', methods=['Delete'])
def delete_token():
    global tokens
    data = request.get_json(force=True)
    token = data['token']
    try:
        key = data['secret_key']
    except:
        key=""
    if key == secret_key or "secret_key" in session:
        clear_session(token)
        upload_prev_tokens()
        if token in tokens:
            tokens.remove(token)
            tokens =list(tokens)
            s3.put_object(Body='\n'.join(tokens), Bucket=S3_BUCKET, Key='files/stored_tokens.txt')
        else:
            return jsonify({"response": "This token does not exist!"}) , 404 # NOT Found
        return jsonify(tokens)
    else:
        return jsonify({"response": "UNAUTHORIZED"}), 401 # UNAUTHORIZED


def clear_session(token):
    session.pop(token, None)


@app.route('/', methods=['POST'])
def upload_image():
    global tokens
    input_data = request.get_json(force=True)
    token = input_data["token"]
    json_data =input_data["data"]
    width =int(input_data["width"])
    height =int(input_data["height"])
    if token:

        upload_prev_tokens()
        # print(tokens)

        if token in tokens:
            session[token] = token
        else:
            return jsonify({"response": "Invalid token"}) , 401
    elif "token" in session:
        token = session["token"]
    else:
        return jsonify({"response": "Token is required or session is expired"}), 401 # UNAUTHORIZED

    if not json_data:
        return jsonify({"response": "Image file is required"}), 404 # not found
    else:
        try:
            json_data = resizing_vector(json_data,width,height)
            scores = perdict_img(json_data)

            return jsonify(scores)
        except:
            return jsonify({"response": "Image file is required"}), 400 # Bad Request


if __name__ == "__main__":
    #app.run()
    app.run(host="0.0.0.0", port=5000)
