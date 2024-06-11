from flask import Flask, render_template, request,session
import google.generativeai as genai
import os 


app = Flask(__name__)
# Configurar variable de entorno
clave = os.environ.get('clave')

if not clave:
    raise ValueError("La variable de entorno 'clave' no está definida. Asegúrate de configurarla antes de ejecutar la aplicación.")

app.secret_key = clave  # Usar la clave API como clave de sesión


@app.route('/')
def mostrar_formulario():
    return render_template('formulario.html', error_ms=None, texto_extraido=None, respuesta_generada=None)

#  resolver el problema
@app.route('/resolver', methods=['GET', 'POST'])
def resolver_problema():
    if request.method == 'POST':
        texto_recibido = request.form['mi_texto']
        genai.configure(api_key=clave)

        # Set up the model
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        prompt_parts = [
            "Analiza el siguiente problema y asegúrate de que sea sobre los siguientes temas, (movimiento rectilineo uniformemente variado ,MRU, tiro vertical,tiro parabolico ,movimiento circular uniforme, movimiento circular uniformemente variado ), si es así resuelva el problema, sino de una respuesta como esta, \"el problema solicitado no es posible resolver porque no pertenece a los temas programados\",  y regresa en una lista solo los problemas o temas disponibles para resolver:\neste es el problema,\n",
            texto_recibido,
            "\n",
            "\nPero asegurate que la respuesta sea correcta, aplica bien la aritmetica y algebra y tambien indicame  que formulas estas osando en cada paso y la gravedad siempre sera de 9.8 m/s^2 ,ademas que quiero que hagas las concersiones si es necesario al sistema internacional(metros , segundos , o kilos ) solo si en la pregunta no estan convertidas, y si pertenece a los temas asegurate de ya no mostrarlos, solo muestralo cuando no se el tema correcto, y distinga los pasos, paso 1, paso 2 y los que correspondan",
            "\nY por favor la respuesta puedes mandarlo en un formato para que se pueda formatear facil en el html, no volver a mostrar el listado de temas...q"
        ]

        response = model.generate_content(prompt_parts)
        to_markdown = response.text

        session['respuesta_generada'] = to_markdown

        return render_template('formulario.html', respuesta_generada=to_markdown)
    
    else:
        # Cuando se carga la página (GET), borra la respuesta
        session.pop('respuesta_generada', None)

        return render_template('formulario.html', respuesta_generada=None)

if __name__ == '__main__':
    app.secret_key = clave  # Asegúrate de que 'clave' está definida en tu código

    # Obtener el puerto del entorno o usar el puerto 5000 como predeterminado
    port = int(os.environ.get("PORT", 5000))
    # Ejecutar la aplicación Flask en el puerto especificado
    app.run(host='0.0.0.0', port=port, debug=True)
