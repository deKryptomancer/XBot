import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import json
import requests
from datetime import datetime

class OllamaChatAgent:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Chat Agent")
        self.root.geometry("800x600")
        
        # Configure styles
        self.root.configure(bg='#f0f0f0')
        
        # Create main frames
        self.chat_frame = tk.Frame(root, bg='#f0f0f0')
        self.chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('Arial', 10),
            bg='white',
            fg='#333333',
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Input frame
        self.input_frame = tk.Frame(root, bg='#f0f0f0')
        self.input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        # User input
        self.user_input = tk.Text(
            self.input_frame,
            height=4,
            font=('Arial', 10),
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", lambda e: self.send_message() if not e.state & 0x1 else None)
        self.user_input.bind("<Shift-Return>", lambda e: self.user_input.insert(tk.INSERT, '\n'))
        
        # Send button
        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=10,
            relief=tk.FLAT
        )
        self.send_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Model selection
        self.model_var = tk.StringVar()
        self.model_menu = tk.OptionMenu(root, self.model_var, "Loading models...")
        self.model_menu.pack(side=tk.BOTTOM, pady=(0, 10))
        
        # Load available models in background
        self.load_available_models()
        
        # Set focus to input field
        self.user_input.focus_set()
    
    def add_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        user_message = self.user_input.get("1.0", tk.END).strip()
        if not user_message:
            return
            
        # Add user message to chat
        self.add_message("You", user_message)
        self.user_input.delete("1.0", tk.END)
        
        # Disable input while waiting for response
        self.user_input.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        
        # Start a new thread to get the response
        threading.Thread(
            target=self.get_ai_response,
            args=(user_message,),
            daemon=True
        ).start()
    
    def load_available_models(self):
        def fetch_models():
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    models = [model["name"] for model in response.json().get("models", [])]
                    if models:
                        self.root.after(0, self.update_model_menu, models)
                    else:
                        self.root.after(0, self.update_model_menu, ["No models found"])
                else:
                    self.root.after(0, self.update_model_menu, ["Error loading models"])
            except Exception as e:
                self.root.after(0, self.update_model_menu, ["Error: " + str(e)])
        
        threading.Thread(target=fetch_models, daemon=True).start()
    
    def update_model_menu(self, models):
        menu = self.model_menu["menu"]
        menu.delete(0, "end")
        
        if not models:
            self.model_var.set("No models available")
            return
            
        first_model = models[0]
        self.model_var.set(first_model)
        
        for model in models:
            menu.add_command(
                label=model,
                command=lambda m=model: self.model_var.set(m)
            )
    
    def get_ai_response(self, user_message):
        try:
            model = self.model_var.get()
            if not model or model == "No models available" or model.startswith("Error"):
                self.root.after(0, self.add_message, "System", "Please ensure you have at least one model downloaded and Ollama is running.")
                return
            url = "http://localhost:11434/api/chat"
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": user_message}
                ],
                "stream": False
            }
            
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data['message']['content']
                self.root.after(0, self.add_message, "AI", ai_response)
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                self.root.after(0, self.add_message, "System", error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            self.root.after(0, self.add_message, "System", error_msg)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.add_message, "System", error_msg)
            
        finally:
            # Re-enable input
            self.root.after(0, lambda: [
                self.user_input.config(state=tk.NORMAL),
                self.send_button.config(state=tk.NORMAL),
                self.user_input.focus_set()
            ])

def main():
    root = tk.Tk()
    app = OllamaChatAgent(root)
    
    # Add welcome message
    app.add_message("System", "Welcome to Ollama Chat Agent! Type your message and press Enter to send.")
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code != 200:
            app.add_message("System", "Warning: Could not connect to Ollama. Make sure Ollama is running on port 11434.")
    except Exception as e:
        app.add_message("System", f"Warning: Could not connect to Ollama: {str(e)}. Make sure Ollama is running on port 11434.")
    
    root.mainloop()

if __name__ == "__main__":
    main()
