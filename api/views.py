# Django and DRF imports for building the API view
import os

# HTTP client for making requests to OpenRouter API
import httpx
# Load environment variables from .env file
from dotenv import load_dotenv
# Django streaming response for real-time AI responses
from django.http import StreamingHttpResponse
# Django REST Framework base view class
from rest_framework.views import APIView

# Load environment variables (including OPENROUTER_API_KEY)
load_dotenv()


class ChatCompletionView(APIView):
    """
    API view that acts as a proxy for OpenRouter.ai's chat completion API.
    
    This view receives AI chat requests from clients and forwards them to
    OpenRouter.ai, then streams the responses back to the client.
    
    Authentication and permission classes are empty, making this an open API endpoint.
    """
    
    # No authentication required - this is an open proxy endpoint
    authentication_classes = []
    # No permission restrictions - anyone can access this endpoint
    permission_classes = []

    def post(self, request):
        """
        Handle POST requests for AI chat completions.
        
        This method:
        1. Extracts the OpenRouter API key from environment variables
        2. Builds headers for the upstream request
        3. Forwards the request to OpenRouter.ai
        4. Streams the response back to the client
        """
        
        # Get the OpenRouter API key from environment variables
        api_key = os.getenv("OPENROUTER_API_KEY")

        # Prepare headers for the OpenRouter API request
        headers = {
            "Authorization": f"Bearer {api_key}",  # Add API key for authentication
            "Content-Type": "application/json",    # JSON payload format
        }

        # Copy the request data to avoid modifying the original
        payload = request.data.copy()

        # Create an HTTPX client with no timeout for streaming
        client = httpx.Client(timeout=None)

        # Build the HTTP request to OpenRouter's chat completions endpoint
        response = client.build_request(
            "POST",                                    # HTTP method
            "https://openrouter.ai/api/v1/chat/completions",  # Target URL
            headers=headers,                           # Request headers
            json=payload,                              # Request body
        )

        # Send the request with streaming enabled
        upstream = client.send(
            response,
            stream=True,  # Enable streaming for real-time responses
        )

        def generate():
            """
            Generator function that yields response chunks from OpenRouter.
            
            This function:
            1. Iterates over the streaming response chunks
            2. Yields each chunk to the client
            3. Ensures proper cleanup in the finally block
            """
            try:
                # Stream response chunks as they arrive
                for chunk in upstream.iter_bytes():
                    yield chunk
            finally:
                # Clean up resources when done
                upstream.close()
                client.close()

        # Return a streaming HTTP response with the generated content
        return StreamingHttpResponse(
            generate(),  # The generator function
            status=upstream.status_code,  # Preserve upstream status code
            content_type=upstream.headers.get(
                "Content-Type",
                "text/event-stream",  # Default to Server-Sent Events format
            ),
        )