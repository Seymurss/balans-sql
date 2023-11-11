import sqlite3
from hashlib import sha256

# SQLite verilənlər bazasına qoşul
conn = sqlite3.connect('banka_veritabani.db')
cursor = conn.cursor()

# İstifadəçi cədvəlini yarat
cursor.execute('''
    CREATE TABLE IF NOT EXISTS istifadəçilər (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        istifadəçi_adı TEXT NOT NULL,
        pin TEXT NOT NULL,
        balans REAL NOT NULL
    )
''')
conn.commit()

# İstifadəçi yaratma
def istifadəçi_yarat(istifadəçi_adı, pin):
    # İstifadəçi adının unikal olduğunu yoxla
    cursor.execute("SELECT * FROM istifadəçilər WHERE istifadəçi_adı=?", (istifadəçi_adı,))
    mövcud_istifadəçi = cursor.fetchone()
    
    if mövcud_istifadəçi is None:
        cursor.execute("INSERT INTO istifadəçilər (istifadəçi_adı, pin, balans) VALUES (?, ?, 0)", (istifadəçi_adı, sha256(pin.encode()).hexdigest()))
        conn.commit()
        print("İstifadəçi yaradıldı.")
    else:
        print("Bu istifadəçi adı artıq istifadə olunur. Başqa bir istifadəçi adı seçin.")

# İstifadəçi girişi
def istifadəçi_girişi():
    istifadəçi_adı = input("İstifadəçi Adınızı daxil edin: ")
    pin = input("PIN kodunuzu daxil edin: ")
    return istifadəçi_adı, pin

# İstifadəçinin mövcudluğunu yoxla
def istifadəçi_varmı(istifadəçi_adı, pin):
    cursor.execute("SELECT * FROM istifadəçilər WHERE istifadəçi_adı=? AND pin=?", (istifadəçi_adı, sha256(pin.encode()).hexdigest()))
    return cursor.fetchone() is not None

# Balansı sorğula
def balans_sorğula(istifadəçi_adı):
    cursor.execute("SELECT balans FROM istifadəçilər WHERE istifadəçi_adı=?", (istifadəçi_adı,))
    balans = cursor.fetchone()
    return balans[0] if balans else None

# Balansdan pul çək
def pul_çək(istifadəçi_adı, məbləğ):
    cursor.execute("SELECT balans FROM istifadəçilər WHERE istifadəçi_adı=?", (istifadəçi_adı,))
    köhnə_balans = cursor.fetchone()[0]

    if köhnə_balans >= məbləğ:
        yeni_balans = köhnə_balans - məbləğ
        cursor.execute("UPDATE istifadəçilər SET balans=? WHERE istifadəçi_adı=?", (yeni_balans, istifadəçi_adı))
        conn.commit()
        return f"{istifadəçi_adı} adlı hesabınızdan {məbləğ} AZN çəkildi. Yeni balans: {yeni_balans} AZN"
    else:
        return "Balans kifayət qədər deyil. Əməliyyat icra edilə bilmədi."

# Balansa pul yatır
def pul_yatır(istifadəçi_adı, məbləğ):
    cursor.execute("SELECT balans FROM istifadəçilər WHERE istifadəçi_adı=?", (istifadəçi_adı,))
    köhnə_balans = cursor.fetchone()[0]
    yeni_balans = köhnə_balans + məbləğ
    cursor.execute("UPDATE istifadəçilər SET balans=? WHERE istifadəçi_adı=?", (yeni_balans, istifadəçi_adı))
    conn.commit()
    return f"{istifadəçi_adı} adlı hesabınıza {məbləğ} AZN yatırıldı. Yeni balans: {yeni_balans} AZN"

# Əsas əməliyyat dövrü
while True:
    print("\n1. Giriş Edin\n2. Qeydiyyatdan Keçin\n")
    seçim = input("Edəcəyiniz əməliyyatı seçin (1-2): ")
    
    if seçim == '1':
        # İstifadəçi girişi
        while True:
            istifadəçi_adı, pin = istifadəçi_girişi()
            if istifadəçi_varmı(istifadəçi_adı, pin):
                print("Giriş uğurlu oldu.")
                break
            else:
                print("Yanlış giriş. Zəhmət olmasa təkrar cəhd edin.")
        
        # Balans əməliyyatları
        while True:
            print("\n1. Balans Sorğula\n2. Pul Çək\n3. Pul Yatır\n4. Çıxış\n")
            seçim = input("Edəcəyiniz əməliyyatı seçin (1-4): ")
            if seçim == '1':
                print("Balansınız:", balans_sorğula(istifadəçi_adı), "AZN")
            elif seçim == '2':
                məbləğ = float(input("Çəkmək istədiyiniz məbləği daxil edin: "))
                print(pul_çək(istifadəçi_adı, məbləğ))
            elif seçim == '3':
                məbləğ = float(input("Yatırmaq istədiyiniz məbləği daxil edin: "))
                print(pul_yatır(istifadəçi_adı, məbləğ))
            elif seçim == '4':
                print("Çıxış edilir. Uğurlar!")
                break
            else:
                print("Yanlış seçim. Zəhmət olmasa təkrar cəhd edin.")
    
    elif seçim == '2':
        # Yeni istifadəçi yaradın
        yeni_istifadəçi_adı = input("Yeni İstifadəçi Adı: ")
        yeni_pin = input("Yeni PIN: ")
        istifadəçi_yarat(yeni_istifadəçi_adı, yeni_pin)
    
    else:
        print("Yanlış seçim. Zəhmət olmasa təkrar cəhd edin.")
