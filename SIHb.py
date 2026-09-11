import asyncio
import websockets
import speech_recognition as sr
import json

# This works exactly like a light switch!
listening_switch = False

async def keep_listening(websocket, recognizer, source):
    global listening_switch
    while listening_switch == True:
        try:
            audio = await asyncio.to_thread(recognizer.listen, source, timeout=1, phrase_time_limit=5)
            text = await asyncio.to_thread(recognizer.recognize_google, audio)
            
            print(f"🌟 I heard: {text}")
            
            # NEW: Chop the sentence into a list of uppercase words!
            # "Hello good dog" becomes ["HELLO", "GOOD", "DOG"]
            word_list = text.upper().split()
            
            # Send the list to the webpage
            await websocket.send(json.dumps({"words": word_list, "fullText": text}))
            
        except sr.WaitTimeoutError:
            pass 
        except Exception:
            pass

async def walkie_talkie(websocket):
    global listening_switch
    recognizer = sr.Recognizer()
    print("📻 Connected! Waiting for you to press the button...")
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # Listen for messages from the webpage
        async for message in websocket:
            if message == "START":
                listening_switch = True
                print("🎙️ Switch turned ON! Listening continuously...")
                # Tell Python to start the listening loop in the background
                asyncio.create_task(keep_listening(websocket, recognizer, source))
                
            elif message == "STOP":
                listening_switch = False
                print("🛑 Switch turned OFF!")

async def main():
    print("Walkie-Talkie Server is ON! Open your index.html file.")
    async with websockets.serve(walkie_talkie, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())