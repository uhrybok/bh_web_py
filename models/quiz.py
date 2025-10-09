from flask_sqlalchemy import SQLAlchemy
import models.session as session_model
from random import shuffle

db = SQLAlchemy()

quiz_question = db.Table('quiz_question',
            db.Column('quiz_ud', db.Integer, db.ForeignKey('quiz.id'), primary_key=True),
            db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True),
            )

class IdNameMixin:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, name) -> None:
        super().__init__()
        self.name = name

class User(IdNameMixin, db.Model):
    quizes = db.relationship('Quiz', backref='user', 
                             cascade = "all, delete, delete-orphan",
                             lazy='select')

class Quiz(IdNameMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, name: str, user: User) -> None:
        super().__init__(name)
        self.user = user

class Question(IdNameMixin, db.Model):
    answer = db.Column(db.String(100), nullable=False)
    wrong1 = db.Column(db.String(100), nullable=False)
    wrong2 = db.Column(db.String(100), nullable=False)
    wrong3 = db.Column(db.String(100), nullable=False)
    
    quiz = db.relationship(
                'Quiz', 
                secondary=quiz_question, backref = 'question')

    def __init__(self, name: str, answer, wrong1, wrong2, wrong3) -> None:
        super().__init__(name)
        self.answer = answer
        self.wrong1 = wrong1
        self.wrong2 = wrong2
        self.wrong3 = wrong3

def db_add_test_data():
    db.drop_all()
    db.session.commit()
    db.create_all()

    users = [
        User('Poirot'),
        User('Marple')
    ]    

    quizes = [
        Quiz('QUIZ 1', users[0]),
        Quiz('QUIZ 2', users[0]),
        Quiz('QUIZ 3', users[1]),
        Quiz('QUIZ 4', users[1])
    ]

    questions = [
        Question('Что выведет этот код: print(bool("False"))?', 'True', 'False', 'bool("False")', 'None'),
        Question('Что выведет этот код: print("".join(sorted("cab")))?', 'abc', 'cab', "['a','b','c']", 'True'),
        Question('Что выведет этот код: print({1, 2, 3} & {3, 4, 5})', '{3}', '[3]', '{1, 2, 3, 4, 5}', 'False'),
        Question('Что выведет этот код: print(0.1 + 0.2 == 0.3)', 'False', 'True', '0.1 + 0.2 == 0.3', 'None'),
    ]

    quizes[0].question.append(questions[0])
    quizes[0].question.append(questions[1])
    quizes[0].question.append(questions[2])
    
    quizes[1].question.append(questions[1])
    quizes[1].question.append(questions[2])
    quizes[1].question.append(questions[3])
    
    quizes[2].question.append(questions[0])
    quizes[2].question.append(questions[1])
    quizes[2].question.append(questions[3])
    
    quizes[3].question.append(questions[0])
    quizes[3].question.append(questions[2])
    quizes[3].question.append(questions[3])

    db.session.add_all(users + quizes + questions)
    db.session.commit()

def add_quiz(data):
    if 'name' in data: 
        quiz = data.get('name')
        user = db.session.get(User, 1)
        quiz = Quiz(quiz, user)
        db.session.add(quiz)
        db.session.commit()
        return quiz
    return None

def get_quiz(quize_id=None):
    if quize_id:
        q = Quiz.query.filter_by(id=int(quize_id)).one_or_none()
        return q
    else:
        return Quiz.query.order_by(Quiz.name).all()

def start_quiz(data):
    session_model.session['right_answers'] = 0
    session_model.session['question_n'] = 0
    session_model.session['quiz_id'] = data.id

    question = data.question[0]
    answers = [question.answer, question.wrong1, question.wrong2, question.wrong3 ]
    shuffle(answers)
   
    return [question, answers]

def score(form, question):
    return 1 if form.get('answer') == question.answer else 0

def check_answer(form):
    data = get_quiz(session_model.session['quiz_id'])
    mode = "pass"
    question = None
    answers = None

    session_model.session['right_answers'] += score(form, data.question[session_model.session['question_n']])
    session_model.session['question_n'] += 1

    if session_model.session['question_n'] == len(data.question):
        mode = "finish"
        question = session_model.session['question_n']
        answers = session_model.session['right_answers']
    else:    
        question = data.question[session_model.session['question_n']]
        answers = [question.answer, question.wrong1, question.wrong2, question.wrong3 ]
        shuffle(answers)
    
    return mode, data, [question, answers]

def quiz_logic(method, form):
    mode = "list"
    data = None
    question = None

    def back():
        nonlocal mode, data
        mode = "list"
        data = get_quiz()
        
    if method == "GET":
        back()

    elif method == "POST":
        action = form.get("action") or "list"

        if action == "list":
            back()

        elif action == "new":
            mode = "add"

        elif action == "add":
            mode = "list"
            add_quiz(form)
            data = get_quiz()

        elif action == "pass":
            data = get_quiz(form.get('quiz'))
            if len(data.question):
                mode = "pass"
                question = start_quiz(data)
            else:
                back()
        
        elif action == "next":
            mode, data, question = check_answer(form)

    return mode, data, question
