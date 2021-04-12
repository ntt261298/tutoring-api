from flask import jsonify
from marshmallow import Schema


class BaseSchema(Schema):
    def jsonify(self, obj):
        return jsonify(self.dump(obj))
