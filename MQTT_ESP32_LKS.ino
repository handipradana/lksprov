#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// Konfigurasi WiFi
const char* ssid = "SERVER 00";
const char* password = "Bismillah99";

// Konfigurasi MQTT
const char* mqtt_server = "35.86.171.0";
const int mqtt_port = 1883;
const char* mqtt_username = "pradana";
const char* mqtt_password = "123456";
const char* mqtt_topic = "rumah/dht22";

// Konfigurasi DHT
#define DHT_PIN 15
#define DHT_TYPE DHT11
DHT dht(DHT_PIN, DHT_TYPE);

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected, IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect_mqtt() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT Broker...");
    if (client.connect("ESP32Client", mqtt_username, mqtt_password)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  dht.begin();
}

void loop() {
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();
  
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor");
    return;
  }
  
  String payload = "{\"suhu\":" + String(temperature) + ", \"kelembaban\":" + String(humidity) + "}";
  char msgBuffer[100];
  payload.toCharArray(msgBuffer, 100);
  
  Serial.print("Publishing message: ");
  Serial.println(msgBuffer);
  client.publish(mqtt_topic, msgBuffer);
  
  delay(5000);
}
