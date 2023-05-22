import json
import boto3
import paho.mqtt.client as mqtt
from datetime import datetime
from decimal import Decimal

mqtt_broker = 'XXXXXXX'  # Alamat broker MQTT
mqtt_port = 1883  # Port broker MQTT
mqtt_topic = 'rumah/+'  # Topik MQTT, menggunakan wildcard '+' untuk menerima semua subtopik yang dimulai dengan 'rumah/'

aws_access_key = 'XXXXXXXXXXXXXX'  # Kunci akses AWS Anda
aws_secret_key = 'XXXXXXXXXXXXXXXXXX'  # Kunci rahasia AWS Anda
s3_bucket = 'XXXXXXXXXXXXXXXXXX'  # Nama bucket AWS S3
s3_region = 'us-west-2'  # Wilayah bucket S3

dynamodb_table = 'XXXXXXXXXXX'  # Nama tabel DynamoDB
dynamodb_region = 'us-east-1'  # Wilayah tabel DynamoDB

mqtt_username = 'XXXXXXXXX'  # Username MQTT
mqtt_password = 'XXXXXXXXX'  # Password MQTT

def on_connect(client, userdata, flags, rc):
    print('Terhubung dengan broker MQTT')
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode('utf-8'))

    # Ekstrak data suhu dan kelembaban dari payload
    suhu = Decimal(str(payload.get('suhu')))
    kelembaban = Decimal(str(payload.get('kelembaban')))

    # Buat nama file dengan timestamp saat ini
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f'{topic}/{timestamp}.json'

    # Simpan data ke AWS S3
    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=s3_region)
    s3_client.put_object(Body=json.dumps(payload), Bucket=s3_bucket, Key=file_name)

    # Simpan data ke DynamoDB
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=dynamodb_region)
    table = dynamodb.Table(dynamodb_table)
    payload['timestamp'] = timestamp  # Tambahkan timestamp ke payload
    payload['suhu'] = suhu  # Konversi suhu ke Decimal
    payload['kelembaban'] = kelembaban  # Konversi kelembaban ke Decimal
    payload['sensor_id'] = topic.split('/')[1]  # Tambahkan kunci sensor_id dari topik MQTT
    table.put_item(Item=payload)

client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)

client.loop_forever()
