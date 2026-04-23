# ຄູ່ມືການຕິດຕັ້ງ (Deploy) mai-english-center ເທິງ Ubuntu 20.04/22.04/24.04 LTS

ຄູ່ມືນີ້ຈະຊ່ວຍໃນການຕິດຕັ້ງໂປຣເຈັກ `mai-english-center` ເທິງເຊີບເວີ (Server) ໂດຍໃຊ້ Apache ແລະ mod_wsgi.

---

## 1. ການຕັ້ງຄ່າ Server ເບື້ອງຕົ້ນ (Initial Server Setup)

ລັອກອິນເຂົ້າເຊີບເວີດ້ວຍ user root:

```bash
ssh root@167.172.81.xxx
```

ອັບເດດລະບົບໃຫ້ເປັນປັດຈຸບັນ:

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

ຕັ້ງຊື່ Hostname (ຊື່ເຄື່ອງ):

```bash
sudo hostnamectl set-hostname mai_centre
sudo hostname
```

ແກ້ໄຂໄຟລ໌ `/etc/hosts`:

```bash
sudo nano /etc/hosts
```

ເພີ່ມແຖວນີ້ກ່ອນແຖວ `127.0.0.1`:

```text
167.172.81.xxx mai_centre
```

*(ກົດ `Ctrl+X` > `Y` > `Enter` ເພື່ອບັນທຶກ)*

## 2. ສ້າງ User ໃໝ່ (Create User)

ສ້າງ user ຊື່ `mai` ສຳລັບຣັນໂປຣເຈັກ:

```bash
sudo adduser mai
# ປ້ອນລະຫັດຜ່ານ ແລະ ຂໍ້ມູນຕາມຂັ້ນຕອນ
```

ເພີ່ມສິດ admin (sudo) ໃຫ້ກັບ user ໃໝ່:

```bash
sudo adduser mai sudo
```

ສະຫຼັບໄປໃຊ້ user ໃໝ່:

```bash
su - mai
```

## 3. ຕັ້ງຄ່າ Firewall (UFW)

```bash
sudo apt-get install ufw
sudo ufw default allow outgoing
sudo ufw default deny incoming
sudo ufw allow 22           # SSH
sudo ufw allow 8000         # ທົດສອບຊົ່ວຄາວ
sudo ufw allow http         # Port 80
sudo ufw allow https        # Port 443
sudo ufw enable
sudo ufw status
```

## 4. ຕິດຕັ້ງ Python ແລະ Virtual Environment

ຕິດຕັ້ງ Python 3 ແລະ venv:

```bash
sudo apt update
sudo apt install python3-pip python3-venv -y
```

ສ້າງ Virtual Environment:

```bash
cd ~
python3 -m venv venv
```

## 5. ອັບໂຫຼດໂປຣເຈັກ (Upload Project)

ອັບໂຫຼດໄຟລ໌ໂປຣເຈັກ (ເນື້ອໃນທີ່ຢູ່ໃນ `backend/core/` ຂອງເຄື່ອງທ່ານ) ໄປໄວ້ທີ່ `/home/mai/mai-english-center`.

**ໂຄງສ້າງໄຟລ໌ໃນເຊີບເວີຄວນເປັນດັ່ງນີ້:**

```bash
/home/mai/
    venv/
    mai-english-center/
        manage.py
        requirements.txt
        core/           # ໂຟນເດີທີ່ເກັບ wsgi.py ແລະ settings
            wsgi.py
            settings/
        ...
```

ຕັ້ງຄ່າເຈົ້າຂອງໄຟລ໌:

```bash
sudo chown -R mai:mai /home/mai/mai-english-center
```

## 6. ຕິດຕັ້ງ Dependencies

```bash
source ~/venv/bin/activate
pip install --upgrade pip
pip install -r /home/mai/mai-english-center/requirements.txt
```

ກວດສອບ Django:

```bash
cd ~/mai-english-center
python manage.py check
```

## 7. ຕັ້ງຄ່າ Django (Django Configuration)

ແກ້ໄຂໄຟລ໌ `core/settings/prod.py` (ຫຼື settings ທີ່ທ່ານໃຊ້):

- ຕັ້ງຄ່າ `ALLOWED_HOSTS = ['167.172.81.xxx', 'mai_centre']`
- ຕັ້ງຄ່າ `STATIC_ROOT = BASE_DIR / 'staticfiles'`

ຮວບຮວມໄຟລ໌ Static:

```bash
python manage.py collectstatic
```

ທົດສອບຣັນ Server:

```bash
python manage.py runserver 0.0.0.0:8000
```

*(ເບິ່ງຜ່ານ Browser ທີ່ `http://167.172.81.xxx:8000` ແລ້ວກົດ `Ctrl+C` ເພື່ອປິດ)*

## 8. ຕິດຕັ້ງ Apache2 ແລະ mod_wsgi

```bash
sudo apt-get install apache2 libapache2-mod-wsgi-py3 -y
sudo a2enmod wsgi
```

ສ້າງໄຟລ໌ Config ສຳລັບ Apache:

```bash
sudo nano /etc/apache2/sites-available/mai-english-center.conf
```

**ວາງໂຄ້ດນີ້ລົງໄປ:**

```apache
<VirtualHost *:80>
    ServerName 167.172.81.xxx

    # Static Files
    Alias /static /home/mai/mai-english-center/staticfiles
    <Directory /home/mai/mai-english-center/staticfiles>
        Require all granted
    </Directory>

    # Media Files
    Alias /media /home/mai/mai-english-center/media
    <Directory /home/mai/mai-english-center/media>
        Require all granted
    </Directory>

    <Directory /home/mai/mai-english-center/core>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    # WSGI Configuration
    WSGIScriptAlias / /home/mai/mai-english-center/core/wsgi.py
    WSGIDaemonProcess mai_app python-path=/home/mai/mai-english-center python-home=/home/mai/venv
    WSGIProcessGroup mai_app

    ErrorLog ${APACHE_LOG_DIR}/mai_error.log
    CustomLog ${APACHE_LOG_DIR}/mai_access.log combined
</VirtualHost>
```

ເປີດໃຊ້ Site:

```bash
sudo a2ensite mai-english-center
sudo a2dissite 000-default.conf
sudo systemctl restart apache2
```

## 9. ຕັ້ງຄ່າ Permission ຂັ້ນສຸດທ້າຍ

```bash
sudo chmod 755 /home/mai
cd /home/mai/mai-english-center
sudo chown :www-data db.sqlite3
sudo chmod 775 db.sqlite3
sudo chown :www-data .
sudo chmod 775 .
sudo chown -R :www-data media
sudo chmod -R 775 media

# ປິດ Port 8000
sudo ufw delete allow 8000
```

---

**ໝາຍເຫດ:** ຖ້າມີຂໍ້ຜິດພາດ ສາມາດກວດເບິ່ງ Log ໄດ້ທີ່: `sudo tail -f /var/log/apache2/mai_error.log`
