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

def add_quiz(form):
    if 'name' in form: 
        quiz = form.get('name')
        user = db.session.get(User, 1)
        quiz = Quiz(quiz, user)
        db.session.add(quiz)
        db.session.commit()

def get_quiz(quize_id=None):
    if quize_id:
        q = Quiz.query.filter_by(id=int(quize_id)).one_or_none()
        return q
    else:
        return Quiz.query.order_by(Quiz.name).all()

def save_quiz(form):
    quiz = get_quiz(session_model.session['quiz_id'])
    question = []

    for id in form.getlist("question"):
        question.append(Question.query.filter_by(id=int(id)).one_or_none())

    quiz.question = question
    db.session.commit()

def add_question(form):
    if 'name' in form: 
        question = Question(form.get('name'), form.get('answer'), form.get('wrong1'), form.get('wrong2'), form.get('wrong3'))
        db.session.add(question)
        db.session.commit()
    
def start_quiz(quiz):
    session_model.session['right_answers'] = 0
    session_model.session['question_n'] = 0
    session_model.session['quiz_id'] = quiz.id

    question = quiz.question[0]
    answers = [question.answer, question.wrong1, question.wrong2, question.wrong3 ]
    shuffle(answers)
   
    return [question, answers]

def score(form, question):
    return 1 if form.get('answer') == question.answer else 0

def check_answer(form):
    quiz = get_quiz(session_model.session['quiz_id'])
    mode = "pass"
    question = [None] * 2

    session_model.session['right_answers'] += score(form, quiz.question[session_model.session['question_n']])
    session_model.session['question_n'] += 1

    if session_model.session['question_n'] == len(quiz.question):
        mode = "finish"
        question[0] = session_model.session['right_answers']
        question[1] = session_model.session['question_n']
    else:    
        question[0] = quiz.question[session_model.session['question_n']]
        question[1] = [question[0].answer, question[0].wrong1, question[0].wrong2, question[0].wrong3 ]
        shuffle(question[1])
    
    return mode, quiz, question

def get_questions(quiz=None):
    question = [None] * 2

    if quiz:
        question[0] = quiz.question
        question[1] = Question.query.filter(~Question.quiz.any(Quiz.id == quiz.id)).all()
    else:
        question[0] = Question.query.all()

    return question

def quiz_logic(method, form):
    mode = "list"
    quiz = None
    question = None

    def reset():
        nonlocal mode, quiz, question
        mode = "list"
        quiz = get_quiz()
        question = get_questions()
        
    if method == "GET":
        reset()

    elif method == "POST":
        action = form.get("action") or "list"

        if action == "new":
            mode = "new"

        elif action == "new_question":
            mode = "new_question"

        elif action == "add":
            add_quiz(form)
            reset()

        elif action == "add_question":
            add_question(form)
            reset()

        elif action == "pass":
            quiz = get_quiz(form.get('quiz'))
            if len(quiz.question):
                mode = "pass"
                question = start_quiz(quiz)
            else:
                reset()
        
        elif action == "next":
            mode, quiz, question = check_answer(form)

        elif action == "edit":
            quiz = get_quiz(form.get('quiz'))
            question = get_questions(quiz)
            session_model.session['quiz_id'] = quiz.id
            mode = "edit"

        elif action == "save":
            save_quiz(form)
            reset()

        else: # action == "list" or any    
            reset()

    return mode, [quiz, question]
