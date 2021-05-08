from marshmallow import fields, Schema

from main.schemas.base import BaseSchema


class CreateQuestionSchema(BaseSchema):
    class AttachmentSchema(BaseSchema):
        id = fields.Integer(required=True)
        nonce = fields.String(required=True)

    # For creating question with file
    file = fields.Nested(AttachmentSchema, allow_none=True)

    content = fields.Str(required=True)
    topic_id = fields.Int(required=True)


class TopicSchema(Schema):
    id = fields.Int()
    name = fields.String()


class UserRatingSchema(Schema):
    id = fields.Int()
    score = fields.String()


class FileSchema(Schema):
    id = fields.Int()
    name = fields.String()
    rendered_data = fields.String()


class QuestionMessageSchema(BaseSchema):
    class AttachmentSchema(BaseSchema):
        id = fields.Integer(required=True)
        nonce = fields.String(required=True)

    id = fields.Integer()
    user_id = fields.Integer()
    expert_id = fields.Integer()
    message = fields.String(required=False, missing=None)
    created = fields.DateTime()
    question_id = fields.Integer(required=True)

    # For file message
    file = fields.Nested(AttachmentSchema, allow_none=True)


class QuestionState(Schema):
    state = fields.String()


class ResponseMessageSchema(BaseSchema):
    id = fields.Integer()
    user_id = fields.Integer()
    expert_id = fields.Integer()
    message = fields.String(required=False, missing=None)
    created = fields.DateTime()
    question_id = fields.Integer(required=True)
    file = fields.Nested(FileSchema)


class QuestionSchema(BaseSchema):
    id = fields.Int()
    user_id = fields.Int()
    expert_id = fields.Int()
    created = fields.String()

    file = fields.Nested(FileSchema)

    text = fields.Str()
    topic = fields.Nested(TopicSchema)
    user_rating = fields.Nested(UserRatingSchema)
    messages = fields.Nested(ResponseMessageSchema, many=True)


class QuestionWithState(QuestionSchema):
    question_state = fields.Nested(QuestionState)
