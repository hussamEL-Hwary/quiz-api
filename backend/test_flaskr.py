import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres:///{}".format(self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        self.question = {
            'question': "Who is the best striker in the world?",
            'answer': "Robert Lewandowski",
            'difficulty': "1",
            'category': 6
        }

    def tearDown(self):
        """Executed after reach test"""
        print("test done!")
        pass

    def test_get_categories(self):
        """test successful get categories """
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_paginated_questions(self):
        """test successful get paginated questions"""
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_404_paginated_questions(self):
        """get questions for not found page number"""
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_question_by_ID(self):
        """test successful delete a question """
        # create a new question to delete
        new_question = Question(
            question=self.question['question'],
            answer=self.question['answer'],
            category=self.question['category'],
            difficulty=self.question['difficulty']
        )
        new_question.insert()
        res = self.client().delete('/questions/{}'.format(new_question.id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_delete_question(self):
        """trying to delete a question doesn't exist in the db"""
        res = self.client().delete('/question/100000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_create_question(self):
        """test succssfuly create a question"""
        res = self.client().post('/questions', json=self.question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_400_uncreated_question(self):
        """test create question with invalid data"""
        # miss category from data
        self.question['category'] = None
        res = self.client().post('/questions', json=self.question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_get_questions_in_category(self):
        """test get all questions in a specific category"""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_404_get_questions_in_category(self):
        """test get question for not existing category"""
        res = self.client().get('/categories/8898989/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_search_question(self):
        """test search with existing items"""
        res = self.client().post('/questions', json={'searchTerm': "ho"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_search_not_found(self):
        """test search with empty value"""
        res = self.client().post('/questions', json={'searchTerm': ""})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_get_quiz_question(self):
        """test successful get question for quiz"""
        res = self.client().post('/quizzes', json={'quiz_category': {'type': 'Science', 'id': '1'},
                                                   'previous_questions': []})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_notfound_quiz_question(self):
        """"test get quiz question with not existing category"""
        res = self.client().post('/quizzes', json={'quiz_category': {'type': 'none', 'id': '8888'},
                                                   'previous_questions': []})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
