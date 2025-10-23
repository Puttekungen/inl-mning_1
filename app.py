from flask import Flask, redirect, render_template, request, session, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # TODO: Ändra detta till en slumpmässig hemlig nyckel

# Databaskonfiguration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Ändra detta till ditt MySQL-användarnamn
    'password': '',  # Ändra detta till ditt MySQL-lösenord
    'database': 'inlamning_1'  # TODO: Ändra detta till ditt databasnamn
}
# hel
def get_db_connection():
    """Skapa och returnera en databasanslutning"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Fel vid anslutning till MySQL: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    # hantera POST request från inloggningsformuläret
    if request.method == 'POST':
        username = request.form.get('username')        
        password = request.form.get('password')
        # Anslut till databasen
        connection = get_db_connection()
        if connection is None:
            return "Databasanslutning misslyckades", 500
        
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Fråga för att kontrollera om användare finns med matchande användarnamn
            query = "SELECT * FROM users WHERE username = %s"
            
            cursor.execute(query, (username,))
            user = cursor.fetchone()

            if user is None:
                return ("Ogiltigt användarnamn eller lösenord", 401)
            
            # Kontrollera om användaren fanns i databasen och lösenordet är korrekt.
            # Om lösenordet är korrekt så sätt sessionsvariabler och skicka tillbaka en hälsning med användarens namn.
            # Om lösenordet inte är korrekt skicka tillbaka ett felmeddelande med http-status 401.
            if user['username'] == username and user['password'] == password:
                # Inloggning lyckades - spara användarinfo i session
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['name'] = user['name']
                return render_template('index.html', user=user)
            else:
                # Inloggning misslyckades, skicka http status 401 (Unauthorized)
                return ('Ogiltigt användarnamn eller lösenord', 401)

        except Error as e:
            print(f"Databasfel: {e}")
            return "Databasfel inträffade", 500
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)