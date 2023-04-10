from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from .models.user import User,db,Rehber

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key'
db.init_app(app)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #tekrarlanan kayıt engelleme
        user = User.query.filter_by(username=username).first()
        if user is  None:
            kayit = User(username=username, password=password)
            db.session.add(kayit)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            error = 'Kullanıcı adı kayıtlı'
            return render_template('register.html', error=error)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user is not None:
            return redirect(url_for('rehber'))
        else:
            error = 'Kullanıcı adı veya şifre hatalı.'
            return render_template('login.html', error=error)
    return render_template('login.html')


#giriş yaptıkdan sonraki sayfa
@app.route('/rehber', methods=['GET', 'POST'])
def rehber():
    return render_template('rehber.html')


@app.route('/addNumber', methods=['GET', 'POST'])
def addNumber():
    if request.method == 'POST':
        ad = request.form['ad']
        soyad = request.form['soyad']
        telefon = request.form['telefon']
        kayit = Rehber(ad=ad, soyad=soyad, telefon=telefon)
        db.session.add(kayit)
        db.session.commit()
        return render_template('addNumber.html', mesaj='Kayıt başarıyla eklendi.')
    return render_template('addNumber.html')

# Kayıt silme sayfası
@app.route('/deleteNumber', methods=['GET', 'POST'])
def deleteNumber():
    users = Rehber.query.all()
    return render_template('deleteNumber.html', users=users)

# Kayıt listeleme sayfası
@app.route('/list', methods=['GET', 'POST'])
def list():
    users = Rehber.query.all()
    return render_template('list.html', users=users)

# Kayıt güncelleme sayfası
@app.route('/update', methods=['GET', 'POST'])
def update():
    users = Rehber.query.all()
    return render_template('update.html', users=users)
    


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
