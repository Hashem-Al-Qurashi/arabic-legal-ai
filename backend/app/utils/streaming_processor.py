"""
Simple Streaming Text Processor 
Applies Arabic formatting to streaming chunks for perfect real-time experience
"""

from typing import AsyncGenerator, Iterator
from .arabic_formatter import ArabicWordBreaker, format_chatgpt_style


class StreamingTextProcessor:
    """
    Boring solution that applies formatting during streaming
    """
    
    def __init__(self):
        self.word_breaker = ArabicWordBreaker()
        self.accumulated_text = ""
        self.last_formatted_length = 0
    
    def process_chunk(self, chunk: str) -> str:
        """
        Process a single chunk and return ONLY the new formatted content
        """
        # Add chunk to our accumulator
        self.accumulated_text += chunk
        
        # Apply the same formatting as the final result
        full_formatted_content = format_chatgpt_style(self.accumulated_text)
        
        # Return only the NEW content since last time
        new_content = full_formatted_content[self.last_formatted_length:]
        self.last_formatted_length = len(full_formatted_content)
        
        return new_content
    
    def get_final_result(self) -> str:
        """
        Get the final formatted result
        """
        return format_chatgpt_style(self.accumulated_text)
    
    def reset(self):
        """Reset processor for new message"""
        self.word_breaker.reset()
        self.accumulated_text = ""


async def process_streaming_response(
    original_stream: AsyncGenerator[str, None]
) -> AsyncGenerator[str, None]:
    """
    Process streaming response with Arabic formatting
    This is the main function that wraps the RAG engine streaming
    """
    processor = StreamingTextProcessor()
    
    try:
        async for chunk in original_stream:
            if chunk and chunk.strip():
                # Process chunk with Arabic formatting
                formatted_chunk = processor.process_chunk(chunk)
                yield formatted_chunk
            
    except Exception as e:
        print(f"⚠️ Streaming processor error: {e}")
        # Yield the final result if streaming fails
        final_result = processor.get_final_result()
        if final_result:
            yield final_result


# Simple synchronous version for non-async contexts
def process_streaming_chunks(chunks: Iterator[str]) -> Iterator[str]:
    """
    Synchronous version for processing chunks
    """
    processor = StreamingTextProcessor()
    
    for chunk in chunks:
        if chunk and chunk.strip():
            formatted_chunk = processor.process_chunk(chunk)
            yield formatted_chunk