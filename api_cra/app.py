from flask import Flask
from flask_restful import Api
from cra_api import *
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_jwt_extended import JWTManager


app = Flask(__name__)
api = Api(app)

app.config["DEBUG"] = True # Able to reload flask without exit the process
app.config["JWT_SECRET_KEY"] = "secret_key" #JWT token setting 

# Swagger setting
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Awesome Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

api.add_resource(Search, '/Comments/<string:brand>/<string:source>')
docs.register(Search)


if __name__ == '__main__':
    JWTManager().init_app(app)
    app.run(host='0.0.0.0', port=5000, debug=True)