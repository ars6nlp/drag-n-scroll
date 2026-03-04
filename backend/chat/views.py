from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import ChatRoom, ChatMessage, ChatParticipant
from .serializers import (
    ChatRoomSerializer, ChatRoomDetailSerializer, ChatMessageSerializer,
    CreateDirectChatSerializer, CreateGroupChatSerializer, SendMessageSerializer,
    SuggestedUserSerializer
)

User = get_user_model()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_chat_rooms(request):
    """Get all chat rooms for current user"""
    user = request.user
    rooms = ChatRoom.objects.filter(participants=user).distinct()
    serializer = ChatRoomSerializer(rooms, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_chat_room_detail(request, room_id):
    """Get detailed info about a specific chat room"""
    user = request.user
    try:
        room = ChatRoom.objects.get(id=room_id, participants=user)
        serializer = ChatRoomDetailSerializer(room)
        return Response(serializer.data)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_direct_chat(request):
    """Create a direct chat with another user"""
    serializer = CreateDirectChatSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    other_user_id = serializer.validated_data['user_id']

    try:
        other_user = User.objects.get(id=other_user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if direct chat already exists
    existing_rooms = ChatRoom.objects.filter(
        room_type='direct'
    ).filter(participants=user).filter(participants=other_user)

    if existing_rooms.exists():
        room = existing_rooms.first()
    else:
        # Create new direct chat
        room = ChatRoom.objects.create(
            room_type='direct',
            created_by=user
        )
        # Add both participants
        ChatParticipant.objects.create(room=room, user=user, role='admin')
        ChatParticipant.objects.create(room=room, user=other_user, role='admin')

    serializer = ChatRoomSerializer(room, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_group_chat(request):
    """Create a group chat"""
    serializer = CreateGroupChatSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    room = ChatRoom.objects.create(
        name=serializer.validated_data['name'],
        room_type='group',
        created_by=user
    )

    # Add creator as admin
    ChatParticipant.objects.create(room=room, user=user, role='admin')

    serializer = ChatRoomDetailSerializer(room)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_messages(request):
    """Get messages for a specific room"""
    room_id = request.GET.get('room')
    if not room_id:
        return Response({'error': 'Room ID required'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    try:
        room = ChatRoom.objects.get(id=room_id, participants=user)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)

    # Use select_related to optimize sender lookup
    messages = room.messages.select_related('sender').all()[:50]  # Limit to last 50 messages
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request):
    """Send a message to a chat room"""
    serializer = SendMessageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user

    try:
        room = ChatRoom.objects.get(id=serializer.validated_data['room'], participants=user)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)

    message = ChatMessage.objects.create(
        room=room,
        sender=user,
        text=serializer.validated_data['text'],
        message_type=serializer.validated_data.get('message_type', 'text')
    )

    # Update room's updated_at timestamp
    room.save()

    serializer = ChatMessageSerializer(message)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_messages_read(request, room_id):
    """Mark messages in a room as read"""
    user = request.user

    try:
        participant = ChatParticipant.objects.get(room__id=room_id, user=user)
        from django.utils import timezone
        participant.last_read_at = timezone.now()
        participant.save()
        return Response({'message': 'Messages marked as read'})
    except ChatParticipant.DoesNotExist:
        return Response({'error': 'Not a participant'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_suggested_users(request):
    """Get suggested users to chat with - always shows demo users first"""
    user = request.user

    # Demo bot users that should always appear first
    demo_usernames = ['Li_Mei', 'Wang_Wei', 'Chen_Yu']
    demo_users_info = {
        'Li_Mei': {'bio': 'Преподаватель китайского языка из Пекина 🇨🇳'},
        'Wang_Wei': {'bio': 'Изучает русский язык, любит общаться 📚'},
        'Chen_Yu': {'bio': 'Студент университета, помогает с практикой 🎓'}
    }

    # Get demo users
    demo_users = User.objects.filter(username__in=demo_usernames).exclude(id=user.id)

    # Get users excluding current user, demo users, and those already in direct chats
    existing_chat_users = User.objects.filter(
        chat_rooms__room_type='direct',
        chat_rooms__created_by=user
    )

    suggested = User.objects.exclude(id=user.id).exclude(username__in=demo_usernames).exclude(id__in=existing_chat_users)[:7]

    data = []

    # Add demo users first
    for u in demo_users:
        bio = demo_users_info.get(u.username, {}).get('bio', '')
        data.append({
            'id': u.id,
            'username': u.username,
            'bio': bio,
            'avatar': None,
            'online': True  # Demo users always appear online
        })

    # Add other users
    for u in suggested:
        # Safely extract profile data
        bio = ''
        avatar_url = None
        try:
            if hasattr(u, 'profile') and u.profile:
                bio = getattr(u.profile, 'bio', '') or ''
                # Only get avatar URL if file exists
                if hasattr(u.profile, 'avatar') and u.profile.avatar and hasattr(u.profile.avatar, 'name') and u.profile.avatar.name:
                    try:
                        avatar_url = u.profile.avatar.url
                    except:
                        avatar_url = None
        except:
            pass

        data.append({
            'id': u.id,
            'username': u.username,
            'bio': bio,
            'avatar': avatar_url,
            'online': False  # Simplified - would need online status tracking
        })

    serializer = SuggestedUserSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def translate_message(request, message_id):
    """Translate a message to the target language (auto-detects source language)"""
    from django.utils import timezone
    import re

    user = request.user
    target_language = request.data.get('target_language', 'en')

    print(f"[TRANSLATE] User: {user.username}, Message ID: {message_id}, Target: {target_language}")

    # Validate target language
    valid_languages = ['ru', 'en', 'zh', 'kz', 'de', 'fr', 'es', 'ja', 'ko']
    if target_language not in valid_languages:
        return Response({'error': f'Invalid target language. Valid options: {", ".join(valid_languages)}'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        # Use select_related to optimize queries
        message = ChatMessage.objects.select_related('room', 'sender').get(id=message_id)
        # Safe print - only show length to avoid encoding issues
        text_len = len(message.text) if message.text else 0
        print(f"[TRANSLATE] Message found: length={text_len}")
    except ChatMessage.DoesNotExist:
        print(f"[TRANSLATE] Message not found: {message_id}")
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if user has access to this message (is participant in the room)
    try:
        if not message.room.participants.filter(id=user.id).exists():
            print(f"[TRANSLATE] Access denied for user {user.username}")
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        print(f"[TRANSLATE] Error checking access: {e}")
        return Response({'error': f'Access check failed: {str(e)}'}, status=status.HTTP_403_FORBIDDEN)

    # Check if message has text
    if not message.text:
        print(f"[TRANSLATE] Message has no text")
        return Response({'error': 'Message has no text to translate'}, status=status.HTTP_400_BAD_REQUEST)

    # Auto-detect source language
    def detect_language(text: str) -> str:
        """Detect the language of the text"""
        if not text:
            return 'en'
        # Check for Chinese characters
        if re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'
        # Check for Russian characters
        if re.search(r'[а-яА-Я]', text):
            return 'ru'
        # Check for Kazakh characters
        if re.search(r'[әіңғүұөқһӘІҢҒҮҰӨҚҺ]', text):
            return 'kz'
        # Check for Japanese characters
        if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return 'ja'
        # Check for Korean characters
        if re.search(r'[\uac00-\ud7af\u1100-\u11ff]', text):
            return 'ko'
        # Check for German special characters
        if re.search(r'[äöüßÄÖÜ]', text):
            return 'de'
        # Check for French special characters
        if re.search(r'[àâäéèêëïîôùûüÿñçÀÂÄÉÈÊËÏÎÔÙÛÜŸÑÇ]', text):
            return 'fr'
        # Check for Spanish special characters
        if re.search(r'[ñáéíóúüÑÁÉÍÓÚÜ¿¡]', text):
            return 'es'
        # Default to English
        return 'en'

    source_lang = detect_language(message.text)
    print(f"[TRANSLATE] Detected language: {source_lang}")

    # Check if translation already exists for this language
    translation_field = f'translation_{target_language}'
    existing_translation = getattr(message, translation_field, None)
    if existing_translation:
        print(f"[TRANSLATE] Translation already exists")
        serializer = ChatMessageSerializer(message)
        return Response(serializer.data)

    try:
        # Language code mapping for deep-translator
        lang_codes = {
            'ru': 'ru',
            'en': 'en',
            'zh': 'zh-CN',
            'kz': 'kk',  # Kazakh might not be well supported
            'de': 'de',
            'fr': 'fr',
            'es': 'es',
            'ja': 'ja',
            'ko': 'ko'
        }

        # Use deep-translator for real translation with timeout and retry
        from deep_translator import GoogleTranslator
        import signal

        source_code = lang_codes.get(source_lang, source_lang)
        target_code = lang_codes.get(target_language, target_language)

        # Translation with timeout and retry
        translated_text = None
        max_retries = 2

        for attempt in range(max_retries):
            try:
                translator = GoogleTranslator(source=source_code, target=target_code)
                translated_text = translator.translate(message.text)
                print(f"[TRANSLATE] Translated: {source_code} -> {target_code}")
                break
            except Exception as trans_error:
                print(f"[TRANSLATE] Attempt {attempt + 1} failed: {trans_error}")
                if attempt == max_retries - 1:
                    # All retries failed - return error instead of fallback
                    print(f"[TRANSLATE] All retries exhausted")
                    return Response({
                        'error': 'Translation service unavailable. Please try again later.',
                        'details': str(trans_error)
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Store the translation using direct attribute assignment
        if target_language == 'ru':
            message.translation_ru = translated_text
        elif target_language == 'en':
            message.translation_en = translated_text
        elif target_language == 'zh':
            message.translation_zh = translated_text
        elif target_language == 'kz':
            message.translation_kz = translated_text
        elif target_language == 'de':
            message.translation_de = translated_text
        elif target_language == 'fr':
            message.translation_fr = translated_text
        elif target_language == 'es':
            message.translation_es = translated_text
        elif target_language == 'ja':
            message.translation_ja = translated_text
        elif target_language == 'ko':
            message.translation_ko = translated_text

        message.translated_at = timezone.now()
        message.save()
        print(f"[TRANSLATE] Translation saved successfully")

        serializer = ChatMessageSerializer(message)
        return Response(serializer.data)

    except Exception as e:
        import traceback
        print(f"[TRANSLATE] ERROR: {str(e)}")
        print(f"[TRANSLATE] TRACEBACK: {traceback.format_exc()}")
        return Response({'error': f'Translation failed: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'GET'])
@permission_classes([permissions.IsAuthenticated])
def typing_indicator(request):
    """Handle typing indicators (simplified - just returns success)"""
    # In production, this would use WebSockets or Redis to broadcast typing status
    # For now, just return success to avoid errors
    return Response({'message': 'Typing indicator received'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_chat(request):
    """AI Chat endpoint for Chinese language learning using Groq API (FREE)"""
    from decouple import config
    from groq import Groq

    user_message = request.data.get('message', '').strip()
    conversation_history = request.data.get('history', [])

    if not user_message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get Groq API key from environment
        groq_api_key = config('GROQ_API_KEY', default=None)

        if not groq_api_key or groq_api_key == 'gsk_YOUR_KEY_HERE':
            # Fallback: provide a simple response without AI
            return Response({
                'message': f"你说的对！\"{user_message}\" 是一个很好的句子。\n\n(To enable AI responses, please add GROQ_API_KEY to your .env file. Get FREE API key from: https://console.groq.com/keys)",
                'usage': None
            }, status=status.HTTP_200_OK)

        # System prompt for Chinese language learning (as specified by user)
        system_prompt = """Ты — ассистент по изучению китайского языка.
Отвечай кратко и понятно, объясняй пиньинь, перевод и тоны.
Если вопрос не связан с китайским языком — сообщи об этом."""

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        for msg in conversation_history[-8:]:  # Keep last 8 messages for context
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role in ['user', 'assistant']:
                messages.append({"role": role, "content": content})

        # Add current message
        messages.append({"role": "user", "content": user_message})

        # Initialize Groq client
        client = Groq(api_key=groq_api_key)

        # Call Groq API with Llama3 model (FREE and fast)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Latest and most capable
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            top_p=0.9,
            stream=False
        )

        # Extract the assistant's response
        ai_message = response.choices[0].message.content

        return Response({
            'message': ai_message,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        # Safe logging without encoding issues
        import sys
        traceback_text = traceback.format_exc()
        try:
            print(f"[AI CHAT] ERROR: {str(e)}", file=sys.stderr)
        except:
            pass

        # Provide more specific error messages
        error_msg = str(e)
        if 'authentication' in error_msg.lower() or 'invalid_api_key' in error_msg.lower() or '401' in error_msg:
            return Response({
                'error': 'Authentication failed. Please check your GROQ_API_KEY. Get FREE API key from: https://console.groq.com/keys'
            }, status=status.HTTP_401_UNAUTHORIZED)
        elif 'rate_limit' in error_msg.lower() or '429' in error_msg:
            return Response({
                'error': 'API rate limit exceeded. Please try again in a moment.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        elif 'timeout' in error_msg.lower():
            return Response({
                'error': 'AI request timeout. Please try again.'
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        else:
            return Response({
                'error': f'AI chat failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
