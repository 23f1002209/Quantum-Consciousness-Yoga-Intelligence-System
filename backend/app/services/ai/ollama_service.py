import aiohttp
import asyncio
import json
import logging
from typing import Dict, Optional, Any
from core.config import settings

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the Ollama service"""
        try:
            self.session = aiohttp.ClientSession()
            # Test connection
            await self.health_check()
            self.is_initialized = True
            logger.info(f"Ollama service initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama service: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if Ollama service is available"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(f"{self.host}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model['name'] for model in data.get('models', [])]
                    return self.model in models
                return False
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using Ollama"""
        if not self.is_initialized:
            await self.initialize()
            
        try:
            yoga_context = """You are an expert yoga instructor and wellness coach. 
            Provide helpful, accurate, and safe yoga guidance. Focus on:
            - Proper alignment and technique
            - Safety considerations and modifications
            - Breathing techniques (pranayama)
            - Mindfulness and meditation guidance
            - Beginner-friendly explanations
            
            Always prioritize safety and encourage users to listen to their bodies."""
            
            full_prompt = f"{yoga_context}\n\nContext: {context}\n\nUser: {prompt}\n\nYoga Instructor:"
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "keep_alive": "15m",
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500,
                    "num_thread": 4
                }
            }
            
            async with self.session.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('response', 'I apologize, but I cannot provide a response right now.')
                else:
                    logger.error(f"Ollama API error: {response.status}")
                    return "I'm having trouble connecting to the AI service. Please try again."
                    
        except asyncio.TimeoutError:
            logger.error("Ollama request timeout")
            return "The AI service is taking too long to respond. Please try again."
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return "I'm experiencing technical difficulties. Please try again later."

    async def generate_yoga_sequence(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized yoga sequence"""
        level = user_profile.get('level', 'beginner')
        duration = user_profile.get('duration', 30)
        focus = user_profile.get('focus', 'general wellness')
        
        prompt = f"""Create a {duration}-minute yoga sequence for a {level} practitioner focusing on {focus}. 
        Include:
        1. Warm-up poses (5 minutes)
        2. Main sequence with pose names and hold durations
        3. Cool-down and relaxation (5 minutes)
        4. Breathing instructions
        
        Format as JSON with pose names, durations, and instructions."""
        
        response = await self.generate_response(prompt, "sequence_generation")
        
        try:
            # Try to parse as JSON, fallback to text response
            return {"sequence": response, "type": "personalized"}
        except:
            return {"sequence": response, "type": "text"}

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
