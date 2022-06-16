from datetime import datetime

def failure(data=None):
    if data is not None:
        return {'message': 'failure'}, 500
    
    return {
        'message': 'failure',
        'data': data,
        'datatime': datetime.utcnow().isoformat()
    }, 500

def success(data=None):
    if data is None:
        return {'message': 'success'}, 200

    return {
        'message': 'success',
        'data': data,
        'datatime': datetime.utcnow().isoformat()

    }, 200