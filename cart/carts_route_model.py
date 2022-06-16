from marshmallow import Schema, fields


#Parameters(Schema)

class CartPostRequest(Schema):
    product_name = fields.Str(doc="product_name", required=True)
    amount = fields.Int(doc="amount", required=True)
    customer_name = fields.Str(doc="customer_name", required=True)

class CartPatchRequest(Schema):

    amount = fields.Int(doc="amount")


class SigninRequest(Schema):
    customer_name = fields.Str(doc="customer_name", required=True)
    account = fields.Str(doc="account", required=True)
    password = fields.Str(doc="product_num", required=True)
    customer_note = fields.Str(doc="customer_note")



class LoginRequest(Schema):
    account = fields.Str(doc = "account", required=True)
    password = fields.Str(doc = "password", required=True)

#Responses

class CartCommonResponse(Schema):
    message = fields.Str(example="success")

class CartGetResponse(CartCommonResponse):
    data = fields.List(fields.Dict(), example={
            "cart_id": 2,
            "product_name": "Apple",
            "amount": 10,
            "customer_id": 10
        })
    datetime = fields.Str()

class CartPostResponse(CartGetResponse):
    total_price = fields.Int()



