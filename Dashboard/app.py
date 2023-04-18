from flask import Flask, render_template
import boto3
    

client = boto3.resource(service_name = 'dynamodb', region_name = 'us-east-1', 
        aws_access_key_id = '', 
        aws_secret_access_key = '')
table = client.Table('Capstone-DynamoDB')


def get_data():
    data = table.scan()['Items']
    data_sorted = sorted(data, key=lambda time: time['TimeStamp'], reverse=True)

    current_data = data_sorted[0]

    if (current_data['FanStatus'] == True):
        current_data['FanStatus']='ON'
    else:
        current_data['FanStatus'] = 'OFF'

    if (current_data['HeaterStatus'] == True):
        current_data['HeaterStatus']='ON'
    else:
        current_data['HeaterStatus'] = 'OFF'

    if (current_data['SprayStatus'] == True):
        current_data['SprayStatus']='ON'
    else:
        current_data['SprayStatus'] = 'OFF'
    
    return current_data



app = Flask(__name__)

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
    data = get_data()
    return render_template('index.html', date=data['TimeStamp'], fan=data['FanStatus'], heat=data['HeaterStatus'], humid=data['Humidity'], temp=data['Temperature'], spray=data['SprayStatus'])


@app.route('/dashboard')
def data():
    return get_data()


