from flask import jsonify
from marshmallow import Schema


class BaseSchema(Schema):
    def jsonify(self, obj, many=False):
        return jsonify(self.dump(obj, many=many))
