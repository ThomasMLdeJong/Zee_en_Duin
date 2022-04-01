from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from mijnproject.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "E-mail"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Wachtwoord"})
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "E-mail"})
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Gebruikersnaam"})
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('pass_confirm', message='Passwords Must Match!')], render_kw={"placeholder": "Wachtwoord"})
    pass_confirm = PasswordField('Confirm password', validators=[DataRequired()], render_kw={"placeholder": "Herhaal wachtwoord"})
    submit = SubmitField('Registreer!')

    def check_email(self, field):
        # Check of het e-mailadres al in de database voorkomt!
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Dit e-mailadres staat al geregistreerd!')

    def check_username(self, field):
        # Check of de gebruikersnaam nog niet vergeven is!
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Deze gebruikersnaam is al vergeven, kies een andere naam!')

class BoekForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "E-mail"})
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Gebruikersnaam"})
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('pass_confirm', message='Passwords Must Match!')], render_kw={"placeholder": "Wachtwoord"})
    pass_confirm = PasswordField('Confirm password', validators=[DataRequired()], render_kw={"placeholder": "Herhaal wachtwoord"})
    submit = SubmitField('Registreer!')

    def check_email(self, field):
        # Check of het e-mailadres al in de database voorkomt!
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Dit e-mailadres staat al geregistreerd!')

    def check_username(self, field):
        # Check of de gebruikersnaam nog niet vergeven is!
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Deze gebruikersnaam is al vergeven, kies een andere naam!')