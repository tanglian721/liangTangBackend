from flask import Flask, request, Response,render_template
import mariadb
import dbcreds
import json
import random
from datetime import datetime
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/api/project', methods=["GET"])
def project():
    if request.method == "GET":
        conn = None
        cursor = None
        try:          
            conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM project",)
            rows = cursor.fetchall()
            data = []
            headers = [ i[0] for i in cursor.description]
            for row in rows:
                data.append(dict(zip(headers,row)))
        except mariadb.ProgrammingError:
            print("program error...")
        except mariadb.DataError:
            print("Data error...")
        except mariadb.DatabaseError:
            print("Database error...")
        except mariadb.OperationalError:
            print("connect error...")
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if data != None:
                print(data)
                return Response(json.dumps(data, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
            
@app.route('/api/message', methods=["POST"])
def message():
    if request.method == "POST":
        name = request.json.get('name')
        email = request.json.get('email')
        content = request.json.get('content')
        conn = None
        cursor = None
        rows = None
        try:          
            conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            print(name)
            print(email)
            print(content)
            cursor.execute("INSERT INTO message(name,email,content) VALUES (?,?,?)", [name, email, content])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError:
            print("program error...")
        except mariadb.DataError:
            print("Data error...")
        except mariadb.DatabaseError:
            print("Database error...")
        except mariadb.OperationalError:
            print("connect error...")
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if rows == 1:
                return Response("Sent sccuess", mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)


@app.route('/api/upload', methods=["POST", "DELETE"])
def upload():
    if  request.method == "POST":
        target = os.path.join(APP_ROOT, '/var/www/homeDelicious/home_delicious_frontend/dist/img/uploadImgs')   
    # target = os.path.join(APP_ROOT, '/Users/Taylo/InnoTech/Assignments/Project/Home delicious/home_delicious_frontend')   
        if not os.path.isdir(target):
            os.mkdir(target)
        files = request.files.getlist("file")
        for file in files:
            # print(file)        
            filename = file.filename
            destination = "/".join([target, filename])
            print(destination)
            file.save(destination)
            image = Image.open(destination)
            if image.width > 1280 and image.height < 1280:
                with open(destination, 'r+b') as f:
                    with Image.open(f) as image:
                        cover = resizeimage.resize_width(image, 1280)
                        cover.save(destination, image.format)
            elif image.width < 1280 and image.height > 1280:
                with open(destination, 'r+b') as f:
                    with Image.open(f) as image:
                        cover = resizeimage.resize_height(image, 1280)
                        cover.save(destination, image.format)
            elif image.width > 1280 and image.height > 1280:
                with open(destination, 'r+b') as f:
                    with Image.open(f) as image:
                        cover = resizeimage.resize_cover(image, [1280,1280])
                        cover.save(destination, image.format)
        return Response(json.dumps(destination, default=str), mimetype="application/json", status=204)
    if __name__=="__main__":
        app.run(port=4555,debug=True)
    if  request.method == "DELETE":
        image = request.json.get("image")
        print(image)
        path = "/var/www/homeDelicious/home_delicious_frontend/dist/img/uploadImgs/"
        image_path = path+image
        print(image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
            if os.path.exists(image_path):
                return Response("Delete went wrong!", mimetype="text/html", status=500)
            else:
                return Response("Delete sucess", mimetype="application/json", status=200) 
        else:
            print("The file does not exist")