from flask_restful import reqparse
import pymysql
from flask import jsonify
import util
from flask_apispec import doc, use_kwargs, MethodResource, marshal_with
from carts_route_model import *
from flask_jwt_extended import create_access_token, jwt_required
from datetime import timedelta


def db_init():
    db = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        port=3307,
        db='myshop'
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return db, cursor

def get_access_token(account):
    token = create_access_token(
        identity={"account": account},
        expires_delta=timedelta(days=1)
    )
    return token


class Carts(MethodResource):

    @doc(description = "Add products", tags = ['Cart'])
    @use_kwargs(CartPostRequest ,location="json")
    @marshal_with(CartPostResponse, code=201)
    @jwt_required()
    def post(self, **kwargs):
        db,cursor = db_init()



        cart = {
            'product_name': kwargs['product_name'],
            'amount': int(kwargs['amount']),
            'customer_name': kwargs['customer_name']
        }

        sql = """

        INSERT INTO `myshop`.`carts` (`product_name`,`amount`,`customer_name`)
        VALUES (%s,%s,%s);

        """

        sql1 = "SELECT * FROM myshop.products"
        cursor.execute(sql1)
        carts0 = cursor.fetchall()

        '''判斷有沒有庫存'''

        for i in carts0:
            if i['product_name'] == cart['product_name']:
                if i['product_num'] <= 0:
                    return f'Sorry，There is no enough {i["product_name"]}'


        result = cursor.execute(sql,(cart['product_name'], cart['amount'],cart['customer_name']))
        db.commit()


        '''更新產品庫存'''

        sql0 = f"UPDATE myshop.products INNER JOIN myshop.carts ON products.product_name = carts.product_name SET products.product_num = products.product_num - {cart['amount']} WHERE products.product_name = '{cart['product_name']}';"
        cursor.execute(sql0)
        db.commit()


        '''將購物車產品合計後輸出'''

        sql2 = f"SELECT product_name,SUM(amount) AS amount FROM `carts` WHERE customer_name = '{cart['customer_name']}' GROUP BY product_name;"
        cursor.execute(sql2)

        '''計算購物車產品之總價'''

        carts1 = cursor.fetchall()
        sql3 = f"SELECT SUM(`carts`.`amount` * `products`.`product_price`) AS total_price FROM `carts` LEFT JOIN `products` ON `carts`.`product_name` = `products`.`product_name` WHERE customer_name = '{cart['customer_name']}';"

        cursor.execute(sql3)
        carts2 = cursor.fetchall()
        price = carts2[0]['total_price']

        db.close()

        if result == 1:
            return util.success(carts1, price)
        
        return util.failure()

class Cart(MethodResource):
    
    @doc(description = "Change product info", tags = ['Cart'])
    @use_kwargs(CartPatchRequest ,location="json")
    @marshal_with(CartPostResponse, code=201)
    @jwt_required()
    def patch(self, customer_name, product_name, **kwargs):
        db, cursor = db_init()

        cart = {

            'amount': int(kwargs['amount']),
        }

        query = []

        '''將修改前的數量記下'''

        sql1 = f"SELECT amount FROM myshop.carts WHERE customer_name = '{customer_name}' AND product_name = '{product_name}'"
        cursor.execute(sql1)
        carts0 = cursor.fetchall()
        amount_ori = carts0[0]['amount']


        for key, value in cart.items():
            if value is not None:
                query.append(f"{key} = '{value}'")
        query = ",".join(query)

        sql = """
            UPDATE myshop.carts
            SET {}
            WHERE customer_name = '{}' AND product_name = '{}';
        """.format(query, customer_name, product_name)

        result = cursor.execute(sql)
        db.commit()

        '''更新產品庫存'''

        sql0 = f"UPDATE myshop.products INNER JOIN myshop.carts ON products.product_name = carts.product_name SET products.product_num = products.product_num - {cart['amount']} WHERE products.product_name = '{product_name}';"
        cursor.execute(sql0)
        db.commit()

        '''利用之前記錄的原本數量恢復庫存'''

        sql4 = f"UPDATE myshop.products INNER JOIN myshop.carts ON products.product_name = carts.product_name SET products.product_num = products.product_num + {amount_ori} WHERE products.product_name = '{product_name}';"
        cursor.execute(sql4)
        db.commit()

        '''將購物車產品合計後輸出'''

        sql2 = f"SELECT product_name,SUM(amount) AS amount FROM `carts` WHERE customer_name = '{customer_name}' GROUP BY product_name;"
        cursor.execute(sql2)
        carts1 = cursor.fetchall()

        '''計算購物車產品之總價'''

        sql3 = f"SELECT SUM(`carts`.`amount` * `products`.`product_price`) AS total_price FROM `carts` LEFT JOIN `products` ON `carts`.`product_name` = `products`.`product_name` WHERE customer_name = '{customer_name}';"
        cursor.execute(sql3)
        carts2 = cursor.fetchall()
        price = carts2[0]['total_price']

        db.close()

        if result == 1:
            return util.success(carts1, price)

        return util.failure()

class Delete(MethodResource):

    @doc(description = "Delete product in cart", tags = ['Cart'])
    @marshal_with(CartPostResponse, code=201)
    @jwt_required()
    def delete(self, customer_name, product_name):
        db, cursor = db_init()


        sql = """
            DELETE FROM carts
            WHERE product_name = '{}' AND customer_name = '{}';            
        """.format(product_name, customer_name)

        '''先更新產品庫存再執行刪除'''

        sql0 = f"UPDATE myshop.products INNER JOIN myshop.carts ON products.product_name = carts.product_name SET products.product_num = products.product_num + carts.amount WHERE products.product_name = '{product_name}';"
        cursor.execute(sql0)
        db.commit()

        result = cursor.execute(sql)
        db.commit()

        '''將購物車產品合計後輸出'''

        sql2 = f"SELECT product_name,SUM(amount) AS amount FROM `carts` WHERE customer_name = '{customer_name}' GROUP BY product_name;"
        cursor.execute(sql2)
        carts1 = cursor.fetchall()

        '''計算購物車產品之總價'''

        sql3 = f"SELECT SUM(`carts`.`amount` * `products`.`product_price`) AS total_price FROM `carts` LEFT JOIN `products` ON `carts`.`product_name` = `products`.`product_name` WHERE customer_name = '{customer_name}' ;"
        cursor.execute(sql3)
        carts2 = cursor.fetchall()
        price = carts2[0]['total_price']

        db.close()

        if result == 1:
            return util.success(carts1, price)

        return util.failure()

class ALL_info(MethodResource):

    @doc(description = "Get cart info", tags = ['Cart'])
    @marshal_with(CartGetResponse, code=201)
    @jwt_required()
    def get(self,customer_name):
        db,cursor = db_init()

        '''依照客戶姓名將購物車產品合計後輸出'''

        sql = f"SELECT product_name,SUM(amount) AS amount FROM `carts` WHERE customer_name = '{customer_name}' GROUP BY product_name;"
        cursor.execute(sql)
        carts = cursor.fetchall()

        '''計算購物車產品之總價'''

        sql3 = f"SELECT SUM(`carts`.`amount` * `products`.`product_price`) AS total_price FROM `carts` LEFT JOIN `products` ON `carts`.`product_name` = `products`.`product_name` WHERE customer_name = '{customer_name}';"
        cursor.execute(sql3)
        carts2 = cursor.fetchall()
        price = carts2[0]['total_price']

        db.close()
        return util.success(carts,price)

class Search(MethodResource):
    @doc(description = "Check/Search products info", tags = ['Cart'])
    @marshal_with(CartGetResponse, code=200)
    @jwt_required()
    def get(self, customer_name, word):
        db,cursor = db_init()

        '''依照客戶姓名以及模糊搜尋關鍵字，將購物車內相符合之產品合計後輸出'''

        sql = f"SELECT product_name,SUM(amount) AS amount FROM myshop.carts WHERE product_name LIKE '%{word}%' AND customer_name = '{customer_name}' GROUP BY product_name;"
        cursor.execute(sql)
        carts = cursor.fetchall()


        db.close()
        return util.success(carts)


class Login(MethodResource):
    @doc(description='User Login', tags=['Login'])
    @use_kwargs(LoginRequest, location="json")
    # @marshal_with(user_router_model.UserGetResponse, code=200)
    def post(self, **kwargs):
        db, cursor = db_init()
        account, password = kwargs["account"], kwargs["password"]
        sql = f"SELECT * FROM myshop.customers WHERE account = '{account}' AND password = '{password}';"
        cursor.execute(sql)
        user = cursor.fetchall()
        db.close()

        if user != ():
            token = get_access_token(account)
            data = {
                "message": f"Welcome back {user[0]['customer_name']}",
                "token": token}
            return util.success(data)
        
        return util.failure({"message":"Account or password is wrong"})


class Signin(MethodResource):
    @doc(description="Customer Sign in", tags=['Signin'])
    @use_kwargs(SigninRequest, location="json")
    @marshal_with(CartCommonResponse, code=200)
    def post(self, **kwargs):
        db, cursor = db_init()

        '''讓新客戶註冊'''

        user = {
            'customer_name': kwargs['customer_name'],
            'account': kwargs['account'],
            'password': kwargs['password'],
            'customer_note': kwargs['customer_note']
        }

        sql = """

            INSERT INTO `myshop`.`customers` (`customer_name`,`account`,`password`,`customer_note`)
            VALUES (%s,%s,%s,%s);

            """

        result = cursor.execute(sql, (user['customer_name'], user['account'], user['password'],user['customer_note']))

        db.commit()
        db.close()

        if result == 1:
            return util.success()

        return util.failure()