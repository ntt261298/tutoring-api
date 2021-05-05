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


class QuestionSchema(BaseSchema):
    id = fields.Int()
    user_id = fields.Int()
    expert_id = fields.Int()
    created = fields.DateTime()

    file_data = fields.Raw()

    text = fields.Str()
    topic = fields.Nested(TopicSchema)


class QuestionState(Schema):
    state = fields.String()


class QuestionWithState(QuestionSchema):
    question_state = fields.Nested(QuestionState)
