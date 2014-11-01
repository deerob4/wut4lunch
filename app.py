from flask import Flask, render_template, redirect, url_for
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretstring'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class LunchForm(Form):
    name = StringField('Hi, my name is', validators=[DataRequired('Come on, they must call you something!')])
    food = StringField('and I just ate',
                       validators=[DataRequired('If you\'re not going to say what you ate, then piss off!')])
    submit = SubmitField('Share my meal!')


class Lunch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    food = db.Column(db.String())


@app.route('/', methods=['GET', 'POST'])
def home():
    form = LunchForm()
    if form.validate_on_submit():
        entry = Lunch(name=(form.name.data).lower(), food=form.food.data)
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('home'))
    entries = Lunch.query.all()
    winner = Lunch.query.filter_by()
    return render_template('index.html', form=form, entries=entries)


@app.route('/<name>')
def person(name):
    entries = Lunch.query.filter_by(name=name).all()
    return render_template('person.html', entries=entries, name=name)


if __name__ == '__main__':
    app.run(debug=True)