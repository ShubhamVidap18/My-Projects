from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get user inputs from the form
        topic = request.form["topic"]
        duration = int(request.form["days"])

        # Generate the query
        query = f"Explain {topic} for {duration} days. Explain in plain text only, in day by day systematic bullet points manner"

        # Configure API key
        genai.configure(api_key="AIzaSyBUvWpceqDAm4bHQMUMyH4aJl2sJ7DZjnY")
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Generate content
        response = model.generate_content(query)

        # Return the response to the HTML page
        return render_template("index1.html", topic=topic, duration=duration, response=response.text)

    return render_template("index1.html", response=None)


if __name__ == "__main__":
    app.run(debug=True)
