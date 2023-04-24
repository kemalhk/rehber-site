from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    Response,
)
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from .models.user import User, db, Rehber, Adres
from flask_paginate import Pagination, get_page_parameter, get_page_args
from http import HTTPStatus
import math
import hashlib

from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret-key"
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template("login.html")


@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)


# kayıt ol sayfası
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # tekrarlanan kayıt engelleme
        user = User.query.filter_by(username=username).first()
        if user is None:
            # Şifreyi şifreleme
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            kayit = User(username=username, password=hashed_password)
            db.session.add(kayit)
            db.session.commit()
            return redirect(url_for("login"))
        else:
            error = "Kullanıcı adı kayıtlı"
            return render_template("register.html", error=error)
    return render_template("register.html")


# giriş sayfası
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Şifreyi şifreleme
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = User.query.filter_by(username=username, password=hashed_password).first()
        if user is not None:
            login_user(user, remember=True)
            user_id = user.id
            return redirect(url_for("list", user_id=user_id))
        else:
            error = "Kullanıcı adı veya şifre hatalı."
            return render_template("login.html", error=error)
    return render_template("login.html")


# telefon numarası ekleme
@app.route("/addNumber", methods=["GET", "POST"])
@login_required
def addNumber():
    if request.method == "POST":
        ad = request.form["ad"]
        soyad = request.form["soyad"]
        numara = request.form["numara"]
        kayit = Rehber(ad=ad, soyad=soyad, numara=numara)
        db.session.add(kayit)
        db.session.commit()
        mesaj = "Kayıt başarıyla eklendi."
        return redirect(url_for("list"))
        # return render_template("addNumber.html", mesaj=mesaj)
    return render_template("list.html")


# Kayıt silme sayfası
@app.route("/deleteNumber", methods=["GET", "POST"])
@login_required
def deleteNumber():
    if request.method == "POST":
        id = request.form["id"]
        user = Rehber.query.get(id)
        # Rehber modeline bağlı olan Adres modellerini silme
        adresler = Adres.query.filter_by(rehber_id=id).all()
        for adres in adresler:
            db.session.delete(adres)
        db.session.delete(user)
        # db.session.delete(adressil)
        db.session.commit()
        return redirect(url_for("list"))
    return render_template("list.html")


# test
# Kayıt listeleme sayfası
@app.route("/list", methods=["GET", "POST"])
@login_required
def list():
    user_id = request.args.get(
        "user_id"
    )  # profil sayfasında işlem yapabilmek için loginden gelen id yi alıyoruz
    users = Rehber.query.all()
    addresses = Adres.query.all()

    # sayfalama islemi
    sayfa_numarasi = request.args.get(
        "sayfa_numarasi", 1, type=int
    )  # URL'den sayfa numarasını al, varsayılan olarak 1
    sayfa_basi_oge_sayisi = 3
    offset = (sayfa_numarasi - 1) * sayfa_basi_oge_sayisi
    limit = sayfa_basi_oge_sayisi
    users = Rehber.query.offset(offset).limit(limit).all()  #  sayfalara böl
    toplam_oge_sayisi = Rehber.query.count()  # toplam kayıtlar
    toplam_sayfa_sayisi = int(
        math.ceil(toplam_oge_sayisi / sayfa_basi_oge_sayisi)
    )  # Toplam sayfa sayısını hesaplaa

    return render_template(
        "list.html",
        users=users,
        toplam_sayfa_sayisi=toplam_sayfa_sayisi,
        sayfa_numarasi=sayfa_numarasi,
        addresses=addresses,
        user_id=user_id,
    )


# Kayıt güncelleme sayfası
@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    if request.method == "POST":
        id = request.form["id"]
        # Güncellenen kaydı veritabanından al
        guncelle = Rehber.query.get(id)
        if guncelle:
            guncelle.ad = request.form["ad"]
            guncelle.soyad = request.form["soyad"]
            guncelle.numara = request.form["numara"]
            db.session.commit()
            return redirect(url_for("list"))
            # return render_template('list.html',mesaj='kayıt başarıyla güncellendi')
        else:
            return render_template("list.html", hata_mesaj="Kayıt bulunamadı")
    return render_template("list.html")


# adres  sayfası
@app.route("/adres", methods=["GET", "POST"])
@login_required
def adres():
    user_id = request.args.get("user_id")  # URL'den user_id parametresini al
    rehber_id = request.args.get("rehber_id")  # URL'den rehber_id parametresini al
    if rehber_id is None:
        return redirect(url_for("list"))
    user = Rehber.query.filter_by(id=rehber_id).first()  # seçilen kullanıcıyı bul
    addresses = Adres.query.filter_by(rehber_id=rehber_id).all()  # kayıtları listele
    #####################

    # sayfalama islemi
    sayfa_numarasi = request.args.get(
        "sayfa_numarasi", 1, type=int
    )  # URL'den sayfa numarasını al, varsayılan olarak 1
    sayfa_basi_oge_sayisi = 3
    offset = (sayfa_numarasi - 1) * sayfa_basi_oge_sayisi
    limit = sayfa_basi_oge_sayisi
    users = Rehber.query.offset(offset).limit(limit).all()  #  sayfalara böl
    addresses = (
        Adres.query.filter_by(rehber_id=rehber_id).offset(offset).limit(limit).all()
    )  # Sayfalı kayıtları al
    toplam_oge_sayisi = Adres.query.filter_by(
        rehber_id=rehber_id
    ).count()  # toplam kayıt sayısını hesapla
    toplam_sayfa_sayisi = int(
        math.ceil(toplam_oge_sayisi / sayfa_basi_oge_sayisi)
    )  # Toplam sayfa sayısını hesapla

    ########################
    return render_template(
        "adres.html",
        user=user,
        addresses=addresses or [],  # [] adres boş geliyorsa listeleme için
        toplam_sayfa_sayisi=toplam_sayfa_sayisi,
        sayfa_numarasi=sayfa_numarasi,
        user_id=user_id,
        rehber_id=rehber_id,  # yukarıdaki if kontrolünden geçip adres listelemesinde sayfalama işlemi için yolluyor
    )


# adres ekleme
@app.route("/add_adres", methods=["POST"])
def add_adres():
    rehber_id = request.args.get("rehber_id")  # URL'den rehber_id parametresini al
    print(rehber_id)
    user = Rehber.query.filter_by(id=rehber_id).first()  # seçilen kullanıcıyı bul

    adres_adi = request.form["adres_adi"]

    if request.method == "POST":
        print(rehber_id)

        user = Adres.query.filter_by(adres_adi=adres_adi, rehber_id=rehber_id).first()
        if user is None:
            adres_adi = request.form["adres_adi"]
            il = request.form["il"]
            ilce = request.form["ilce"]
            adres = request.form["adres"]
            mail = request.form["mail"]
            yeni_adres = Adres(
                adres_adi=adres_adi,
                il=il,
                ilce=ilce,
                adres=adres,
                mail=mail,
                rehber_id=rehber_id,
            )
            db.session.add(yeni_adres)
            db.session.commit()
            return redirect(url_for("adres", rehber_id=rehber_id))
        else:
            error = " adresi kayıtlı"
            return render_template("adres.html", error=error)
    return redirect(url_for("adres"))


# adres güncelleme sayfası
@app.route("/adresUpdate", methods=["GET", "POST"])
@login_required
def updateAdres():
    if request.method == "POST":
        rehber_id = request.form["rehber_id"]
        print(rehber_id)
        id = request.form["id"]
        print(id)

        kayit = Adres.query.get(rehber_id)  # rehber id ve id den kayıt bulma
        if kayit:
            kayit.adres_adi = request.form["adres_adi"]
            kayit.il = request.form["il"]
            kayit.ilce = request.form["ilce"]
            kayit.adres = request.form["adres"]
            kayit.mail = request.form["mail"]
            db.session.commit()
        return redirect(url_for("adres", rehber_id=id))
    else:
        return render_template("adres.html", hata_mesaj="Kayıt bulunamadı")


# adres silme sayfası
@app.route("/deleteAdres", methods=["GET", "POST"])
@login_required
def deleteAdres():
    rehber_id = request.args.get("id")  # URL'den rehber_id parametresini al
    print(rehber_id)
    if request.method == "POST":
        adres_adi = request.form["adres_adi"]
        adressil = Adres.query.filter_by(
            rehber_id=rehber_id, adres_adi=adres_adi
        ).first()
        if adressil is not None:
            db.session.delete(adressil)
            db.session.commit()
            return redirect(url_for("adres", rehber_id=rehber_id))
    return redirect(url_for("adres", rehber_id=rehber_id))


# profil sayfası
@app.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    user_id = request.args.get("user_id")
    # print(user_id)
    return render_template("profil.html", user_id=user_id)


# profil şifre değiştirme işlemleri
@app.route("/profilsifre", methods=["GET", "POST"])
@login_required
def profilsifre():
    user_id = request.args.get("user_id")
    print(user_id)
    if request.method == "POST":
        kullanici = User.query.filter_by(id=user_id).first()
        if kullanici is not None:
            mevcutSifre = request.form["mevcutSifre"]
            hashed_password = hashlib.sha256(mevcutSifre.encode()).hexdigest()
            yeniSifre = request.form["yeniSifre"]
            yeniSifreTekrar = request.form["yeniSifreTekrar"]
            # şifre hashlib ile şifrelenmeli
            if kullanici.password == hashed_password:
                if yeniSifre == yeniSifreTekrar:
                    # yeni şifreler eşleşiyorsa şifre güncellenmeli
                    # yeni şifre hashlib ile şifrelenmeli ve kaydedilmeli
                    yeniSifre = hashlib.sha256(yeniSifre.encode()).hexdigest()
                    kullanici.password = yeniSifre
                    db.session.commit()
                    return redirect(url_for("adres", user_id=user_id))
                else:
                    error = "Girdiğiniz yeni şifreler uyuşmuyor"
                    return render_template("profil.html", error=error, user_id=user_id)
            else:
                error = "Mevcut şifreniz hatalı"
                return render_template("profil.html", error=error, user_id=user_id)

        else:
            error = "Kullanıcı bulunamadı"
            return render_template("profil.html", error=error, user_id=user_id)


# search
""" @app.route("/fetchrecords", methods=["POST", "GET"])
@login_required
def fetchrecords():
    if request.method == "POST":
        query = request.form["query"]
        if query == "":
            users = Rehber.query.order_by(Rehber.id.desc()).all()
        else:
            search_text = request.form["query"]
            users = (
                Rehber.query.filter(Rehber.office.in_([search_text]))
                .order_by(Rehber.id.desc())
                .all()
            )
        return jsonify({"list": render_template("list.html", users=users)})
    return render_template(
        "list.html"
    )  # Ekranda gösterilecek bir form sayfası döndürebilirsiniz """


# Arama endpointi
@app.route("/arama", methods=["POST", "GET"])
def arama():
    if request.method == "POST":
        ad = request.form["ad"]  # Gelen ad değerini alın
        # Veritabanında ad değerine göre arama yapın ve sonuçları alın
        sonuclar = Rehber.query.filter_by(ad=ad).all()
        # Rehber nesnesini JSON formatına dönüştürün
        sonuclar_json = [rehber.to_dict() for rehber in sonuclar]
        # Sonuçları JSON formatında döndürün
        return jsonify(sonuclar_json)

        """ # Sonuçları HTML formatında döndürmek için bir HTML string oluşturun
        html_string = "<html><body>"
        for rehber in sonuclar:
            html_string += "<p>Ad: {}</p>".format(rehber.ad)

        html_string += "</body></html>"

        # Sonuçları HTML formatında döndürün
        return html_string """
        """ # Sonuçları HTML formatında döndürmek için bir HTML string oluşturun
        html_string = "<html><body>"
        for rehber in sonuclar:
            html_string += "<p>Ad: {}</p>".format(rehber.ad)
            html_string += "<p>Telefon: {}</p>".format(rehber.telefon)
        html_string += "</body></html>"

        # Sonuçları HTML formatında döndürün
        return Response(html_string, content_type="text/html") """

        """ return render_template(
            "adres.html",
            sonuclar=sonuclar or [],  # [] adres boş geliyorsa listeleme için
        ) """


# sayfa içi arama kısımı
# kod olmadan vt oluşmyor sorulucak
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
