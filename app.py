from main import app, db
from flask import render_template, redirect, request, url_for, flash, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from main.models import User, Bungalow, Type, Boeking
from main.forms import LoginForm, RegistrationForm
from datetime import datetime, timedelta
import os
from sqlalchemy.exc import IntegrityError


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/aanbod')
@login_required
def aanbod():
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
        
@app.route('/boek', methods=['POST'])
@login_required
def boek():
    if request.method == 'POST':
        if request.form["Boeking"]:
            id = request.form["Boeking"]
            bungalow = Bungalow.query.get(id)
            bungalow_afbeelding = bungalow.afbeelding
            bungalow_naam = bungalow.naam
            bungalow_omschrijving = bungalow.beschrijving
            bungalow_type = bungalow.type
            type = Type.query.get(bungalow_type)
            bungalow_prijs = type.weekprijs
            boeken = f"{id} {bungalow_prijs}"
            return render_template('boek.html', bungalow_afbeelding=bungalow_afbeelding,
                                bungalow_naam=bungalow_naam, bungalow_omschrijving=bungalow_omschrijving,
                                bungalow_prijs=bungalow_prijs, boeken=boeken)
    form = "boekform?"

    if form.validate_on_submit():
        flash('Dank voor de boeking! ')
        return redirect(url_for('/aanbod'))
    return render_template('boek.html', form=form)

@app.route('/logout')
@login_required
def logout():
    # Logout the user
    logout_user()

    flash('Je bent nu uitgelogd!', 'info')
    return redirect(url_for('aanbod'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        if user != None:
            if user.check_password(form.password.data) and user is not None:
                # Log in the user

                login_user(user)
                flash('Succesvol ingelogd!.')

                # If a user was trying to visit a page that requires a login
                # flask saves that URL as 'next'.
                next = request.args.get('next')

                # So let's now check if that next exists, otherwise we'll go to
                # the aanbod page.
                if next == None or not next[0] == '/':
                    next = url_for('home')

                return redirect(next)
        else:
            flash("Gebruiker bestaat niet!")
    return render_template('login.html', form=form)


@app.route('/registreren', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    # Check if form is succesfully submitted.
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Dank voor de registratie. Er kan nu ingelogd worden! ')
            return redirect(url_for('login'))

        except IntegrityError:
            db.session.rollback()
            flash('Gebruikersnaam of e-mail bestaat al!')
            return redirect(url_for('register'))

        except Exception as e:
            print(e)
            return redirect(url_for('register'))

    return render_template('registreren.html', form=form)

@app.route('/bedankt', methods=["POST"])
def bedankt():
    if request.method == "POST":
        if "Bevestigen" in request.form:
            vanaf_datum = request.form["boeking-start"]

            if vanaf_datum != '':
                beschikbare_datum = True
                date_time_obj = datetime.strptime(vanaf_datum, '%Y-%m-%d')
                vanaf_datum = date_time_obj.date()
                tot_datum = vanaf_datum + timedelta(days=7)
                def Convert(string):
                    """ Convert neemt een string als parameter en split deze string bij elke spatie.
                        Vervolgens wordt hier een lijst van gemaakt."""
                    li = list(string.split(" "))
                    return li
                
                data = Convert(request.form["Bevestigen"])
                boeking = Boeking.query.filter_by(bungalow=data[0]).all()
                #Hoeveel boekingen er al zijn in de database voor dezelfde bungalow
                print(f'boeking = {boeking}')
                
                #Filteren op id's van boekingen op dezelfde bungalow
                boeking_id = []
                boeking_van = []
                for x in range(len(boeking)):
                    boeking_date_object = boeking[x].van
                    boeking_id.append(boeking[x].id)
                    print(boeking_date_object)
                    if boeking_date_object == vanaf_datum:
                        beschikbare_datum = False
                id = data[0]
                print(f'boeking_id = {boeking_id}')
                print(f'boeking_van = {boeking_van}') 
                bungalow = Bungalow.query.get(id)
                bungalow_afbeelding = bungalow.afbeelding
                bungalow_naam = bungalow.naam
                bungalow_omschrijving = bungalow.beschrijving
                bungalow_type = bungalow.type
                type = Type.query.get(bungalow_type)
                bungalow_prijs = type.weekprijs
                boeken =f"{id} {bungalow_prijs}"        

                if beschikbare_datum: 
                    id = data[0]
                    prijs = data[1]

                    
                    boeking = Boeking(gast=current_user.get_id(),
                            bungalow=id,
                            prijs=prijs,
                            van=vanaf_datum,
                            tot=tot_datum)
                    db.session.add(boeking)
                    db.session.commit()
    
            else:
                return redirect(url_for('aanbod')), flash('Error, je bent de datum vergeten in te vullen')
    if beschikbare_datum==True:     
        print(True)   
        return render_template('bedankt.html')
    else:
        print(False)
        return render_template('boek.html', bungalow_afbeelding=bungalow_afbeelding,
                                bungalow_naam=bungalow_naam, bungalow_omschrijving=bungalow_omschrijving,
                                bungalow_prijs=bungalow_prijs, boeken=boeken,id = data[0])

@app.route('/mijn-boekingen', methods=['POST', 'GET'])
@login_required
def mijnBoekingen():
    # Vraag id op van de gebruiker
    user = User.query.filter_by(username=current_user.username).all()[0]
    user_id = user.id

    # Zoek boekingen van deze gebruiker
    aantal = Boeking.query.filter_by(gast=user_id).all()
    print(f'aantal = {aantal}')
    # Maak lege lijsten van alle tabellen die een boeking heeft
    naam = []
    van = []
    tot = []
    bungalow_id = []
    prijs = []
    afbeelding = []
    omschrijving = []
    boeking_id = []

    # Voor alle boekingen in de breedte van de boekingen en in de lengte van het aantal, append deze boeking aan de lijsten.
    for i in range(len(aantal)):
        x = Boeking.query.filter_by(gast=user_id).all()[i]
        van.append(x.van)
        tot.append(x.tot)
        bungalow_id.append(x.bungalow)
        prijs.append(x.prijs)
        boeking_id.append(x.id)

        aantal_b = Bungalow.query.filter_by(id=x.id).all()
        for j in range(len(aantal_b)):
            y = Bungalow.query.filter_by(id=x.bungalow).all()[j]
            naam.append(y.naam)
            afbeelding.append(y.afbeelding)
            omschrijving.append(y.beschrijving)



    if request.method == 'POST':
        if request.form["Annuleren"]:
            annuleer_id = request.form["Annuleren"]
            boeking = Boeking.query.get(annuleer_id)
            db.session.delete(boeking)
            db.session.commit()
            return redirect(url_for('mijnBoekingen'))
            


    aantal_b = len(aantal)
    return render_template('mijn_boeking.html', boeking_id=boeking_id, prijs=prijs, aantal=aantal_b, naam=naam, afbeelding=afbeelding, omschrijving=omschrijving, van=van, tot=tot)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)
