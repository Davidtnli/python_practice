from flask_restful import reqparse        # pip install flask==2.0.3
import pymysql                            # pip install pymysql
from flask import jsonify                 # pip install Flask-RESTful==0.3.9
import util                               # pip install flask-apispec==0.11.0
from flask_apispec import doc, use_kwargs, MethodResource, marshal_with  # pip install Flask-JWT-Extended==4.3.1
from cra_api_route import *
from flask_jwt_extended import create_access_token, jwt_required
from datetime import timedelta


def db_init():
    db = pymysql.connect(
        host='resanalyze.onthewifi.com',
        user='alldatainhere',
        password='SiDs5hPRSC/Vq[W1',
        port=3306,
        db='MYDB'
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return db, cursor


class Search(MethodResource):
    @doc(description = "查詢王品/瓦城最新20筆評論", tags = ['Comments'])
    @marshal_with(CommentsGetResponse, code=200)
    # @jwt_required()
    def get(self, brand, source):
        db,cursor = db_init()


        sql = f"SELECT * FROM `{brand}` WHERE src = '{source}' LIMIT 20;"
        cursor.execute(sql)
        content = cursor.fetchall()


        db.close()
        return util.success(content)