#include <SoftwareSerial.h>

#include <SPI.h>

#include <MFRC522.h>

// NodeMCU için seri port tanimlaniyor
SoftwareSerial nodeSerial(2, 3); // RX, TX (pin 2: RX, pin 3: TX)

bool isNodeSending = false;
// SPI için SABITLER tanimlaniyor
#define RST_PIN 9 // Yapilandirilabilir, tipik pin yerleşimine bakiniz
#define SS_PIN 10 // Yapilandirilabilir, tipik pin yerleşimine bakiniz

MFRC522 mfrc522(SS_PIN, RST_PIN); // MFRC522 örneği oluşturuluyor

// LED'lerin ve Buzzer'in pinleri tanimlaniyor
#define BUZZER_PIN 5
#define LED_GREEN_PIN 8
#define LED_YELLOW_PIN 7
#define LED_RED_PIN 6

String blockData[3];
MFRC522::MIFARE_Key key;
bool cardRead = false;

bool isActivated = true;

int melody[] = {
  //Based on the arrangement at https://www.flutetunes.com/tunes.php?id=192
  659,
  16,
  494,
  8
};

void nodeHandShake() {
  // NodeMCU ile handshake başlat
  bool nodeHandshakeDone = false;
  Serial.println(F("NodeMCU ile handshake baslatildi."));
  while (!nodeHandshakeDone) {
    nodeSerial.println("[ARDU SYNC]");
    unsigned long startTime = millis();
    while (millis() - startTime < 2000) { // 2 saniye bekle
      if (nodeSerial.available()) {
        String response = nodeSerial.readStringUntil('\n');
        response.trim();
        if (response.startsWith("[NODE ACK + SYNC]")) {
          nodeHandshakeDone = true;
          Serial.println(F("NodeMCU ile handshake tamamlandi."));
          break;
        }
      }
      delay(50);
    }
    if (!nodeHandshakeDone) {
      Serial.println(F("NodeMCU'dan yanit alinamadi, tekrar deneniyor..."));
      delay(1500);
    }
  }
}

void buzzerPlayTest(int buzzerPin, int tempo) {
  int wholenote = (60000 * 4) / tempo;
  for (int i = 0; i < sizeof(melody) / sizeof(melody[0]); i += 2) {
    int noteDuration = (melody[i + 1] > 0) ? wholenote / melody[i + 1] : (wholenote / abs(melody[i + 1])) * 1.5;
    tone(buzzerPin, melody[i], noteDuration * 0.9);
    delay(noteDuration);
    noTone(buzzerPin);
  }
}

void setLeds(bool green = false, bool yellow = false, bool red = false) {
  digitalWrite(LED_GREEN_PIN, green ? HIGH : LOW); // Yeşil LED  
  digitalWrite(LED_YELLOW_PIN, yellow ? HIGH : LOW); // Sarı LED  
  digitalWrite(LED_RED_PIN, red ? HIGH : LOW); // Kırmızı LED  
}

void startUpLedsBuzzerTest() {
  // LED'leri başlat
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_YELLOW_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  setLeds(1, 1, 1);

  buzzerPlayTest(BUZZER_PIN, 180); // Buzzer çaliyor

  delay(250);
  setLeds(0, 0, 0);
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

void mfrc522Startup() {
  setLeds(1, 1, 1);

  // AA
  SPI.begin();
  // SPI başlatilana kadar bekle
  // while (!SPI.begin()) {
  //   Serial.println(F("SPI baslatilamadi, tekrar deneniyor..."));
  //   delay(500);
  // }

  // AA
  mfrc522.PCD_Init();
  delay(4);

  // MFRC522 başlatilana kadar bekle
  // while (true) {
  //   mfrc522.PCD_Init();
  //   delay(4); // Kart hazir olana kadar bekle
  //   // Kart okuyucu versiyonunu okuyabiliyorsak başlatilmiştir
  //   if (mfrc522.PCD_PerformSelfTest()) {
  //     break;
  //   }
  //   Serial.println(F("MFRC522 baslatilamadi, tekrar deneniyor..."));
  //   delay(500);
  // }

  mfrc522.PCD_DumpVersionToSerial(); // PCD - MFRC522 Kart Okuyucu detaylarini gösterir

  setLeds(1, 1, 0);
  Serial.println(F("MFRC522 baslatildi."));
}

void statusFeedback(int ledPin, int buzzerDuration, bool doubleBeep) {
  digitalWrite(ledPin, HIGH);
  digitalWrite(BUZZER_PIN, HIGH);
  delay(buzzerDuration);

  if (doubleBeep) { // İkinci kisa beep gerekiyorsa
    digitalWrite(BUZZER_PIN, LOW);
    delay(150);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(50);
  }

  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(ledPin, LOW);
}

void nodeStartUp() {
  nodeSerial.begin(9600); // NodeMCU ile haberleşme
  nodeHandShake(); // NodeMCU ile handshake başlat
  setLeds(1, 0, 0);
  statusFeedback(LED_GREEN_PIN, 1000, true);
}

void setup() {
  pcSerialStartup();
  startUpLedsBuzzerTest(); // LED'leri ve Buzzer'i test et
  mfrc522Startup(); // Kart okuyucu başlat
  nodeStartUp(); // Wifi modülü başlat

}

void clearBlockData() {
  /* Okunan Kartın kaydedildiği Bufferı temizler */
  for (int i = 0; i < 3; i++) {
    blockData[i] = "";
  }
}

void setupKeys() {
  /* Kart okumak için gerekli anahtarları ayarlar */
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
}

bool authenticateAndReadBlock(MFRC522 & mfrc522, byte block, byte * data, byte & size) {
  /* 
  Anahtarları kulanarak kartları okur 
  Eğer kart okuma başarısız ise ->
  Eğer kart okuma başarılı ise ->
  */
  MFRC522::StatusCode status = mfrc522.PCD_Authenticate(
    MFRC522::PICC_CMD_MF_AUTH_KEY_B, block, & key, & (mfrc522.uid)
  );

  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("Yetkilendirme hatasi (blok "));
    Serial.print(block);
    Serial.print(F("): "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  }

  status = mfrc522.MIFARE_Read(block, data, & size);
  if (status == MFRC522::STATUS_OK) {
    blockData[block - 24] = "";
    for (byte i = 0; i < 16; i++) {
      blockData[block - 24] += (data[i] >= 32 && data[i] <= 126) ? (char) data[i] : '.';
    }
    return true;
  } else {
    Serial.print(F("Okuma hatasi (blok "));
    Serial.print(block);
    Serial.print(F("): "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  }
}

String * readCardData(MFRC522 & mfrc522) {
  /*
    Kart okumaya hazır olunup olunmadığı 
    Okunduktan sonra return edilecek veriyi ayarlar 
    Kullanıcıya sesli görüntülü uyarı verir
    - Başarılı okuma (Loop içinde kullanıcı bilgilendirilir)
    - Hatalı okuma (Sarı Işık, Ses, 300ms bekleme)
    - Başarısız okuma (Loop içinde kullanıcı bilgilendirilir)
  */
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial() || cardRead)
    return blockData;

  cardRead = true;
  setupKeys(); // Anahtarlari ayarla

  byte data[18];
  byte size = sizeof(data);
  bool allBlocksRead = true;

  for (byte block = 24; block <= 26; block++) {
    if (!authenticateAndReadBlock(mfrc522, block, data, size))
      allBlocksRead = false;
  }

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  // Eğer okuma hatasi varsa yeşil işik yakip 300 ms bekle
  if (!allBlocksRead) {
    clearBlockData();
    cardRead = false; // Kart okuma işlemini sifirla
    statusFeedback(LED_YELLOW_PIN, 300, false); // Türkçe: Okuma hatasi durumunda yeşil LED yanar
  }

  return blockData;
}

void printReadedCard(String * cardData) {
  Serial.print("Kart Okuma Sonucu: Blok 24: ");
  Serial.print(cardData[0]);
  Serial.print(" | Blok 25: ");
  Serial.print(cardData[1]);
  Serial.print(" | Blok 26: ");
  Serial.println(cardData[2]);
}

void nodeKeepAlive() {
  nodeSerial.println("[ARDU SYNC]");
  nodeSerial.readStringUntil("[NODE ACK + SYNC]\n");
}

short sendDataToNode(String * cardData) {
  nodeKeepAlive();
  // String message = "";  
  String message1 = "24:" + cardData[0];
  String message2 = "25:" + cardData[1];
  String message3 = "26:" + cardData[2];

  nodeSerial.print(message1 + message2 + message3);

  nodeSerial.println("\n");

delay(9000);
  String response = nodeSerial.readStringUntil("]\n\n");
  response.trim();

  if (response.equals("[OK]")) {
    return 2;
  } else if (response.equals("[DENIED]")) {
    return 3;
  } else if (response.equals("[OPEN]")) {
    return 1;
  } else if (response.equals("[CLOSE]")) {
    return 0;
  } else {
    return -1;
    // Serial.println("Bilinmeyen yanıt: " + response);
  }
}

void loop() {
  String * cardData = readCardData(mfrc522);

  if (cardRead) { // Sadece bir kez yazdirilmasini sağliyoruz
    digitalWrite(LED_YELLOW_PIN, HIGH);
    short postResponse = -1;
    postResponse = sendDataToNode(cardData);
    delay(5000);
    Serial.println(postResponse);
    switch (postResponse) {
    case 0:
      isActivated = false;
      statusFeedback(LED_RED_PIN, 150, true);
      delay(100);
      statusFeedback(LED_YELLOW_PIN, 50, true);
    digitalWrite(LED_YELLOW_PIN, HIGH);
      
      delay(100);
      statusFeedback(LED_GREEN_PIN, 150, true);
      break;

    case 1:
      isActivated = true;
      statusFeedback(LED_GREEN_PIN, 50, true);
      delay(100);
      statusFeedback(LED_YELLOW_PIN, 50, true);
    digitalWrite(LED_YELLOW_PIN, HIGH);

      delay(100);
      statusFeedback(LED_RED_PIN, 50, true);
      break;

    case 2:
      statusFeedback(LED_GREEN_PIN, 50, true);
    digitalWrite(LED_YELLOW_PIN, HIGH);

      break;
    case 3:
      statusFeedback(LED_RED_PIN, 150, false);
    digitalWrite(LED_YELLOW_PIN, HIGH);

      break;
    }
    digitalWrite(LED_YELLOW_PIN, LOW);

    printReadedCard(cardData);
    clearBlockData();
    cardRead = false; // Eğer bir sonraki okuma için tekrar başlatmak istersen, burada değiştir
  }
  delay(1000);
}