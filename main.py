# Required Libraries
import tkinter as tk
from tkinter import messagebox  # Used for creating pop-up windows for messages
from newspaper import Article  # Used for downloading and parsing news articles
from textblob import (
    TextBlob,
)  # Used for performing simple text-based sentiment analysis
from gtts import gTTS  # Google Text-to-Speech, used for converting text into speech
from playsound import playsound  # Used to play sound files
import os  # Used for operating system dependent functionality like file paths
import validators  # Used for validating URLs
import webbrowser  # Used for opening the web browser
from tkinter import (
    filedialog,
    ttk,
    simpledialog,
)  # Used for file dialogs, themed widgets, and simple dialogs

# Import NLTK libraries for natural language processing
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist


# Main class for the news summarizer application
class NewsSummarizerApp:
    def __init__(self, root):
        self.root = root
        # Define supported languages and their corresponding ISO codes
        self.languages = {
            "English": "en",
            "Arabic": "ar",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
        }
        print("Initialized languages:", self.languages)
        # Default language is English
        self.current_language = tk.StringVar(value="English")
        self.setup_ui()

    # Create a dropdown menu for language selection
    def create_language_dropdown(self):
        print("Languages available before creating dropdown:", self.languages)
        lang_label = tk.Label(self.root, text="Select Language")
        lang_label.pack()

        lang_dropdown = ttk.Combobox(self.root, textvariable=self.current_language)
        lang_dropdown["values"] = list(self.languages.keys())
        lang_dropdown["state"] = "readonly"
        lang_dropdown.pack()

    # Setup the user interface
    def setup_ui(self):
        self.root.title("News Summarizer")
        self.root.geometry("1200x720")

        # Add padding to all widgets in the main window
        for widget in self.root.pack_slaves():
            widget.pack_configure(padx=10, pady=10)

        # Setup widgets for displaying the article title, author, publication date, and summary
        # Title
        tlabel = tk.Label(self.root, text="Title")
        tlabel.pack()
        self.title_text = tk.Text(
            self.root, height=1, width=140, bg="#dddddd", state="disabled"
        )
        self.title_text.pack()

        # Author
        alabel = tk.Label(self.root, text="Author")
        alabel.pack()
        self.author_text = tk.Text(
            self.root, height=1, width=140, bg="#dddddd", state="disabled"
        )
        self.author_text.pack()

        # Publication Date
        plabel = tk.Label(self.root, text="Publication Date")
        plabel.pack()
        self.publish_date_text = tk.Text(
            self.root, height=1, width=140, bg="#dddddd", state="disabled"
        )
        self.publish_date_text.pack()

        # Summary with scrollbar
        slabel = tk.Label(self.root, text="Summary")
        slabel.pack()
        summary_frame = tk.Frame(self.root)
        summary_frame.pack()
        self.summary_text = tk.Text(
            summary_frame, height=20, width=130, bg="#dddddd", state="disabled"
        )
        self.summary_text.pack(side=tk.LEFT)
        summary_scroll = tk.Scrollbar(summary_frame, command=self.summary_text.yview)
        summary_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.summary_text["yscrollcommand"] = summary_scroll.set

        # Sentiment
        selabel = tk.Label(self.root, text="Sentiment")
        selabel.pack()
        self.sentiment_text = tk.Text(
            self.root, height=1, width=140, bg="#dddddd", state="disabled"
        )
        self.sentiment_text.pack()

        # Website URL
        ulabel = tk.Label(self.root, text="Website URL")
        ulabel.pack()
        self.url_text = tk.Text(self.root, height=1, width=140)
        self.url_text.pack()

        # Button Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        # Summarize Button
        btn_summarize = tk.Button(btn_frame, text="Summarize", command=self.summarize)
        btn_summarize.pack(side=tk.LEFT, padx=10, pady=10)

        # Clear Button
        btn_clear = tk.Button(btn_frame, text="Clear", command=self.clear_fields)
        btn_clear.pack(side=tk.LEFT, padx=10, pady=10)

        # Speak Summary Button
        btn_speak = tk.Button(
            self.root, text="Speak Summary", command=self.speak_summary
        )
        btn_speak.pack(padx=10, pady=10)

        # Initialize dropdown for language selection
        self.create_language_dropdown()

        # Button to save the summary to a file
        btn_save = tk.Button(btn_frame, text="Save Summary", command=self.save_summary)
        btn_save.pack(side=tk.LEFT, padx=10, pady=10)

        # Button to open the URL in a web browser
        btn_open_url = tk.Button(btn_frame, text="Open URL", command=self.open_url)
        btn_open_url.pack(side=tk.LEFT, padx=10, pady=10)

        # Status Bar
        self.status = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    # Method to initiate the summarization of an article
    def summarize(self):
        url = self.url_text.get("1.0", "end").strip()
        # Validate URL
        if not validators.url(url):
            messagebox.showerror("Error", "Invalid URL. Please enter a valid URL.")
            return

        # Update status bar
        self.status.config(text="Summarizing...")
        try:
            # Create an Article object from the provided URL
            article = Article(url)
            # Download the article's HTML content
            article.download()
            # Parse the article to extract useful information like body text and authors
            article.parse()
            # Perform natural language processing to generate a summary, keywords, etc
            article.nlp()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve article: {str(e)}")
            self.status.config(text="Error!")
            return

        self.display_article_info(article)
        # Update status bar
        self.status.config(text="Done!")

    # Method to display the article information in the UI
    def display_article_info(self, article):
        # Enable the text boxes to modify them
        self.enable_text_widgets()

        # Clear the previous content
        self.clear_fields()

        # Insert the new content from the article
        self.title_text.insert("1.0", article.title)
        authors_text = (
            ", ".join(article.authors) if article.authors else "No author listed"
        )
        self.author_text.insert("1.0", authors_text)
        publish_date_text = (
            article.publish_date.strftime("%Y-%m-%d %H:%M:%S")
            if article.publish_date
            else "No publication date"
        )
        self.publish_date_text.insert("1.0", publish_date_text)
        self.summary_text.insert("1.0", article.summary)

        # Sentiment analysis
        analysis = TextBlob(article.text)
        polarity_percentage = round(analysis.polarity * 100, 2)
        sentiment_text = f"Polarity: {polarity_percentage}%, Sentiment: {'Positive' if analysis.polarity > 0 else 'Negative' if analysis.polarity < 0 else 'Neutral'}"
        self.sentiment_text.insert("1.0", sentiment_text)

        # Disable the text boxes to prevent editing
        self.disable_text_widgets()

    # Method to disable user editing in all text widgets
    def disable_text_widgets(self):
        # Disable the title text widget to prevent user editing
        self.title_text.config(state="disabled")
        # Disable the author text widget to prevent user editing
        self.author_text.config(state="disabled")
        # Disable the publication date text widget to prevent user editing
        self.publish_date_text.config(state="disabled")
        # Disable the summary text widget to prevent user editing
        self.summary_text.config(state="disabled")
        # Disable the sentiment text widget to prevent user editing
        self.sentiment_text.config(state="disabled")

    # Method to enable user editing in all text widgets
    def enable_text_widgets(self):
        # Enable the title text widget to allow data insertion
        self.title_text.config(state="normal")
        # Enable the author text widget to allow data insertion
        self.author_text.config(state="normal")
        # Enable the publication date text widget to allow data insertion
        self.publish_date_text.config(state="normal")
        # Enable the summary text widget to allow data insertion
        self.summary_text.config(state="normal")
        # Enable the sentiment text widget to allow data insertion
        self.sentiment_text.config(state="normal")

    # Method to clear all fields in the interface
    def clear_fields(self):
        # Clear the URL text field
        self.url_text.delete("1.0", "end")
        # Clear the title text field
        self.title_text.delete("1.0", "end")
        # Clear the author text field
        self.author_text.delete("1.0", "end")
        # Clear the publication date text field
        self.publish_date_text.delete("1.0", "end")
        # Clear the summary text field
        self.summary_text.delete("1.0", "end")
        # Clear the sentiment text field
        self.sentiment_text.delete("1.0", "end")
        # Reset the status bar text
        self.status.config(text="")

    def speak_text(self, text):
        try:
            # Retrieve the language code based on the selected language from the dropdown
            lang_code = self.languages[self.current_language.get()]
            # Create a text-to-speech object using the Google text-to-speech API
            tts = gTTS(text=text, lang=lang_code)
            # Temporary filename for storing the audio
            filename = "temp_audio.mp3"
            # Save the spoken text to a file
            tts.save(filename)
            # Play the saved audio file
            playsound(filename)
            # Remove the temporary file after playing to clean up
            os.remove(filename)
        except Exception as e:
            # Display an error message if anything goes wrong during the text-to-speech process
            messagebox.showerror(
                "Error", f"Failed to generate or play speech: {str(e)}"
            )

    def save_summary(self):
        # Open a file dialog to allow the user to save the summary to a file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            # Write the text from the summary text widget to the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.summary_text.get("1.0", tk.END))

    def open_url(self):
        # Get the URL text from the URL text widget
        url = self.url_text.get("1.0", "end").strip()
        # Validate the URL to make sure it is well-formed
        if validators.url(url):
            # Open the URL in a new tab of the default web browser
            webbrowser.open(url, new=2)
        else:
            # Display a warning if the URL is not valid
            messagebox.showwarning("Warning", "Invalid URL. Please enter a valid URL.")

    def speak_summary(self):
        # Get the summary text from the summary text widget
        summary_text = self.summary_text.get("1.0", "end").strip()
        if summary_text:
            # If there is summary text, use the speak_text function to speak it
            self.speak_text(summary_text)
        else:
            # Inform the user that there is no summary to speak
            messagebox.showinfo(
                "Info", "Nothing to speak. Please summarize an article first."
            )


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = NewsSummarizerApp(root)
    root.mainloop()
