from flask import Flask, render_template, request
import google.generativeai as genai

# Configure the Gemini API with your API key
genai.configure(api_key="AIzaSyBUvWpceqDAm4bHQMUMyH4aJl2sJ7DZjnY")
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize Flask app
app = Flask(__name__)

# Function to get translations using Gemini API
def get_translation(sanskrit_text, target_language):
    try:
        query = (
            f"Translate the following Sanskrit text into {target_language}. Provide a clear and plain explanation. \
            Also provide output in HTML tabular format, add bootstrap classes to table tags, first row must contain actual meaning and next multiple rows must contain \
            meaning of each sanskrit word one below the other row "
            f"Additionally, include the word-by-word meanings in English, with each word's meaning displayed on a new line. "
            f"Strictly avoid generating any other expalination or information apart from html table tags\n"
            f"Sanskrit Text: {sanskrit_text}"
        )
        response = model.generate_content(query)
        resp = response.text[7:]
        resp = resp[:-4]
        return resp
    except Exception as e:
        return f"An error occurred while fetching the translation: {str(e)}"

# Home route to render the input form
@app.route("/", methods=["GET", "POST"])
def home():
    translation = None
    sanskrit_text = ""
    if request.method == "POST":
        # Get input from the form
        sanskrit_text = request.form.get("sanskrit_text", "")
        language_choice = request.form.get("language", "english")

        # Map the user's choice to the respective language
        language_map = {
            "english": "English",
            "hindi": "Hindi",
            "marathi": "Marathi",
            "telugu": "Telugu",
            "kannada": "Kannada"
        }
        selected_language = language_map.get(language_choice, "English")

        # Get translation using Gemini API
        translation = get_translation(sanskrit_text, selected_language)
        # Redirect to the AI Sanskrit page to display translation
        return render_template("ai_sanskrit.html", sanskrit_text=sanskrit_text, translation=translation)


    return render_template("index.html", sanskrit_text=sanskrit_text, translation=translation)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
