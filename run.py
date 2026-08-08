#from app import create_app
#
#app = create_app()
#
#if __name__ == '__main__':
    #app.run(debug=True)
#    app.run(host='0.0.0.0', port=5000, debug=True)
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Render asigna dinámicamente un puerto en producción mediante la variable PORT
    port = int(os.environ.get("PORT", 5000))
    # Es fundamental usar host='0.0.0.0' para que Render detecte la aplicación abierta
    app.run(host="0.0.0.0", port=port)