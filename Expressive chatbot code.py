import tkinter as tk
import cv2
from deepface import DeepFace
import random

class FaceExpressionChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Expression Chatbot")
        self.root.geometry('1000x1000')

        # Interface Designs
        self.interface_designs = [
            {"bg": '#FFD700', "fg": 'black', "button_bg": '#FFD700', "button_fg": 'darkred'},
            {"bg": 'goldenrod', "fg": 'black', "button_bg": 'yellow', "button_fg": 'darkgreen'},
            {"bg": 'blue', "fg": 'black', "button_bg": 'yellow', "button_fg": 'indigo'},
            {"bg": 'darkred', "fg": 'black', "button_bg": 'yellow', "button_fg": 'darkred'},
            {"bg": '#FFD700', "fg": 'black', "button_bg": 'yellow', "button_fg": 'goldenrod'}
        ]

        self.apply_random_design()

        # Start Page
        self.start_frame = tk.Frame(self.root, bg=self.bg)
        self.start_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.title_label = tk.Label(self.start_frame, text="", font=("Baloo Bhai", 24, "bold"), bg=self.bg, fg=self.fg)
        self.title_label.grid(row=0, columnspan=2, pady=20)

        self.animate_text("HEY BUJJI HERE!")

        self.name_label = tk.Label(self.start_frame, text="What's your name :", font=("Baloo Bhai", 16), bg=self.bg, fg=self.fg)
        self.name_label.grid(row=1, column=0, padx=10, pady=10)

        self.name_entry = tk.Entry(self.start_frame, font=("Baloo Bhai", 14), width=30,borderwidth=2, relief=tk.RAISED)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)

        self.start_button = tk.Button(self.start_frame, text="Let's Start ", command=self.start_chat, font=("Baloo Bhai", 16), bg=self.button_bg, fg=self.button_fg)
        self.start_button.grid(row=2, columnspan=2, pady=20)

        # Chat Page
        self.chat_frame = tk.Frame(self.root, bg=self.bg)

        self.chat_window = tk.Text(self.chat_frame, bg='white', fg='black', font=("Baloo Bhai", 14), wrap=tk.WORD, height=15, width=60)
        self.chat_window.grid(row=0, columnspan=2, pady=10, padx=10)

        self.user_input = tk.Entry(self.chat_frame, font=("Baloo Bhai", 14), width=50)
        self.user_input.grid(row=1, column=0, pady=10, padx=10)

        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.get_response, font=("Baloo Bhai", 14), bg=self.button_bg)
        self.send_button.grid(row=1, column=1, pady=10, padx=10)

        # Responses for each emotion
        self.responses = {
            "happy": self.generate_happy_responses(),
            "sad": self.generate_sad_responses(),
            "surprised": self.generate_surprised_responses(),
            "disgust": self.generate_disgust_responses(),
            "feared": self.generate_feared_responses(),
            "angry": self.generate_angry_responses(),
            "neutral": self.generate_neutral_responses()
        }

        # Dictionary to track used responses
        self.used_responses = {
            "happy": [],
            "sad": [],
            "surprised": [],
            "disgust": [],
            "feared": [],
            "angry": [],
            "neutral": []
        }

    def apply_random_design(self):
        design = random.choice(self.interface_designs)
        self.bg = design["bg"]
        self.fg = design["fg"]
        self.button_bg = design["button_bg"]
        self.button_fg = design["button_fg"]
        self.root.configure(bg=self.bg)

    def animate_text(self, text, index=0):
        if index < len(text):
            self.title_label.config(text=self.title_label.cget("text") + text[index])
            self.root.after(100, self.animate_text, text, index + 1)

    def start_chat(self):
        self.user_name = self.name_entry.get()
        self.start_frame.place_forget()
        self.chat_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.title_label.configure(text=f"Hello, {self.user_name}!")

        self.detect_expression()

    def detect_expression(self):
        # Open the webcam
        cap = cv2.VideoCapture(0)

        detected_emotion = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detect face expression
            try:
                result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                detected_emotion = result[0]['dominant_emotion']
                break  # Exit after detecting the emotion
            except Exception as e:
                print(f"Error: {e}")
                continue

            # Display the frame
            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if detected_emotion:
            self.start_chatbot(detected_emotion)
        else:
            self.start_chatbot('neutral')  # Default emotion if detection fails

    def start_chatbot(self, emotion):
        self.emotion = emotion
        self.chat_window.insert(tk.END, f"Bujji: Hello {self.user_name}, why are you feeling {self.emotion} today?\n")

    def get_response(self):
        user_text = self.user_input.get()
        self.chat_window.insert(tk.END, f"You: {user_text}\n")

        # Handle special case for contradictory responses
        new_emotion = self.check_for_new_emotion(user_text, self.emotion)
        if new_emotion:
            self.emotion = new_emotion
            bot_response = self.get_unique_response(self.emotion)
            self.chat_window.insert(tk.END, f"Bujji: It seems like you're feeling {self.emotion} now. {bot_response}\n")
        else:
            bot_response = self.get_unique_response(self.emotion)
            self.chat_window.insert(tk.END, f"Bujji: {bot_response}\n")

        self.user_input.delete(0, tk.END)

    def get_unique_response(self, emotion):
        responses = self.responses.get(emotion, self.generate_neutral_responses())
        available_responses = [resp for resp in responses if resp not in self.used_responses[emotion]]

        if not available_responses:
            # If all responses are used, regenerate responses
            available_responses = responses
            self.used_responses[emotion] = []

        response = random.choice(available_responses)
        self.used_responses[emotion].append(response)
        return response

    def check_for_new_emotion(self, user_text, emotion):
        contradiction_map = {
            "happy": ["not happy", "sad", "angry", "upset"],
            "sad": ["not sad", "happy", "excited"],
            "surprise": ["not surprised", "knew it", "expected"],
            "disgust": ["not disgusted", "okay", "fine"],
            "feared": ["not scared", "brave", "fearless", "happy"],
            "angry": ["not angry", "calm", "relaxed", "happy"],
            "neutral": ["not neutral", "happy", "sad", "angry"]
        }
        for contradiction in contradiction_map.get(emotion, []):
            if contradiction in user_text.lower():
                if contradiction in ["happy", "not sad", "excited"]:
                    return "happy"
                elif contradiction in ["not happy", "sad", "upset"]:
                    return "sad"
                elif contradiction in ["angry"]:
                    return "happy"
                elif contradiction in ["calm", "relaxed"]:
                    return "neutral"
                elif contradiction in ["not scared", "brave", "fearless","not feared"]:
                    return "neutral"
                elif contradiction in ["not surprised", "knew it", "expected"]:
                    return "neutral"
                elif contradiction in ["not disgusted", "okay", "fine"]:
                    return "neutral"
        return None

    def generate_happy_responses(self):
        return [
            "That's great to hear!",
            "I'm glad to share happiness with you",
            "I'm so happy for you!",
            "Enjoy your happiness!",
            "You deserve it!",
            "Amazing news!",
            "I'm excited for you!",
            "Keep spreading the joy!",
            "Today is your day!",
            "What a wonderful moment!",
            "Tell me more about what made you happy.",
            "What's your secret to being happy?",
            "I'm smiling just hearing about it!",
            "You're making my day brighter too!",
            "Happiness looks good on you!",
            "Keep up the positive vibes!",
            "Your happiness is contagious!",
            "Let's celebrate your good news!",
            "Wishing you continued happiness!",
            "You're a ray of sunshine today!",
            "You look absolutely radiant! What's making you so happy?",
            "That's wonderful to hear! Did something special happen?",
            "I'm so glad to hear you're happy! Tell me, what made your day?",
            "It's great to see you so cheerful! Anything exciting going on?",
            "Your happiness is contagious! Care to share the good news?",
            "I love hearing that you're happy! What's the reason for your joy?",
            "Fantastic! What’s the highlight of your day?",
            "You're radiating happiness! What's the secret behind your smile?",
            "Such positive vibes! Did something amazing happen?",
            "Seeing you happy makes my day! What's the good news?",
            "I'm thrilled for you! Can you tell me more about it?",
            "Happiness suits you! What's bringing you so much joy today?",
            "That's fantastic! What’s been going on?",
            "It's awesome to see you happy! What's the story behind it?",
            "Good vibes only! What’s making you so happy today?",
            "Your smile is lighting up the room! What’s the happy occasion?",
            "It’s great to hear you’re doing well! What's making you smile?",
            "That’s brilliant news! What happened?",
            "You seem over the moon! What’s got you in such high spirits?",
            "Awesome! What’s been the best part of your day?",
            "Such joy! Can you tell me what’s making you so happy?"
        ]

    def generate_sad_responses(self):
        return [
            "I'm sorry to hear that.",
            "I'm here for you.",
            "Things will get better, I promise.",
            "Sending you hugs.",
            "It's okay to feel this way.",
            "You're not alone in this.",
            "Take your time to process it.",
            "I'm listening if you want to talk more.",
            "Sending positive thoughts your way.",
            "Sometimes it's okay not to be okay.",
            "I wish I could help more.",
            "I understand, it's tough.",
            "Let me know if there's anything I can do.",
            "You're strong, you'll get through this.",
            "This too shall pass.",
            "Remember, you're loved and valued.",
            "You've got a friend in me.",
            "I'm holding space for your feelings.",
            "I'm here to support you.",
            "You're allowed to feel sad."
             "I'm sorry to hear that. What happened?",
            "That sounds really unpleasant. Do you want to talk about it?",
            "I can understand why you'd feel that way. What happened?",
            "That must have been tough. Can you tell me more?",
            "I can imagine how you'd feel. What led to this?",
            "That sounds terrible. Do you want to share more?",
            "I'm here to listen. What happened?",
            "That must have been hard. Can you tell me more?",
            "I can see why you're upset. What happened?",
            "That sounds really unpleasant. Do you want to talk about it?",
            "I understand your reaction. What led to it?",
            "That must have been difficult. Can you tell me more?",
            "I'm here for you. What happened?",
            "That sounds upsetting. Do you want to share more?",
            "I can understand your feelings. What happened?",
            "That must have been tough to deal with. Can you tell me more?",
            "I'm sorry you had to go through that. What happened?",
            "That sounds like a bad experience. Do you want to talk about it?",
            "I can imagine how you'd feel. What led to this?",
            "That sounds really tough. Can you tell me more?"
        ]

    def generate_surprised_responses(self):
        return [
            "Wow, that's unexpected!",
            "I didn't see that coming!",
            "What a surprise!",
            "That's quite a shock!",
            "You've caught me off guard!",
            "I'm pleasantly surprised!",
            "How exciting!",
            "Surprises are the best!",
            "I love surprises!",
            "That's a twist!",
            "Unexpected but wonderful!",
            "That made my day!",
            "I'm intrigued!",
            "Surprise, surprise!",
            "You've amazed me!"
            "Wow, that's quite something! What happened?",
            "I didn't see that coming! Can you tell me more?",
            "That's amazing! How did it happen?",
            "That's surprising! What led to this?",
            "Wow, that's unexpected! Tell me more.",
            "What a surprise! How did it come about?",
            "That's incredible! What happened?",
            "That must have been quite a shock! What led to it?",
            "What an interesting turn of events! How did it happen?",
            "That's fascinating! Can you tell me more?",
            "What a twist! What happened?",
            "I didn't expect that! How did it come about?",
            "That's pretty surprising! What led to this?",
            "That's quite an event! Tell me more.",
            "I'm amazed! What happened?",
            "That's quite a story! How did it happen?",
            "What a turn of events! Can you tell me more?",
            "That's really surprising! What led to it?",
            "What an unexpected surprise! How did it come about?",
            "That's really something! Tell me more."
            
        ]

    def generate_disgust_responses(self):
        return [
            "I understand why you might feel disgusted.",
            "That sounds unpleasant.",
            "I can see why that would bother you.",
            "It’s okay to feel that way.",
            "I get it, that doesn’t sound nice.",
            "That’s a perfectly normal reaction.",
            "It’s natural to feel that disgust.",
            "You have every right to feel that way.",
            "You’re allowed to feel disgusted.",
            "That’s totally understandable."
            "I'm sorry to hear that. What happened?",
            "That sounds really unpleasant. Do you want to talk about it?",
            "I can understand why you'd feel that way. What happened?",
            "That must have been tough. Can you tell me more?",
            "I can imagine how you'd feel. What led to this?",
            "That sounds terrible. Do you want to share more?",
            "I'm here to listen. What happened?",
            "That must have been hard. Can you tell me more?",
            "I can see why you're upset. What happened?",
            "That sounds really unpleasant. Do you want to talk about it?",
            "I understand your reaction. What led to it?",
            "That must have been difficult. Can you tell me more?",
            "I'm here for you. What happened?",
            "That sounds upsetting. Do you want to share more?",
            "I can understand your feelings. What happened?",
            "That must have been tough to deal with. Can you tell me more?",
            "I'm sorry you had to go through that. What happened?",
            "That sounds like a bad experience. Do you want to talk about it?",
            "I can imagine how you'd feel. What led to this?",
            "That sounds really tough. Can you tell me more?"
        ]

    def generate_feared_responses(self):
        return [
            "I’m sorry you’re feeling scared.",
            "It’s okay to feel afraid sometimes.",
            "Fear is a normal emotion.",
            "I’m here to help you feel safe.",
            "Take a deep breath, you’re okay.",
            "Fear can be overwhelming, but it won’t last forever.",
            "You’re stronger than your fears.",
            "I’m here to listen if you want to talk about it.",
            "You’re not alone in feeling this way.",
            "I’m sending you calming thoughts."
            "I'm here for you. What's scaring you?",
            "Take a deep breath. What's on your mind?",
            "You're not alone. What are you afraid of?",
            "I understand. Can you tell me more?",
            "It's okay to feel scared. What happened?",
            "I'm here to listen. What's troubling you?",
            "You can talk to me. What's going on?",
            "I believe in you. What are you afraid of?",
            "It's natural to feel this way. Can you share more?",
            "I'm here with you. What's making you feel this way?",
            "You can do this. What's scaring you?",
            "I'm here to support you. What happened?",
            "It's okay to be scared. Can you tell me more?",
            "I'm here to help. What's troubling you?",
            "You're not alone in this. What are you afraid of?",
            "I'm here to listen. What's on your mind?",
            "You can talk to me. What's making you feel this way?",
            "I'm here with you. What’s been going on?",
            "You’re stronger than you think. What are you scared of?",
            "Take your time, I’m here to listen. What’s troubling you?"
        ]

    def generate_angry_responses(self):
        return [
            "I understand why you might be angry.",
            "It’s okay to feel angry.",
            "I hear you, anger is a valid emotion.",
            "Take a deep breath, it’ll pass.",
            "I’m here to listen if you want to talk about it.",
            "You’re allowed to express your anger.",
            "Anger is a natural response.",
            "I’m sorry you’re feeling this way.",
            "Let me know if there’s anything I can do to help.",
            "I’m here to support you."
             "I'm sorry you're feeling this way. What happened?",
            "That sounds really frustrating. Do you want to talk about it?",
            "I can see why you're upset. What led to this?",
            "It's okay to feel angry sometimes. What happened?",
            "I'm here to listen. What's making you feel this way?",
            "That must have been really annoying. Can you tell me more?",
            "It's understandable to feel that way. What happened?",
            "That sounds really frustrating. Do you want to talk about it?",
            "I'm sorry you're going through this. What happened?",
            "It's tough to deal with situations like this. What led to it?",
            "I can understand why you're upset. What happened?",
            "It's okay to feel this way. What's making you feel so angry?",
            "That must have been really tough. Can you tell me more?",
            "I'm here for you. What's been going on?",
            "It sounds like you're having a tough time. What happened?",
            "That sounds really difficult. Do you want to talk about it?",
            "It's understandable to feel this way. What happened?",
            "I can see why you're upset. What led to this?",
            "I'm here to listen. What's making you feel so angry?",
            "That must have been really frustrating. Can you tell me more?"
        ]

    def generate_neutral_responses(self):
        return [
            "Interesting...",
            "Tell me more about that.",
            "I see.",
            "That's good to know.",
            "Got it.",
            "Hmm...",
            "Interesting perspective.",
            "I'm listening.",
            "Go on.",
            "I understand.",
            "Please continue.",
            "Fascinating.",
            "I appreciate your thoughts.",
            "That's intriguing.",
            "Interesting point.",
            "Thanks for sharing.",
            "I'm here for you.",
            "You've given me something to think about.",
            "That makes sense.",
            "Fair enough.",
            "I'm curious to know more."
            "How's everything going today?",
            "Is there something on your mind?",
            "How can I assist you today?",
            "Tell me about your day so far.",
            "Anything interesting happening lately?",
            "How do you feel about today?",
            "What have you been up to?",
            "How’s your day going?",
            "What's something you’re looking forward to?",
            "Do you have any plans for today?",
            "How’s everything on your end?",
            "What’s been the highlight of your day?",
            "What’s on your mind?",
            "Anything exciting coming up?",
            "How’s your week been?",
            "What’s been the best part of your day?",
            "Do you have any plans for the weekend?",
            "How’s everything with you?",
            "Anything new or interesting happening?",
            "What’s been going on with you?"
        ]

# Create the main application window
root = tk.Tk()
app = FaceExpressionChatbotApp(root)
root.mainloop()
