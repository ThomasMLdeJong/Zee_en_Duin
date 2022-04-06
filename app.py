from main import app, db
from flask import render_template, redirect, request, url_for, flash, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from main.models import User, Bungalow, Type, Boeking
from main.forms import LoginForm, RegistrationForm
from datetime import datetime, timedelta
import os
from sqlalchemy.exc import IntegrityError
import random


@app.route('/')
def home():
    rows = Bungalow.query.count()
    bungalow_omschrijving = []
    bungalow_afbeelding = []
    bungalow_prijs = []
    bungalow_naam = []
    bungalow_id = []
    for x in range(3):
        random_n = random.randrange(1, rows)
        bungalow = Bungalow.query.get(random_n)
        bungalow_id.append(bungalow.id)
        bungalow_naam.append(bungalow.naam)
        bungalow_omschrijving.append(bungalow.beschrijving)
        bungalow_afbeelding.append(bungalow.afbeelding)
        bungalow_type = bungalow.type
        type = Type.query.get(bungalow_type)
        bungalow_prijs.append(type.weekprijs)
    return render_template('index.html', bungalow_id=bungalow_id, bungalow_afbeelding=bungalow_afbeelding, bungalow_naam=bungalow_naam, bungalow_omschrijving=bungalow_omschrijving, bungalow_prijs=bungalow_prijs)


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
        
@app.route('/boek', methods=['GET', 'POST'])
@login_required
def boek():
    # Check of de request methode POST is
    if request.method == "POST":
        # Check of request.form bevestigen is
        if "Bevestigen" in request.form:
            # Selecteer vanaf_datum
            vanaf_datum = request.form["boeking-start"]

            # Controleer of vanaf_datum niet leeg is.
            if vanaf_datum != '':
                beschikbare_reservatie = True

                # Strip vanaf_datum
                date_time_obj = datetime.strptime(vanaf_datum, '%Y-%m-%d')
                # Krijg alleen de datum van ons tijd_object
                vanaf_datum = date_time_obj.date()
                # tot_datum
                tot_datum = vanaf_datum + timedelta(days=7)
                
                # Vraag bungalow_id op uit POST bericht
                geboekte_bungalow_id = int(request.form['Bevestigen'])

                # vraag alle boekingen op met dezelfde bungalow
                boeking = Boeking.query.filter_by(bungalow=geboekte_bungalow_id).all()
                reservatie_data = [] 
                for y in range(0,8):
                    reservatie_data.append(vanaf_datum + timedelta(days=y))

                # Creeër lege lijst voor boeking_id's
                boeking_id = []
                gereserveerde_data = []
                # Filteren op id's van boekingen op dezelfde bungalow
                for x in range(len(boeking)):
                    boeking_date_object = boeking[x].van
                    for z in range(0,8):
                        gereserveerde_data.append(boeking_date_object+timedelta(days=z))
                    for p in reservatie_data:
                        if p in gereserveerde_data:
                            beschikbare_reservatie = False
                    boeking_id.append(boeking[x].id)


                # Als beschikbare_datum True is, dan gaan we de boeking maken.
                if beschikbare_reservatie:
                    bungalow = Bungalow.query.filter_by(id=geboekte_bungalow_id).first()
                    type = bungalow.type
                    id = bungalow.id
                    prijs_object = Type.query.filter_by(id=type).first()
                    prijs = prijs_object.weekprijs
                    boeking = Boeking(gast=current_user.get_id(),
                            bungalow=id,
                            prijs=prijs,
                            van=vanaf_datum,
                            tot=tot_datum)
                    db.session.add(boeking)
                    db.session.commit()
                    return render_template('bedankt.html')
                else:
                    # Datum niet beschikbaar, GET request naar /boek met bungalow id + flash bericht
                    bungalow = request.form['Bevestigen']
                    return redirect(url_for('boek', bungalow=bungalow)), flash(f"Datum {request.form['boeking-start']} is al geboekt!")
            else:
                # Datum vergeten in te vullen, GET request naar /boek met bungalow id + flash bericht
                bungalow = request.form['Bevestigen']
                return redirect(url_for('boek', bungalow=bungalow)), flash("Je bent vergeten een datum in te vullen!")
    else:
        # GET request, vraag bungalow informatie op van database.
        id = request.args.get("bungalow")
        bungalow = Bungalow.query.get(id)
        bungalow_id = bungalow.id
        bungalow_afbeelding = bungalow.afbeelding
        bungalow_naam = bungalow.naam
        bungalow_omschrijving = bungalow.beschrijving
        bungalow_type = bungalow.type
        return render_template("boek.html", bungalow=bungalow_id, bungalow_afbeelding=bungalow_afbeelding, bungalow_naam=bungalow_naam, 
                                    bungalow_omschrijving=bungalow_omschrijving, bungalow_type=bungalow_type)


@app.route('/logout')
@login_required
def logout():
    # Log onze gast uit
    logout_user()

    flash('Je bent nu uitgelogd!', 'info')
    return redirect(url_for('/'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Verkrijg gast van User model
        user = User.query.filter_by(email=form.email.data).first()

        if user != None:
            # Check of gegeven wachtwoord overeen komt met onze gast.
            if user.check_password(form.password.data):
                # Log onze gast in
                login_user(user)
                flash('Succesvol ingelogd!.')

                # Als een gebruiker een pagina wilt bekijken die login required is,
                # flask slaat de URL op als 'next'.
                next = request.args.get('next')

                # Check of die url bestaat, ga anders naar de home pagina
                if next == None or not next[0] == 'home':
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

@app.route('/bedankt')
@login_required
def bedankt():
        return render_template('bedankt.html')

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

            if int(annuleer_id) not in boeking_id:
                flash("Dat is niet jouw boeking")
            else:
                boeking = Boeking.query.get(annuleer_id)
                db.session.delete(boeking)
                db.session.commit()
                return redirect(url_for('mijnBoekingen'))
            
    aantal_b = len(aantal)

    if aantal_b == 0:
        nul_boekingen = True
    else:
        nul_boekingen = False

    return render_template('mijn_boeking.html', nul_boekingen=nul_boekingen, boeking_id=boeking_id, prijs=prijs, aantal=aantal_b, naam=naam, afbeelding=afbeelding, omschrijving=omschrijving, van=van, tot=tot)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)
