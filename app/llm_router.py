from openai import OpenAI
from app.config import Settings
from app.schemas import QueryAnswer, LoanApprovalResponse

import instructor

settings = Settings()

class LLMRouter:
    """Router for directing LLM requests to the appropriate model or service."""
    
    def __init__(self):

        self.model = "llama-3.3-70b-versatile"  # Default model for Groq API
        self.openai_client = instructor.from_openai(
            OpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            ),
            mode=instructor.Mode.TOOLS
        )

    def route_request(self, request_type: str, **kwargs):
        """Route the request based on its type."""
        # if request_type == "groq":
        return self.handle_groq_request(**kwargs)
        # elif request_type == "whisper":
        #     return self.handle_whisper_request(**kwargs)
        # elif request_type == "deepface":
        #     return self.handle_deepface_request(**kwargs)
        # else:
        #     raise ValueError(f"Unsupported request type: {request_type}")

    def handle_groq_request(self, **kwargs):
        """Handle requests for Groq API."""
        # Implement logic to interact with Groq API using self.settings.groq_api_key
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": kwargs.get("prompt", "")}],
            response_model=QueryAnswer
        )
        return response

    def handle_whisper_request(self, **kwargs):
        """Handle requests for Whisper model."""
        # Implement logic to interact with Whisper model using self.settings.whisper_model_size
        pass

    def handle_deepface_request(self, **kwargs):
        """Handle requests for DeepFace analysis."""
        # Implement logic to interact with DeepFace using self.settings.deepface_backend
        pass