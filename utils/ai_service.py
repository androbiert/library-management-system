"""
AI Service for generating intelligent book recommendations
Uses Google Gemini AI to create engaging descriptions and recommendations
"""

import os
import google.generativeai as genai

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

def generate_book_recommendation(title, author, category, existing_description=""):
    """
    Generate AI-powered book recommendation including:
    - Detailed description
    - Interesting highlights
    - Reasons why readers should borrow it
    
    Args:
        title: Book title
        author: Book author
        category: Book category/genre
        existing_description: Optional existing description for context
        
    Returns:
        dict: {
            'description': str,
            'highlights': list of str,
            'reasons': list of str,
            'summary': str
        }
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
You are a professional librarian and book expert. Create an engaging recommendation for the following book:

**Title:** {title}
**Author:** {author}
**Genre:** {category}
{f'**Current Description:** {existing_description}' if existing_description else ''}

Provide a JSON response with the following structure:
{{
    "description": "A compelling 2-3 paragraph description that captures the essence of the book and hooks the reader",
    "highlights": ["3-4 interesting points about the book, what makes it special", ...],
    "reasons": ["3-4 specific reasons why someone should read this book", ...],
    "summary": "One captivating sentence that summarizes why this book is worth reading"
}}

Make it engaging, specific, and personalized. Focus on what makes this book unique and valuable to readers.
Return ONLY the JSON, no additional text.
"""
        
        response = model.generate_content(prompt)
        
        # Parse JSON response
        import json
        result_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.startswith('```'):
            result_text = result_text[3:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
        
        result = json.loads(result_text.strip())
        
        return {
            'success': True,
            'description': result.get('description', ''),
            'highlights': result.get('highlights', []),
            'reasons': result.get('reasons', []),
            'summary': result.get('summary', ''),
            'error': None
        }
        
    except Exception as e:
        print(f"Error generating AI recommendation: {str(e)}")
        # Return fallback content
        return {
            'success': False,
            'description': existing_description or f"Discover the world of {title} by {author}, a masterpiece in {category} literature.",
            'highlights': [
                f"A compelling {category} narrative",
                f"Written by acclaimed author {author}",
                "Rich storytelling and engaging characters"
            ],
            'reasons': [
                "Expand your literary horizons",
                "Experience exceptional storytelling",
                "Join thousands of satisfied readers"
            ],
            'summary': f"An essential read for {category} enthusiasts.",
            'error': str(e)
        }


def get_or_generate_recommendation(book_data, force_refresh=False):
    """
    Get AI recommendation from cache or generate new one
    
    Args:
        book_data: dict with book information including _id, title, author, category
        force_refresh: bool, if True regenerate even if cached
        
    Returns:
        dict: AI recommendation data
    """
    from db import get_db
    from bson.objectid import ObjectId
    
    db = get_db()
    book_id = book_data.get('_id')
    
    # Check if we have cached AI data
    if not force_refresh and 'ai_recommendation' in book_data:
        cached = book_data['ai_recommendation']
        if cached and 'description' in cached:
            return {
                'success': True,
                **cached,
                'cached': True
            }
    
    # Generate new recommendation
    result = generate_book_recommendation(
        title=book_data.get('title', ''),
        author=book_data.get('author', ''),
        category=book_data.get('category', ''),
        existing_description=book_data.get('description', '')
    )
    
    # Cache the result in database
    if result['success'] and book_id:
        try:
            db.books.update_one(
                {'_id': ObjectId(book_id)},
                {'$set': {
                    'ai_recommendation': {
                        'description': result['description'],
                        'highlights': result['highlights'],
                        'reasons': result['reasons'],
                        'summary': result['summary']
                    }
                }}
            )
            result['cached'] = False
        except Exception as e:
            print(f"Error caching AI recommendation: {e}")
    
    return result
