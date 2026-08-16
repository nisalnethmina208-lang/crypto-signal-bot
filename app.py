from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!-- මෙතැනට මම උඩින් දුන්න HTML Code එක සම්පූර්ණයෙන්ම Paste කරන්න -->
    '''

if __name__ == '__main__':
    app.run()
