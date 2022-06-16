from marshmallow import Schema, fields

#Responses

class CommentsCommonResponse(Schema):
    message = fields.Str(example="success")

class CommentsGetResponse(CommentsCommonResponse):
    data = fields.List(fields.Dict(), example={
            "id": 1,
            "date": "19900101",
            "content": "Good",
            "brand": "王品",
            "src": "google"

        })




