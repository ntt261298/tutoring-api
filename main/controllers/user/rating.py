from marshmallow import fields

from main import app, auth, errors, db
from main.enums import RatingScore
from main.schemas.base import BaseSchema
from main.libs.validate_args import validate_args
from main.models.question import QuestionModel
from main.models.user_rating import UserRatingModel
from main.models.expert_rank import ExpertRankModel
from main.engines.tasks.router import handle_question_rating


class UserRatingResponseSchema(BaseSchema):
    question_id = fields.Integer(required=True)
    comment = fields.String(missing=None)
    score = fields.Integer(validate=lambda n: RatingScore.MINIMUM_SCORE <= n <= RatingScore.MAXIMUM_SCORE)


@app.route('/user/me/ratings', methods=['POST'])
@auth.requires_token_auth('user')
@validate_args(UserRatingResponseSchema())
def user_rating(user, args):
    question_id = args.get('question_id')
    question = QuestionModel.query.get(question_id)

    if not question or question.user_id != user.id:
        raise errors.BadRequest(message='Question is not found')

    score = args.get('score')
    comment = args.get('comment')

    user_rating = UserRatingModel(
        user_id=user.id,
        question_id=question.id,
        expert_id=question.expert_id,
        topic_id=question.topic_id,
        score=score,
        comment=comment
    )

    user_rating.save_to_db()

    expert_rank = ExpertRankModel.query.filter_by(
        expert_id=question.expert_id,
        topic_id=question.topic_id
    ).first()

    all_user_rates = UserRatingModel.query.filter_by(
        expert_id=question.expert_id,
        topic_id=question.topic_id,
    )

    # Recalculate expert rank
    sum = 0
    total = 0
    for rate in all_user_rates:
        sum += rate.score
        total += 1

    if total:
        expert_rank.score_avg = sum / total
        db.session.commit()

    handle_question_rating.delay(question.id)

    return BaseSchema().jsonify({})
