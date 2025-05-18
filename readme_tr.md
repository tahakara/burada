# 📚 RFID Tabanlı Yoklama Sistemi

Bu proje, öğretmenlerin ve öğrencilerin RFID kartları kullanarak yoklama işlemlerini gerçekleştirmesini sağlayan, donanım ve yazılım bileşenlerinden oluşan bir yoklama sistemidir.

<img title="a title" alt="Alt text" src="./misc/images/master_superlight.jpg">


## 🧩 Proje Bileşenleri

### Donanım
- **Arduino Uno** — Cihazın temel kontrol birimi
- **NodeMCU V3 (ESP8266)** — Wi-Fi üzerinden internet bağlantısı
- **RC522 RFID Okuyucu** — Kart okutma işlemi için
- **LED'ler (Kırmızı, Sarı, Yeşil)** — Görsel bildirimler için
- **Buzzer** — Sesli uyarılar için

### Yazılım ve Servisler
- **Python Flask** — Backend servisi (REST API)
- **MySQL** — Veritabanı (öğretmen, öğrenci, cihaz, yoklama bilgileri)
- **Traefik** — Reverse proxy ve load balancer
- **Redis** - Obje depolama
- **Cloudflare** — DNS yönlendirme ve güvenlik
- **Frontend (HTML/CSS/JS)** — Öğretmenler için web paneli



## 📌 Senaryo ve Cihaz Davranışları

### ⏱️ Yoklama Açma (Öğretmen Kartı)
- Eğer yoklama kapalı ise:
  - Kart okutulunca `status: 100` döner.
  - Sırasıyla: **Yeşil → Sarı → Kırmızı LED** 50ms arayla yanar, her LED süresince buzzer çalışır.
  - Yoklama oturumu başlatılır.

- Eğer yoklama açık ise:
  - `status: 000` döner.
  - Sırasıyla: **Kırmızı → Sarı → Yeşil LED** 150ms arayla yanar, buzzer eşlik eder.

### 🧑‍🎓 Öğrenci Kartı
- Eğer yoklama açık değilse:
  - `status: 400` döner.
  - **Kırmızı LED** + buzzer
- Eğer yoklama açıksa:
  - `status: 200` döner.
  - **Yeşil LED** ve **buzzer** 50ms yanar.
- Okunamayan kart:
  - **Sarı LED** 150ms yanıp söner, buzzer eşlik eder.
- Tanınmayan kart:
  - `status: 400` döner.
  - **Kırmızı LED** + buzzer

### 🔚 Yoklama Kapatma (Tekrar Öğretmen Kartı)
- `status: 000` döner.
- Sırasıyla: **Kırmızı → Sarı → Yeşil LED** 150ms, buzzer eşlik eder.
- Yoklama oturumu sonlandırılır.



## 🔁 Veri Akışı ve Altyapı

````

RFID Cihaz (ESP8266)
││
│├──> DNS İsteği
││
│└──> Cloudflare (DNS & SSL)
↓
Traefik Reverse Proxy
↓
Flask Backend API
↓
MySQL

````

- Her cihaz bir UUID ile tanımlıdır.
- POST istekleri `UUID` ve `Kart ID` bilgisi ile backend'e iletilir.
- Traefik, gelen isteği uygun Flask servisine yönlendirir.



## 🌍 Frontend (Öğretmen Paneli)

- Giriş ve kimlik doğrulama
- Ders ve cihaz seçimi
- Yoklama başlat/durdur butonları
- Anlık okutulan öğrencilerin görüntülenmesi
- Geçmiş yoklamaların listelenmesi



## 🔒 Güvenlik Özellikleri

- **Cloudflare ile HTTPS ve DDoS koruması**
- **UUID tabanlı cihaz doğrulama**
- **Role-based erişim (öğretmen/öğrenci)**
- **Veritabanı güvenliği için şifreli bağlantılar**



## 🚀 Kurulum

> Sistem, Docker ile container bazlı kuruluma da uygundur. Aşağıda temel kurulum adımları yer almaktadır.

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
````

### Frontend

Statik dosyalar Traefik altında `/frontend` yoluna yönlendirilir.

### MySQL

Veritabanı yapısını aşağıdaki SQL dosyasından kurabilirsiniz:

```sql
CREATE TABLE users (...);
CREATE TABLE devices (...);
CREATE TABLE attendance (...);
```

---

<br>

## 📈 Geliştirme Potansiyeli

* NFC desteği
* Offline kayıt ve senkronizasyon
* Mobil uygulama entegrasyonu
* Gelişmiş raporlama ve analizler
* MQTT ile daha hızlı mesajlaşma



## 👨‍💻 Katkıda Bulun

Katkılarınızı memnuniyetle karşılıyoruz! Yeni özellik önerileri, bug bildirimleri ve pull request'ler için lütfen [Issues](https://github.com/tahakara/burada/issues) veya [Pull Requests](https://github.com/tahakara/Page/pulls) bölümlerini kullanın.



## 📄 Lisans

MIT Lisansı ile lisanslanmıştır.

<br>
<br>


# 🔧 **Kurulum** 
## IoT Cihaz Kurulumu 

Bu döküman, Arduino + NodeMCU + RC522 RFID donanımı ile çalışan yoklama cihazının kurulumu ve bağlantı detaylarını içerir.



### 📦 Donanım Gereksinimleri

- Arduino Uno
- NodeMCU V3 (ESP8266)
- RC522 RFID Okuyucu
- 3x LED (Kırmızı, Sarı, Yeşil)
- 1x Buzzer
- Jumper kabloları
- 2x 1kΩ direnç (Gerilim bölücü için)



### 🔌 Donanım Bağlantıları

#### Arduino Uno – NodeMCU V3 Bağlantısı

| Arduino | NodeMCU V3  | Açıklama                |
|---------|-------------|-------------------------|
| D2      | D6          | Doğrudan bağlantı       |
| D3      | D7          | **Gerilim bölücü ile**  |
| GND     | G (GND)     | Ortak toprak            |
| 5V      | VIN         | NodeMCU besleme         |
| RST     | RST         | Reset senkronizasyonu   |

> ⚠️ D3-D7 bağlantısında **1kΩ–1kΩ** direnç ile gerilim bölücü kullanmanız gerekir. NodeMCU pinleri 3.3V seviyesinde çalışır.

---

#### Arduino Uno – RC522 RFID Bağlantısı

| Arduino | RC522 | Açıklama        |
|---------|-------|-----------------|
| 3.3V    | 3.3V  | Besleme (3.3V)  |
| GND     | GND   | Toprak          |
| D9      | RST   | Reset pini      |
| D10     | SDA   | SPI Chip Select |
| D11     | MOSI  | SPI veri çıkışı |
| D12     | MISO  | SPI veri girişi |
| D13     | SCK   | SPI saat pini   |

> ⚠️ RC522 modülünün **3.3V** ile beslendiğinden emin olun. 5V kullanılması modüle zarar verebilir.

---

#### Arduino Uno – Göstergeler

| Arduino | Parça       | Açıklama          |
|---------|-------------|-------------------|
| D5      | Buzzer      | Sesli uyarı       |
| D6      | Kırmızı LED | Yanlış/Ret durumu |
| D7      | Sarı LED    | Okunuyor durumu   |
| D8      | Yeşil LED   | Başarılı durum    |

> LED'lere seri direnç (220Ω – 330Ω) bağlanması tavsiye edilir.



### ⚙️ Yazılım Kurulumu

#### Arduino IDE

1. Arduino IDE'yi kurun: https://www.arduino.cc/en/software
2. Gerekli kütüphaneleri yükleyin:
   - `SPI`
   - `MFRC522`
   - `SoftwareSerial` (gerekirse)

#### Arduino Kodunun Yüklenmesi

1. `burada_ardunio.ino` dosyasını açın.
2. Aşağıdaki değerleri güncelleyin:

4. Kartı Arduino'ya yükleyin.
---

#### NodeMCU v3 Kodunun Yüklenmesi

1. `burada_node.ino` dosyasını açın.
2. Aşağıdaki değerleri güncelleyin:

3. NodeMCU üzerinden ESP8266'nın IP adresine bağlandığınızdan emin olun.
4. Kartı Arduino'ya yükleyin.

```cpp
#define WIFI_SSID "ssid"        // WiFi SSID
#define WIFI_PASSWORD "pss"     // WiFi password
#define HOST "sub.example.com"  // Sunucu adresi
#define PORT 443                // HTTPS için varsayılan port
#define IP_PATH "/ip"
#define DATA_PATH "/burada"

#define cookieDust "88888888-4444-4444-4444-121212121212"
#define cookieDevice "88888888-4444-4444-4444-121212121212"
````

---

#### 🌐 NodeMCU (ESP8266) Firmware

NodeMCU, Arduino'dan aldığı veriyi Wi-Fi üzerinden backend'e iletir.

#### Gerekli Ortam

* `ESP8266 Board Manager` (Arduino IDE'ye kurulu)
* `SoftwareSerial` (Arduino → ESP haberleşmesi)

#### Kod Özeti

* ESP8266 D6 ve D7 pinleri ile Arduino'dan veri alır.
* JSON POST isteği yaparak verileri backend'e gönderir.

---

### 🔄 Veri Akışı

1. Kart okutulur.
2. Arduino → ESP8266 üzerinden JSON veri gönderir.
3. ESP8266 → Wi-Fi üzerinden Flask backend'e POST isteği yapar.
4. Backend → JSON formatında yanıt döner (`status: 100`, `200`, `400`, `000`)
5. ESP8266 → Ardunio serial üstünden gelen responsa göre cevap döner.
6. Arduino gelen cevaba göre LED ve buzzer'ı yönetir.

---

### 🧪 Test ve Doğrulama

* Her parça tek tek test edilmelidir (LED, buzzer, kart okuma).
* Kart okutulduğunda seri monitörden POST cevabı gözlemlenebilir.
* LED ve buzzer senaryoları test edilerek doğruluk kontrol edilir.

---

### ⚠️ Notlar

* NodeMCU ve Arduino’nun toprak hatları **ortak** olmalıdır.
* ESP8266 3.3V ile çalıştığı için D3–D7 hattında **gerilim bölücü** zorunludur.
* RC522 doğrudan 5V ile **beslenmemelidir**.

---

## 💻 Sunucu Kurulumu 

Sunucu yapılandırması için minimum 2 çekirdek 2 Gigabyte RAM bulundurunuz.

### 📦 Gereksinimler

- 💻 2 Core 2 RAM VM (Ubuntu whatever)
- 🐋 Docker [*Installation*](https://docs.docker.com/engine/install/ubuntu/) 

---

### 🐋 Docker Kurulum

Run the following command to uninstall all conflicting packages:
``` bash
$ for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
<br>

#### **Install using the apt repository** 
##### *1. Set up Docker's apt repository.*
``` bash
# Add Docker's official GPG key:
$ sudo apt-get update
$ sudo apt-get install ca-certificates curl
$ sudo install -m 0755 -d /etc/apt/keyrings
$ sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
$ sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
$ echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```


##### *2. Install the Docker packages.*

``` bash
# To install the latest version, run:
$ sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

##### *3. Verify that the installation is successful by running the hello-world image:*

``` bash
# This command downloads a test image and runs it in a container. When the container runs, it prints a confirmation message and exits.  
$ sudo docker run hello-world
```

### Running All Services
- **Befor starting services you must replace**:
    - all SSL certs
    - enviroments from ``docker-compose.yaml``
``` bash
# Change directory same as docker-compose.yaml
# Run the `docker-compose.yaml`
$ docker compose -f docker-compose.yaml up -d
```

---

### 📂 Dosya Yapısı

```
/burada
├──
|  └── burada_ardunio/
|      └── burada_ardunio.ino
├──
|  └── burada_node/
|      └── burada_node.ino
|
├──
|  └── server/
|      └── src/
|      └── docker-compose.yaml
|
└── README.md
```

---

### 👨‍🔧 Destek

Sorun bildirimi veya destek için lütfen [Issues](https://github.com/tahakara/burada/issues) sekmesini kullanın.

---
*Created with ❤️ by [GitHub Copilot](https://github.com/features/copilot)*