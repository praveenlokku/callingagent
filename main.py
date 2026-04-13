import asyncio
import traceback
import os
import logging
from dotenv import load_dotenv

from videosdk.agents import Agent, AgentSession, RealTimePipeline, JobContext, RoomOptions, WorkerJob, Options
from videosdk.agents import function_tool
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig

logging.basicConfig(level=logging.INFO)
load_dotenv()

# ------------------ AGENT DEFINITION ------------------
class MyVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are Luna, a real-time voice assistant. "
                "Respond instantly to user messages with natural, conversational audio. "
                "Be fast, natural, and concise. "
                "Ask follow-up questions only when necessary."
            )
        )

    async def on_enter(self):
        print("Agent started - audio stream active")
        await self.session.say("Hi, I'm Luna, how can I help you?")  # fast greeting

    async def on_exit(self):
        print("Agent stopped - cleaning up session")
        await self.session.say("Goodbye! Have a great day!")

    # Lightweight intent detection
    def detect_intent(self, text: str):
        text = text.lower()
        if "food" in text or "pizza" in text or "order" in text:
            return "food"
        elif "movie" in text or "book ticket" in text:
            return "movie"
        return "general"

    async def on_user_message(self, message: str):
        # Immediate acknowledgement for perceived speed
        await self.session.say("Yeah...")

        intent = self.detect_intent(message)

        # Respond based on intent
        if intent == "food":
            await self.session.say("What would you like to eat?")
        elif intent == "movie":
            await self.session.say("Which movie would you like to watch?")
        else:
            await self.session.say("Tell me more.")

# ------------------ SESSION START ------------------
async def start_session(context: JobContext):
    # Configure Gemini Realtime model
    model = GeminiRealtime(
        model="gemini-2.5-flash-native-audio-latest",
        api_key=os.getenv("GOOGLE_API_KEY"),
        config=GeminiLiveConfig(
            voice="Aoede",
            response_modalities=["AUDIO"]
            # Note: check VideoSDK for streaming/interrupt options
        )
    )

    pipeline = RealTimePipeline(model=model)
    session = AgentSession(agent=MyVoiceAgent(), pipeline=pipeline)

    try:
        await context.connect()
        await session.start()
        # Keep session alive for testing; in production use proper shutdown triggers
        await asyncio.sleep(3600)
    finally:
        await session.close()
        await context.shutdown()

# ------------------ JOB CONTEXT ------------------
def make_context() -> JobContext:
    room_options = RoomOptions()
    return JobContext(room_options=room_options)

# ------------------ MAIN ------------------
if __name__ == "__main__":
    try:
        options = Options(
            agent_id="MyTelephonyAgent",  # unique ID for routing
            register=True,               # register for telephony
            max_processes=10,
            host="0.0.0.0",
            port=8081
        )
        job = WorkerJob(entrypoint=start_session, jobctx=make_context, options=options)
        job.start()
    except Exception as e:
        traceback.print_exc()