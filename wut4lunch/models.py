from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    member_since = db.Column(db.Date)

    lunches = db.RelationshipProperty('Lunch', backref='user', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        from sqlalchemy.exc import IntegrityError
        import forgery_py

        seed()
        for x in range(count):
            name = forgery_py.name.full_name()
            email = forgery_py.internet.email_address()
            username = (name.split()[0] + str(randint(1, 500))).lower()
            password = forgery_py.lorem_ipsum.word()
            member_since = forgery_py.date.date()
            u = User(name=name, email=email, username=username, password=password, member_since=member_since)
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, name, username, email, password, member_since):
        self.name = name
        self.username = username
        self.email = email
        self.set_password(password)
        self.member_since = member_since

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.username


class Lunch(db.Model):
    __tablename__ = 'lunches'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128))
    pub_date = db.Column(db.DateTime)
    visible_to = db.Column(db.String(12))
    enjoyed = db.Column(db.String())

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint, choice
        from sqlalchemy.exc import IntegrityError
        import forgery_py

        seed()
        user_count = User.query.count()
        enjoyed = choice(['delicious', 'tasty', 'nice', 'ok', 'nasty'])
        for x in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            l = Lunch(text=forgery_py.lorem_ipsum.word(), pub_date=forgery_py.date.date(), visible_to='all', enjoyed=enjoyed, author_id=u.id)
            db.session.add(l)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, text, pub_date, visible_to, enjoyed, author_id):
        self.text = text
        self.pub_date = pub_date
        self.visible_to = visible_to
        self.enjoyed = enjoyed
        self.author_id = author_id

    def __repr__(self):
        return '<Lunch %r>' % self.lunch