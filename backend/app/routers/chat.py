import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from anthropic import Anthropic

from ..config import Settings, get_settings
from ..models.schemas import ChatRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", status_code=status.HTTP_200_OK)
async def chat(
    payload: ChatRequest,
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """Chat with Claude using streaming responses."""
    
    if not settings.claude_api_key:
        logger.error("Claude API key is not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Claude API key is not configured. Please set CLAUDE_API environment variable.",
        )

    try:
        # Initialize Anthropic client
        client = Anthropic(api_key=settings.claude_api_key)

        # Convert messages to Anthropic format
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in payload.messages
        ]

        logger.info(f"Starting chat stream with {len(anthropic_messages)} messages")

        def generate_stream():
            """Generator function for streaming responses."""
            try:
                # Stream the response - use context manager
                with client.messages.stream(
                    model="claude-3-5-haiku-latest",
                    max_tokens=700,
                    messages=anthropic_messages,
                ) as stream:
                    for event in stream:
                        if event.type == "content_block_delta":
                            if event.delta.type == "text_delta":
                                # Send SSE formatted data
                                data = json.dumps({
                                    "type": "content_block_delta",
                                    "delta": {
                                        "type": "text_delta",
                                        "text": event.delta.text,
                                    },
                                })
                                yield f"data: {data}\n\n"
                        elif event.type == "message_stop":
                            yield "data: [DONE]\n\n"
                            break
            except Exception as e:
                logger.error(f"Error in stream generation: {e}", exc_info=True)
                error_data = json.dumps({
                    "type": "error",
                    "error": str(e),
                })
                yield f"data: {error_data}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        logger.error(f"Error setting up chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting up chat: {str(e)}",
        )

