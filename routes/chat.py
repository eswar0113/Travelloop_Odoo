from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from google import genai
from google.genai import types

chat_bp = Blueprint('chat', __name__)

SYSTEM_PROMPT = """You are Traveloop's AI travel assistant — friendly, knowledgeable, and concise.

You help users with:
- Travel destination suggestions, hidden gems, and must-see attractions
- Building multi-city trip itineraries and planning travel routes
- Daily budget estimates and cost breakdowns by city (budget / mid-range / luxury)
- Visa requirements, entry rules, and travel documents
- Packing lists tailored to destination and trip duration
- Local culture, food recommendations, and travel tips
- Best time to visit, weather, and seasonal advice
- Flight routes, layover tips, and transport between cities

About Traveloop app features you can mention:
- Trip Builder: add city stops, set arrival/departure dates, add activities
- Budget Tracker: track expenses by category, set budget targets
- Community Feed: share trip stories and tips with other travellers
- Packing Checklist: categorised lists (clothing, documents, electronics, toiletries)
- Trip Notes: save ideas, research, and reminders per trip

Style rules:
- Keep responses concise — 3-5 sentences or a short bullet list (max 5 bullets)
- Be enthusiastic and encouraging about travel
- Use 1-2 relevant emojis per response (not excessive)
- Always end with one brief follow-up suggestion or question
- If asked non-travel questions, gently redirect to travel topics"""


@chat_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    api_key = current_app.config.get('GEMINI_API_KEY', '').strip()

    if not api_key or api_key == 'your_gemini_api_key_here':
        return jsonify({'reply': (
            'AI assistant needs a Gemini API key. '
            'Get a free one at aistudio.google.com/app/apikey and add it to .env as GEMINI_API_KEY'
        )})

    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    history = data.get('history') or []

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        client = genai.Client(api_key=api_key)

        contents = []
        for entry in history[-12:]:
            role = entry.get('role')
            text = (entry.get('text') or '').strip()
            if role == 'user' and text:
                contents.append(types.Content(role='user', parts=[types.Part(text=text)]))
            elif role == 'model' and text:
                contents.append(types.Content(role='model', parts=[types.Part(text=text)]))

        contents.append(types.Content(role='user', parts=[types.Part(text=message)]))

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=512,
            ),
        )
        return jsonify({'reply': response.text})

    except Exception as e:
        err = str(e)
        if 'SERVICE_DISABLED' in err or 'not been used' in err:
            return jsonify({'reply': (
                '⚠️ Gemini API is disabled for this key. '
                'Get a new key at aistudio.google.com/app/apikey and update GEMINI_API_KEY in .env'
            )})
        if 'API_KEY_INVALID' in err or 'invalid' in err.lower():
            return jsonify({'reply': 'Invalid API key. Check your GEMINI_API_KEY in .env'})
        if 'quota' in err.lower() or 'RESOURCE_EXHAUSTED' in err:
            return jsonify({'reply': (
                '⚠️ Gemini quota exceeded. This usually means the free tier limit is 0 for your region. '
                'Try creating a new API key at aistudio.google.com/app/apikey'
            )})
        return jsonify({'reply': f'Error: {err[:120]}'})
