import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    def paginate_questions(request):
        page = request.args.get('page', 1, type=int)
        start = (page-1)*QUESTIONS_PER_PAGE
        end = start+QUESTIONS_PER_PAGE
        questions = Question.query.all()
        return questions[start:end]

    def format_data(items):
        formatted_items = [item.format() for item in items]
        return formatted_items

    @app.route('/categories')
    def categories():
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type
        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    @app.route('/questions')
    def get_questions():
        questions = paginate_questions(request)
        if len(questions) == 0:
            abort(404)

        # format questions
        formatted_questions = format_data(questions)

        # get categories
        categories = Category.query.all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type

        total_question = len(Question.query.all())

        current_category = list(set([ques['category']
                                     for ques in formatted_questions]))

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': total_question,
            'categories': formatted_categories,
            'current_category': current_category
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter_by(id=question_id).one_or_none()
        if not question:
            abort(404)

        question.delete()

        return jsonify({
            'success': True
        })

    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            body = request.get_json()
            # if search term found
            title = body.get('searchTerm', None)
            if title:
                # get questions based in search term
                questions = Question.query.filter(
                    Question.question.ilike('%'+title+'%')).all()
                formatted_questions = format_data(questions)

                return jsonify({
                    'success': True,
                    'questions': formatted_questions
                })

            # check if all data exists
            if body.get('question') is None or body.get('answer') is None or\
                    body.get('category') is None or body.get('difficulty') is None:
                abort(400)
            # if the request for creating a new item
            new_question = Question(
                question=body.get('question'),
                answer=body.get('answer'),
                category=body.get('category'),
                difficulty=int(body.get('difficulty'))
            )

            new_question.insert()
            return jsonify({
                'success': True
            })
        except:
            abort(400)

    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()
        if not category:
            abort(404)

        # get all question by category
        questions = Question.query.filter_by(category=category_id)
        formatted_questions = format_data(questions)
        return jsonify({
            'success': True,
            'questions': formatted_questions
        })

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()
        category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions')
        if category['id'] != 0:
            # get category and all its questions
            categorydb = Category.query.filter_by(
                id=category['id']).one_or_none()
            if not categorydb:
                abort(404)
            questions = Question.query.filter_by(category=categorydb.id)
        else:
            questions = Question.query.all()
        remaining_question = []
        for question in questions:
            found = False
            for prev in previous_questions:
                if prev == question.id:
                    found = True
                    break
            if not found:
                remaining_question.append(question)
        random_index = random.randint(0, len(remaining_question)-1)
        return jsonify({
            'success': True,
            'question': remaining_question[random_index].format()
        })

    '''
  error handlers for all expected errors  
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Not Found"
        }), 404

    @app.errorhandler(422)
    def un_processable_entitiy(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "un processable entitiy"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "bad request"
        }), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': "internal server error"
        }), 500

    return app
