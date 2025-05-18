#include <SoftwareSerial.h>

#include <ESP8266WiFi.h>

#include <WiFiClientSecure.h>

#include <ArduinoJson.h>  // JSON parsing kütüphanesi

// #define WIFI_SSID "HThere" // WiFi SSID
// #define WIFI_PASSWORD "TCIZKJPE" // WiFi password
#define WIFI_SSID "ssid" // WiFi SSID
#define WIFI_PASSWORD "pass" // WiFi password
#define HOST "sub.example.com" // Sunucu adresi
#define PORT 443 // HTTPS için varsayılan port
#define IP_PATH "/ip"
#define DATA_PATH "/burada"

#define cookieDust "74951a85-31de-11f0-8318-1aebcda1d33f"
#define cookieDevice "7495376e-31de-11f0-8318-1aebcda1d33f"

bool wifiConnected = false;
bool isActivated = true;

SoftwareSerial ardSerial(D7, D6); // RX, TX
WiFiClientSecure client;

struct HttpResponse {
  int statusCode;
  String payload;
};

// POST isteği gönderme fonksiyonu
HttpResponse sendRequest(String method, String path, String body = "") {
  client.setInsecure();

  HttpResponse response;
  response.statusCode = -1;
  response.payload = "";

  if (!client.connect(HOST, PORT)) {
    Serial.println(F("Baglanti basarisiz"));
    return response;
  }

  String cookieHeader = "Cookie: dust=" + String(cookieDust) +
    "; dust-device=" + String(cookieDevice);

  String request = method + " " + path + " HTTP/1.1\r\n" +
    "Host: " + String(HOST) + "\r\n" +
    "User-Agent: ESP8266\r\n" +
    cookieHeader + "\r\n";

  if (method == "POST") {
    request += "Content-Type: application/json\r\n"; // JSON formatı
    request += "Content-Length: " + String(body.length()) + "\r\n";
  }

  request += "Connection: close\r\n\r\n";

  if (method == "POST") request += body;

  client.print(request);

  Serial.println(method + " istegi gonderildi.");

  while (client.connected()) {
    String line = client.readStringUntil('\n');
    if (line.startsWith("HTTP/1.1")) {
      int firstSpace = line.indexOf(' ');
      int secondSpace = line.indexOf(' ', firstSpace + 1);
      response.statusCode = line.substring(firstSpace + 1, secondSpace).toInt();
    }
    if (line == "\r") break;
    // Serial.println(line);
  }

  response.payload = client.readString();
  Serial.println(F("Gelen veri:"));
  Serial.println(response.payload);

  client.stop();
  return response;
}

void connectToWiFi() {
  Serial.print(F("WiFi'ye baglaniliyor: "));
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(F("\nWiFi baglantisi basarili!"));
    Serial.print(F("IP adresi: "));
    Serial.println(WiFi.localIP());
  } else {
    Serial.println(F("\nWiFi baglantisi basarisiz!"));
  }
}

void arduHandShake() {
  bool handshakeDone = false;
  Serial.println(F("Arduino ile handshake baslatildi.\n"));
  while (!handshakeDone) {
    if (ardSerial.available()) {
      String msg = ardSerial.readStringUntil('\n');
      msg.trim();
      if (msg.startsWith("[ARDU SYNC]")) {
        ardSerial.println("[NODE ACK + SYNC]");
        handshakeDone = true;
        Serial.println(F("Arduino ile handshake tamamlandi.\n"));
        break;
      }
    }
    delay(50);
  }
}

void pcSerialStartup() {
  Serial.begin(9600); // PC ile seri iletişimi başlat

  if (!Serial) {
    // Seri port açilmadiysa log yaz ve hiçbir şey yapma
    Serial.println(F("PCSeri port acilamadi."));
    while (!Serial); // Seri port açilana kadar bekle
  }
  Serial.println(F("PCSeri port acildi."));
}

void arduSerialStartup() {
  ardSerial.begin(9600); // Arduino ile haberleşme
}

void serverHendShake() {
  bool requestSuccess = false;

  while (!requestSuccess) {
    connectToWiFi(); // WiFi bağlantısını başlat
    Serial.println(F("WiFi bağlantısı tamamlandi.\n"));

    // HttpResponse getResp = sendRequest("GET", IP_PATH);
    // delay(3000);

    HttpResponse postResp = sendRequest("POST", IP_PATH);

    if (postResp.statusCode == 200) { // && getResp.statusCode == 200) {
      // Başarılı durum — payload'a göre karar ver
      // if (getResp.payload.indexOf("arduinoya-gonder") != -1) {
      //   ardSerial.println(F("[COMMAND_FROM_NODE] LED_ON"));
      // }

      if (postResp.payload.indexOf("reset") != -1) {
        ardSerial.println(F("[COMMAND_FROM_NODE] RESET_DEVICE"));
      }

      requestSuccess = true;
    } else {
      Serial.print(postResp.statusCode);
      Serial.println(F("GET veya POST başarısız. Tekrar denenecek..."));
      WiFi.disconnect();
      delay(3000);
    }
  }
}

void setup() {
  pcSerialStartup();
  arduSerialStartup();
  serverHendShake();
  arduHandShake();
}

void ardunioKeepAlive() {
  bool keepAliveDone = false;

  Serial.println(F("Arduino keepAlive.\n"));
  while (!keepAliveDone) {
    if (ardSerial.available()) {
      ardSerial.println("[NODE ACK + SYNC]");
      keepAliveDone = true;
      Serial.println(F("Arduino keepAlive tamamlandi.\n"));
      break;
    }
    delay(50);
  }
}

String getValue(String input, String key) {
  int startIdx = input.indexOf(key);
  if (startIdx == -1) return "";

  startIdx += key.length();

  int nextIdx = input.length();
  for (String otherKey: {
      "24:",
      "25:",
      "26:"
    }) {
    if (otherKey != key) {
      int i = input.indexOf(otherKey, startIdx);
      if (i != -1 && i < nextIdx) {
        nextIdx = i;
      }
    }
  }

  String result = input.substring(startIdx, nextIdx);
  result.trim();

  if (result.length() != 16) {
    return ""; // Geçersizse boş döner
  }

  return result;
}

void postToServer(String id24, String id25, String id26) {
  client.setInsecure(); // Sertifika doğrulamasını atlamak için

  if (!client.connect(HOST, PORT)) {
    Serial.println(F("Bağlantı başarısız."));
    return;
  }

  // JSON body hazırla
  String jsonBody;
  StaticJsonDocument<200> doc;
  doc["id24"] = id24;
  doc["id25"] = id25;
  doc["id26"] = id26;
  serializeJson(doc, jsonBody);

  // İstek başlığı ve body
  client.println("POST " + String(DATA_PATH) + " HTTP/1.1");
  client.println("Host: " + String(HOST));
  client.println("User-Agent: ESP8266-NodeMCU/1.0 (NodeMCU V3; esp8266; Arduino; en-US) Microcontroller/HTTPClient");
  client.println("Content-Type: application/json");
  client.println("Cookie: dust=" + String(cookieDust) + "; device=" + String(cookieDevice));
  client.print("Content-Length: ");
  client.println(jsonBody.length());
  client.println();  // Header bitişi
  client.println(jsonBody); 

  // Yanıtı oku
  String response = "";
  while (client.connected()) {
    String line = client.readStringUntil('\n');
    if (line == "\r") break; // Header sonu
  }

  String responseBody = client.readString();
  Serial.println("Sunucu yanıtı: "+ responseBody);

  StaticJsonDocument<200> responseDoc;
  DeserializationError err = deserializeJson(responseDoc, responseBody);
  if (err) {
    Serial.println(F("JSON ayrıştırma hatası!"));
    return;
  }

  int status = responseDoc["status"];
  switch (status) {
    case 200:
      ardSerial.println("[OK]\n");
      break;
    case 400:
      ardSerial.println("[DENIED]\n");
      break;
    case 100:
      ardSerial.println("[OPEN]\n");
      break;
    case 0:
      ardSerial.println("[CLOSE]\n");
      break;
    default:
      Serial.println("Bilinmeyen status: " + String(status));
      break;
  }
}

void loop() {
  // Arduino'dan gelen mesajı dinle
  if (ardSerial.available()) {
    String incomingMsg = ardSerial.readStringUntil('\n\n'); // Verinin tamamını al
    incomingMsg.trim(); // Trim boşlukları
    // Serial.println(incomingMsg);

    if (incomingMsg.startsWith("[ARDU SYNC]")) {
      ardSerial.println("[NODE ACK + SYNC]\n");
    }

    if (incomingMsg.startsWith("24:")) {
      // 24: ile başlıyorsa özel formatta veri gelmiş demektir
      String id24 = getValue(incomingMsg, "24:");
      String id25 = getValue(incomingMsg, "25:");
      String id26 = getValue(incomingMsg, "26:");

      if (id24 != "" && id25 != "" && id26 != "") {
        String output = "Hepsi geçerli: ID 24: " + id24 + " ID 25: " + id25 + " ID 26: " + id26;
Serial.println(output);

        postToServer(id24, id25, id26);

      } else {
        Serial.println(F("Hatalı veri! Bir veya daha fazla ID 16 karakter değil."));
      }

    }
  }

  delay(1000);
}