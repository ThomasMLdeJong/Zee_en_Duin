from mijnproject import app, db
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from mijnproject.models import User, Bungalow, Type
from mijnproject.forms import LoginForm, RegistrationForm, BoekForm


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/aanbod')
@login_required
def welkom():
    rows = Bungalow.query.count()
    bungalow_omschrijving = []
    bungalow_afbeelding = []
    bungalow_prijs = []
    bungalow_naam = []
    bungalow_id = []
    for x in range(1, rows+1):
        user = current_user.username
        bungalow = Bungalow.query.get(x)
        bungalow_id.append(bungalow.id)
        bungalow_naam.append(bungalow.naam)
        bungalow_omschrijving.append(bungalow.beschrijving)
        bungalow_afbeelding.append(bungalow.afbeelding)
        bungalow_type = bungalow.type
        type = Type.query.get(bungalow_type)
        bungalow_prijs.append(type.weekprijs)
    return render_template('aanbod.html', user=user, bungalow_naam=bungalow_naam, bungalow_prijs=bungalow_prijs, 
                            bungalow_omschrijving=bungalow_omschrijving, bungalow_afbeelding=bungalow_afbeelding, 
                            bungalows=rows, bungalow_id=bungalow_id)
        
@app.route('/boek', methods=['GET','POST'])
@login_required
def boek():
    if request.method == 'POST':
        if request.form["Boeking"]:
            print(True)
            id = request.form["Boeking"]
            bungalow = Bungalow.query.get(id)
            bungalow_afbeelding = bungalow.afbeelding
            bungalow_naam = bungalow.naam
            bungalow_omschrijving = bungalow.beschrijving
            bungalow_type = bungalow.type
            type = Type.query.get(bungalow_type)
            bungalow_prijs = type.weekprijs
            return render_template('boek.html', bungalow_afbeelding=bungalow_afbeelding,
                                bungalow_naam=bungalow_naam, bungalow_omschrijving=bungalow_omschrijving,
                                bungalow_prijs=bungalow_prijs)

    form = BoekForm()

    if form.validate_on_submit():
        boeking = Boeking(gast=current_user.get_id(),
            bungalow=form.username.data,
            week=form.password.data)

        db.session.add(boeking)
        db.session.commit()
        flash('Dank voor de boeking! ')
        return redirect(url_for('/aanbod'))
    return render_template('boek.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Je bent nu uitgelogd!', 'info')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            flash('Succesvol ingelogd!.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0] == '/':
                next = url_for('welkom')

            return redirect(next)
    return render_template('login.html', form=form)


@app.route('/registreren', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        print(True)
        try:
            user = User(email=form.email.data,
                        username=form.username.data,
                        password=form.password.data)

            db.session.add(user)
            db.session.commit()
            flash('Dank voor de registratie. Er kan nu ingelogd worden! ')
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
    return render_template('registreren.html', form=form)

@app.route('/bevestig', methods=["POST"])
def bevestig():

    return render_template('bevestig.html')


if __name__ == '__main__':
    app.run(debug=True)
