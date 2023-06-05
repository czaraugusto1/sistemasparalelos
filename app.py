from flask import Flask, render_template, request, jsonify
import pika

app = Flask(__name__)
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='user_choice', exchange_type='direct')
channel.queue_declare(queue='users')

def write_to_file(filename, message):
    with open(filename, 'a') as file:
        file.write(message + '\n')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        choice = request.form['choice']
        channel.basic_publish(exchange='user_choice', routing_key=choice, body=name)
        return render_template('index.html')
    return render_template('index.html')

@app.route('/free')
def free():
    channel.queue_bind(exchange='user_choice', queue='users', routing_key='free')
    method_frame, header_frame, body = channel.basic_get(queue='users', auto_ack=True)
    users = []
    while body is not None:
        user = body.decode()
        users.append(user)
        write_to_file('users.txt', f'Free: {user}')
        method_frame, header_frame, body = channel.basic_get(queue='users', auto_ack=True)
    return render_template('free.html', users=','.join(users))

@app.route('/paid')
def paid():
    channel.queue_bind(exchange='user_choice', queue='users', routing_key='paid')
    method_frame, header_frame, body = channel.basic_get(queue='users', auto_ack=True)
    users = []
    while body is not None:
        user = body.decode()
        users.append(user)
        write_to_file('users.txt', f'Paid: {user}')
        method_frame, header_frame, body = channel.basic_get(queue='users', auto_ack=True)
    return render_template('paid.html', users=','.join(users))

@app.route('/history')
def history():
    with open('users.txt', 'r') as file:
        users = file.readlines()
    return render_template('history.html', users=users)

if __name__ == '__main__':
    app.run()
