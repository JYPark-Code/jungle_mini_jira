from flask import Flask, jsonify, render_template
app = Flask(__name__)

@app.route('/')
def home():
  weeks = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

  return render_template(
     "calendar/main.html",
     weeks=weeks
  )

  return render_template('calendar/main.html')

# @app.route('/calendar', method=['GET'])
# def calendar():
#   return jsonify({'result': 'success', 'msg':'msg'})

@app.route('/issues/new', methods=['POST'])
def createIssue():
   return jsonify({
        'title': 'TEST',
        'description': 'TestDes',
        'createdAt': '',
        'due_date': '20250113',
        'status': 'TODO',
        'assigned_id': 'd'
      }
    );


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)