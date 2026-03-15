"""
Views for Session A/B Learning System
5 Steps per session: SRS Review, New Words, Grammar, Dialogue, Word Arrangement
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
import random
import uuid

from core.models import UserCourseProgress, UserProfile
from course.models import Course, CourseDay
from vocab.models import Word, WordProgress, GrammarRule, GrammarExample
from .models import (
    LearningSession, Dialogue, WordArrangementExercise, GrammarTask,
    NewWordLearningProgress, StepProgress, SRSReviewCard
)
from .serializers import (
    LearningSessionSerializer, StartSessionSerializer,
    Step1DataSerializer, Step2DataSerializer, Step3DataSerializer,
    Step4DataSerializer, Step5DataSerializer, AnswerResponseSerializer,
    SessionSummaryResponseSerializer, MainScreenSerializer
)
from .srs import update_srs, get_srs_batch, get_due_count, initialize_word_progress, get_mistakes_batch


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initialize_demo_course(request):
    """
    Initialize complete demo course with 5 lessons, dialogues, and exercises
    """
    import logging
    import random
    logger = logging.getLogger(__name__)

    user = request.user
    hsk_level = request.data.get('hsk_level', 1)

    logger.info(f"[InitDemo] Initializing FULL demo course for user {user.username}, HSK {hsk_level}")

    # Get or create course
    course, created = Course.objects.get_or_create(
        hsk_level=hsk_level,
        is_active=True,
        defaults={
            'title': f'HSK {hsk_level} - Начальный уровень',
            'description': 'Полный курс китайского языка для начинающих',
            'total_days': 5
        }
    )

    if created:
        logger.info(f"[InitDemo] Created new course: {course.title}")
    else:
        # Clear existing days
        course.days.all().delete()
        logger.info(f"[InitDemo] Cleared existing course days")

    # Words for all lessons
    all_words = [
        # Lesson 1: Greetings
        ('你好', 'nǐ hǎo', 'Привет', 'Сәлем', 1),
        ('我', 'wǒ', 'Я', 'Мен', 1),
        ('你', 'nǐ', 'Ты', 'Сен', 1),
        ('谢谢', 'xièxie', 'Спасибо', 'Рахмет', 1),
        ('再见', 'zàijiàn', 'До свидания', 'Сау бол', 1),
        ('好', 'hǎo', 'Хороший', 'Жақсы', 1),
        ('是', 'shì', 'Быть', 'Болу', 1),
        ('不', 'bù', 'Нет', 'Жоқ', 1),

        # Lesson 2: Numbers
        ('一', 'yī', 'Один', 'Бір', 1),
        ('二', 'èr', 'Два', 'Екі', 1),
        ('三', 'sān', 'Три', 'Үш', 1),
        ('四', 'sì', 'Четыре', 'Төрт', 1),
        ('五', 'wǔ', 'Пять', 'Бес', 1),
        ('六', 'liù', 'Шесть', 'Алты', 1),
        ('七', 'qī', 'Семь', 'Жеті', 1),
        ('八', 'bā', 'Восемь', 'Сегіз', 1),

        # Lesson 3: Family
        ('妈妈', 'māma', 'Мама', 'Ана', 1),
        ('爸爸', 'bàba', 'Папа', 'Әке', 1),
        ('哥哥', 'gēge', 'Старший брат', 'Ағасын ұлкен', 1),
        ('姐姐', 'jiějie', 'Старшая сестра', 'Апа', 1),
        ('弟弟', 'dìdi', 'Младший брат', 'Сіңіі ұлкен', 1),
        ('妹妹', 'mèimei', 'Младшая сестра', 'Сіңлі қарындас', 1),

        # Lesson 4: Food
        ('吃', 'chī', 'Есть', 'Жеу', 1),
        ('喝', 'hē', 'Пить', 'Ішу', 1),
        ('米饭', 'mǐfàn', 'Рис', 'Күріш', 1),
        ('水', 'shuǐ', 'Вода', 'Су', 1),
        ('茶', 'chá', 'Чай', 'Шай', 1),
        ('肉', 'ròu', 'Мясо', 'Ет', 1),
        ('鱼', 'yú', 'Рыба', 'Балық', 1),
        ('菜', 'cài', 'Овощи', 'Көкөніс', 1),

        # Lesson 5: Time
        ('今天', 'jīntiān', 'Сегодня', 'Бүгін', 1),
        ('明天', 'míngtiān', 'Завтра', 'Ертең', 1),
        ('昨天', 'zuótiān', 'Вчера', 'Кеше', 1),
        ('现在', 'xiànzài', 'Сейчас', 'Қазір', 1),
        ('早上', 'zǎoshang', 'Утро', 'Таңертең', 1),
        ('晚上', 'wǎnshang', 'Вечер', 'Кеште', 1),
    ]

    # Create words
    created_words = {}
    for hanzi, pinyin, ru, kz, hsk in all_words:
        word, created = Word.objects.get_or_create(
            hanzi=hanzi,
            pinyin=pinyin,
            defaults={
                'translation_ru': ru,
                'translation_kz': kz,
                'hsk_level': hsk
            }
        )
        created_words[hanzi] = word

    logger.info(f"[InitDemo] Created {len(created_words)} words")

    # Create 5 course days with words, dialogues, exercises
    lessons_data = [
        {
            'day': 1,
            'title': 'Урок 1: Приветствие и знакомство',
            'description': 'Научимся здороваться и представляться',
            'words': ['你好', '我', '你', '谢谢', '再见'],
            'dialogue': {
                'zh': '你好！我叫李梅。你叫什么名字？',
                'ru': 'Привет! Меня зовут Ли Мэй. А тебя как зовут?',
                'speaker_a': 'Li_Mei',
                'speaker_b': 'Student'
            }
        },
        {
            'day': 2,
            'title': 'Урок 2: Цифры и счет',
            'description': 'Научимся считать от 1 до 10',
            'words': ['一', '二', '三', '四', '五'],
            'dialogue': {
                'zh': '一，二，三...你有几个哥哥？',
                'ru': 'Раз, два, три... Сколько у тебя братьев?',
                'speaker_a': 'Teacher',
                'speaker_b': 'Student'
            }
        },
        {
            'day': 3,
            'title': 'Урок 3: Семья',
            'description': 'Расскажем о своей семье',
            'words': ['妈妈', '爸爸', '哥哥', '姐姐', '弟弟', '妹妹'],
            'dialogue': {
                'zh': '我家有五口人：爸爸、妈妈、哥哥、妹妹和我。',
                'ru': 'В моей семье 5 человек: папа, мама, старший брат, младшая сестра и я.',
                'speaker_a': 'Chen_Yu',
                'speaker_b': None
            }
        },
        {
            'day': 4,
            'title': 'Урок 4: Еда',
            'description': 'Изучим названия продуктов и глаголы',
            'words': ['吃', '喝', '米饭', '水', '茶', '肉'],
            'dialogue': {
                'zh': '你想吃什么？我想吃米饭和喝茶。',
                'ru': 'Что ты хочешь есть? Я хочу рис и пить чай.',
                'speaker_a': 'Wang_Wei',
                'speaker_b': 'Li_Mei'
            }
        },
        {
            'day': 5,
            'title': 'Урок 5: Время',
            'description': 'Научимся говорить о времени',
            'words': ['今天', '明天', '昨天', '现在', '早上', '晚上'],
            'dialogue': {
                'zh': '你今天做什么？我早上学习，晚上休息。',
                'ru': 'Что ты делаешь сегодня? Утром я учусь, вечером отдыхаю.',
                'speaker_a': 'Teacher',
                'speaker_b': 'Chen_Yu'
            }
        }
    ]

    for lesson in lessons_data:
        # Create course day
        course_day = CourseDay.objects.create(
            course=course,
            day_number=lesson['day'],
            title=lesson['title'],
            description=lesson['description'],
            estimated_minutes=15
        )

        # Add words
        for word_hanzi in lesson['words']:
            if word_hanzi in created_words:
                course_day.new_words.add(created_words[word_hanzi])

        # Create dialogue for Session A
        dialogue_data = lesson['dialogue']
        Dialogue.objects.create(
            course_day=course_day,
            session_type='A',
            lines=[
                {
                    'speaker': dialogue_data['speaker_a'],
                    'hanzi': dialogue_data['zh'],
                    'pinyin': '',
                    'translation_ru': dialogue_data['ru'],
                    'translation_kz': ''
                }
            ],
            question_hanzi=dialogue_data['zh'],
            question_pinyin='',
            question_translation_ru=dialogue_data['ru'],
            question_translation_kz='',
            audio_url='',
            options=[
                {
                    'hanzi': '是',
                    'pinyin': 'Shì',
                    'translation_ru': 'Да',
                    'translation_kz': 'Иә',
                    'is_correct': True
                },
                {
                    'hanzi': '不',
                    'pinyin': 'Bù',
                    'translation_ru': 'Нет',
                    'translation_kz': 'Жоқ',
                    'is_correct': False
                },
                {
                    'hanzi': '也许',
                    'pinyin': 'Yěxǔ',
                    'translation_ru': 'Может быть',
                    'translation_kz': 'Мүмкін',
                    'is_correct': False
                }
            ],
            explanation_ru='Прослушайте диалог и выберите правильный ответ.',
            explanation_kz='Диалогты тыңыңыз.'
        )

        # Create word arrangement exercise
        target_sentence = _get_target_sentence(lesson['day'])
        WordArrangementExercise.objects.create(
            course_day=course_day,
            session_type='A',
            target_hanzi=target_sentence,
            target_pinyin='',
            target_translation_ru=_get_translation_ru(lesson['day']),
            target_translation_kz='',
            audio_url='',
            scrambled_words=_scramble_sentence(target_sentence),
            hint_ru=_get_hint_ru(lesson['day']),
            hint_kz=''
        )

        # Create grammar rule and task for Step 3
        grammar_rule_data = _get_grammar_rule_data(lesson['day'])
        grammar_rule, _ = GrammarRule.objects.get_or_create(
            title=grammar_rule_data['title'],
            pattern=grammar_rule_data['pattern'],
            defaults={
                'explanation_ru': grammar_rule_data['explanation_ru'],
                'explanation_kz': grammar_rule_data['explanation_kz'],
                'hsk_level': hsk_level
            }
        )

        # Create grammar examples if they don't exist
        if not grammar_rule.examples.exists():
            for example in grammar_rule_data['examples']:
                GrammarExample.objects.create(
                    grammar_rule=grammar_rule,
                    sentence_hanzi=example['hanzi'],
                    sentence_pinyin=example['pinyin'],
                    translation_ru=example['translation_ru'],
                    translation_kz=example['translation_kz']
                )

        # Create grammar task for Session A
        grammar_task_data = _get_grammar_task_data(lesson['day'])
        GrammarTask.objects.create(
            course_day=course_day,
            session_type='A',
            grammar_rule=grammar_rule,
            task_prompt_ru=grammar_task_data['task_prompt_ru'],
            task_prompt_kz=grammar_task_data['task_prompt_kz'],
            components=grammar_task_data['components'],
            correct_hanzi=grammar_task_data['correct_hanzi'],
            correct_pinyin=grammar_task_data['correct_pinyin'],
            correct_translation_ru=grammar_task_data['correct_translation_ru'],
            correct_translation_kz=grammar_task_data['correct_translation_kz']
        )

        logger.info(f"[InitDemo] Created Lesson {lesson['day']}: {lesson['title']}")

    return Response({
        'success': True,
        'message': f'Полный демо-курс создан с {len(lessons_data)} уроками',
        'course': {
            'id': course.id,
            'title': course.title,
            'hsk_level': course.hsk_level,
            'total_days': len(lessons_data)
        },
        'words_created': len(created_words),
        'lessons_created': len(lessons_data)
    })


def _get_target_sentence(day):
    sentences = {
        1: '你好 你 好 吗',
        2: '我 有 三 个 苹果',
        3: '这 是 我 的 家',
        4: '我 们 吃 米饭',
        5: '今 天 是 星期 一'
    }
    return sentences.get(day, '你好 世界')


def _scramble_sentence(sentence):
    words = sentence.split()
    random.shuffle(words)
    return ' '.join(words)


def _get_translation_ru(day):
    translations = {
        1: 'Привет, как дела?',
        2: 'У меня три яблока',
        3: 'Это мой дом',
        4: 'Мы едим рис',
        5: 'Сегодня понедельник'
    }
    return translations.get(day, 'Привет мир')


def _get_hint_ru(day):
    hints = {
        1: 'Порядок слов: приветствие + ты + хороший + вопросительная частица',
        2: 'Сначала подлежащее, потом сказуемое, потом дополнение',
        3: 'Указательное местоимение "это" + глагол "быть" + притяжательное местоимение',
        4: '"Мы" + глагол + объект',
        5: '"Сегодня" + глагол "быть" + день недели'
    }
    return hints.get(day, 'Собери предложение')


def _get_grammar_rule_data(day):
    """Get grammar rule data for each lesson"""
    grammar_rules = {
        1: {
            'title': 'Порядок слов в предложении',
            'pattern': 'Подлежащее + Сказуемое',
            'explanation_ru': 'В китайском языке порядок слов строгий: сначала подлежащее (кто?), потом сказуемое (что делает?).',
            'explanation_kz': 'Қытай тілінде сөз тәртібі қатаң: бастауыш (кім?) одан соң етістік (не істейді?).',
            'examples': [
                {
                    'hanzi': '我是学生。',
                    'pinyin': 'Wǒ shì xuésheng.',
                    'translation_ru': 'Я студент.',
                    'translation_kz': 'Мен студент.'
                },
                {
                    'hanzi': '你好吗？',
                    'pinyin': 'Nǐ hǎo ma?',
                    'translation_ru': 'Как дела?',
                    'translation_kz': 'Жақсысың ба?'
                }
            ]
        },
        2: {
            'title': 'Числительные',
            'pattern': 'Число + Счетное слово + Существительное',
            'explanation_ru': 'В китайском языке после числительных всегда идет счетное слово.',
            'explanation_kz': 'Қытай тілінде сандардың соңы әрқашан санау сөзы келеді.',
            'examples': [
                {
                    'hanzi': '我有三个苹果。',
                    'pinyin': 'Wǒ yǒu sān gè píngguǒ.',
                    'translation_ru': 'У меня три яблока.',
                    'translation_kz': 'Менің үш алмам бар.'
                },
                {
                    'hanzi': '这是一个人。',
                    'pinyin': 'Zhè shì yī gè rén.',
                    'translation_ru': 'Это один человек.',
                    'translation_kz': 'Бір адам.'
                }
            ]
        },
        3: {
            'title': 'Указательное местоимение',
            'pattern': '这/那 + 是 + Существительное',
            'explanation_ru': 'Для указания на предметы используем "这" (это) и "那" (то) перед глаголом "быть" (是).',
            'explanation_kz': 'Заттарды көрсету үшін "是" (болу) етістігінің алдында "这" (бұл) және "那" (сол) қолданамыз.',
            'examples': [
                {
                    'hanzi': '这是我的家。',
                    'pinyin': 'Zhè shì wǒ de jiā.',
                    'translation_ru': 'Это мой дом.',
                    'translation_kz': 'Бұл менің үйім.'
                },
                {
                    'hanzi': '那是书。',
                    'pinyin': 'Nà shì shū.',
                    'translation_ru': 'То книга.',
                    'translation_kz': 'Сол - кітап.'
                }
            ]
        },
        4: {
            'title': 'Глаголы действия',
            'pattern': 'Подлежащее + Глагол + Объект',
            'explanation_ru': 'Глаголы "есть" (吃) и "пить" (喝) ставятся перед объектом.',
            'explanation_kz': '"Жеу" (吃) және "ішу" (喝) етістіктері объектінің алдында қойылады.',
            'examples': [
                {
                    'hanzi': '我们吃米饭。',
                    'pinyin': 'Wǒmen chī mǐfàn.',
                    'translation_ru': 'Мы едим рис.',
                    'translation_kz': 'Біз күріш жейміз.'
                },
                {
                    'hanzi': '我喝茶。',
                    'pinyin': 'Wǒ hē chá.',
                    'translation_ru': 'Я пью чай.',
                    'translation_kz': 'Мен шай ішемін.'
                }
            ]
        },
        5: {
            'title': 'Временные слова',
            'pattern': 'Сегодня/Завтра + Глагол',
            'explanation_ru': 'Слова времени ставятся в начале предложения перед подлежащим.',
            'explanation_kz': 'Уақыт сөздері сөйлемнің басында бастауыштың алдында қойылады.',
            'examples': [
                {
                    'hanzi': '今天是星期一。',
                    'pinyin': 'Jīntiān shì xīngqī yī.',
                    'translation_ru': 'Сегодня понедельник.',
                    'translation_kz': 'Бүгін дүйсенбі.'
                },
                {
                    'hanzi': '我早上学习。',
                    'pinyin': 'Wǒ zǎoshang xuéxí.',
                    'translation_ru': 'Утром я учусь.',
                    'translation_kz': 'Таңертең мен оқимын.'
                }
            ]
        }
    }
    return grammar_rules.get(day, grammar_rules[1])


def _get_grammar_task_data(day):
    """Get grammar task data with components for sentence building"""
    grammar_tasks = {
        1: {
            'task_prompt_ru': 'Составьте предложение "Я студент"',
            'task_prompt_kz': '"Мен студент" деген сөйлем құрастырыңыз',
            'components': [
                {'id': 1, 'hanzi': '我', 'pinyin': 'wǒ', 'translation_ru': 'Я', 'translation_kz': 'Мен', 'type': 'subject'},
                {'id': 2, 'hanzi': '是', 'pinyin': 'shì', 'translation_ru': 'быть', 'translation_kz': 'болу', 'type': 'verb'},
                {'id': 3, 'hanzi': '学生', 'pinyin': 'xuésheng', 'translation_ru': 'студент', 'translation_kz': 'студент', 'type': 'noun'}
            ],
            'correct_hanzi': '我是学生',
            'correct_pinyin': 'Wǒ shì xuésheng',
            'correct_translation_ru': 'Я студент',
            'correct_translation_kz': 'Мен студент'
        },
        2: {
            'task_prompt_ru': 'Составьте предложение "У меня три яблока"',
            'task_prompt_kz': '"Менің үш алмам бар" деген сөйлем құрастырыңыз',
            'components': [
                {'id': 1, 'hanzi': '我', 'pinyin': 'wǒ', 'translation_ru': 'Я', 'translation_kz': 'Мен', 'type': 'subject'},
                {'id': 2, 'hanzi': '有', 'pinyin': 'yǒu', 'translation_ru': 'иметь', 'translation_kz': 'bar', 'type': 'verb'},
                {'id': 3, 'hanzi': '三', 'pinyin': 'sān', 'translation_ru': 'три', 'translation_kz': 'үш', 'type': 'number'},
                {'id': 4, 'hanzi': '个', 'pinyin': 'gè', 'translation_ru': 'сч.слово', 'translation_kz': 'санау сөз', 'type': 'counter'},
                {'id': 5, 'hanzi': '苹果', 'pinyin': 'píngguǒ', 'translation_ru': 'яблоко', 'translation_kz': 'алма', 'type': 'noun'}
            ],
            'correct_hanzi': '我有三个苹果',
            'correct_pinyin': 'Wǒ yǒu sān gè píngguǒ',
            'correct_translation_ru': 'У меня три яблока',
            'correct_translation_kz': 'Менің үш алмам бар'
        },
        3: {
            'task_prompt_ru': 'Составьте предложение "Это мой дом"',
            'task_prompt_kz': '"Бұл менің үйім" деген сөйлем құрастырыңыз',
            'components': [
                {'id': 1, 'hanzi': '这', 'pinyin': 'zhè', 'translation_ru': 'это', 'translation_kz': 'бұл', 'type': 'pronoun'},
                {'id': 2, 'hanzi': '是', 'pinyin': 'shì', 'translation_ru': 'быть', 'translation_kz': 'болу', 'type': 'verb'},
                {'id': 3, 'hanzi': '我', 'pinyin': 'wǒ', 'translation_ru': 'мой', 'translation_kz': 'менің', 'type': 'pronoun'},
                {'id': 4, 'hanzi': '的', 'pinyin': 'de', 'translation_ru': 'частица', 'translation_kz': 'септік', 'type': 'particle'},
                {'id': 5, 'hanzi': '家', 'pinyin': 'jiā', 'translation_ru': 'дом', 'translation_kz': 'үй', 'type': 'noun'}
            ],
            'correct_hanzi': '这是我的家',
            'correct_pinyin': 'Zhè shì wǒ de jiā',
            'correct_translation_ru': 'Это мой дом',
            'correct_translation_kz': 'Бұл менің үйім'
        },
        4: {
            'task_prompt_ru': 'Составьте предложение "Мы едим рис"',
            'task_prompt_kz': '"Біз күріш жейміз" деген сөйлем құрастырыңыз',
            'components': [
                {'id': 1, 'hanzi': '我', 'pinyin': 'wǒ', 'translation_ru': 'Я', 'translation_kz': 'Мен', 'type': 'pronoun'},
                {'id': 2, 'hanzi': '们', 'pinyin': 'men', 'translation_ru': 'мы (мн.ч)', 'translation_kz': 'біз (көпше)', 'type': 'suffix'},
                {'id': 3, 'hanzi': '吃', 'pinyin': 'chī', 'translation_ru': 'есть', 'translation_kz': 'жеу', 'type': 'verb'},
                {'id': 4, 'hanzi': '米饭', 'pinyin': 'mǐfàn', 'translation_ru': 'рис', 'translation_kz': 'күріш', 'type': 'noun'}
            ],
            'correct_hanzi': '我们吃米饭',
            'correct_pinyin': 'Wǒmen chī mǐfàn',
            'correct_translation_ru': 'Мы едим рис',
            'correct_translation_kz': 'Біз күріш жейміз'
        },
        5: {
            'task_prompt_ru': 'Составьте предложение "Сегодня понедельник"',
            'task_prompt_kz': '"Бүгін дүйсенбі" деген сөйлем құрастырыңыз',
            'components': [
                {'id': 1, 'hanzi': '今', 'pinyin': 'jīn', 'translation_ru': 'сегодня', 'translation_kz': 'бүгін', 'type': 'time'},
                {'id': 2, 'hanzi': '天', 'pinyin': 'tiān', 'translation_ru': 'день', 'translation_kz': 'күн', 'type': 'noun'},
                {'id': 3, 'hanzi': '是', 'pinyin': 'shì', 'translation_ru': 'быть', 'translation_kz': 'болу', 'type': 'verb'},
                {'id': 4, 'hanzi': '星', 'pinyin': 'xīng', 'translation_ru': 'неделя', 'translation_kz': 'апта', 'type': 'noun'},
                {'id': 5, 'hanzi': '期', 'pinyin': 'qī', 'translation_ru': 'период', 'translation_kz': 'кезең', 'type': 'suffix'},
                {'id': 6, 'hanzi': '一', 'pinyin': 'yī', 'translation_ru': 'один', 'translation_kz': 'бір', 'type': 'number'}
            ],
            'correct_hanzi': '今天是星期一',
            'correct_pinyin': 'Jīntiān shì xīngqī yī',
            'correct_translation_ru': 'Сегодня понедельник',
            'correct_translation_kz': 'Бүгін дүйсенбі'
        }
    }
    return grammar_tasks.get(day, grammar_tasks[1])


# ============================================================================
# MAIN SCREEN
# ============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def main_screen(request):
    """
    Get main screen data with Session A/B cards
    Query params:
    - day (optional): override current day (1-5)
    - hsk (optional): override user's HSK level (1-6)
    """
    import logging
    logger = logging.getLogger(__name__)

    user = request.user
    logger.info(f"[MainScreen] Loading for user: {user.username}")

    # Safely get user profile with defaults
    try:
        user_profile = user.profile
        if not user_profile:
            logger.warning(f"[MainScreen] No profile for {user.username}, creating...")
            user_profile = UserProfile.objects.create(user=user)
    except Exception as e:
        logger.error(f"[MainScreen] Error accessing profile: {e}")
        user_profile = UserProfile.objects.create(user=user)

    # Get or create user progress safely
    try:
        user_progress = user.progress
        if not user_progress:
            logger.warning(f"[MainScreen] No progress for {user.username}, creating...")
            user_progress = UserCourseProgress.objects.create(user=user)
    except Exception as e:
        logger.error(f"[MainScreen] Error accessing progress: {e}")
        user_progress = UserCourseProgress.objects.create(user=user)

    # Check if specific HSK level requested
    hsk_level = request.query_params.get('hsk')
    if hsk_level:
        try:
            hsk_level = int(hsk_level)
            if hsk_level < 1 or hsk_level > 6:
                return Response({'error': 'HSK level must be between 1 and 6'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid HSK level'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        hsk_level = getattr(user_profile, 'current_hsk_level', 1)

    # Check if specific day requested
    day_number = request.query_params.get('day')
    if day_number:
        try:
            day_number = int(day_number)
            if day_number < 1 or day_number > 5:
                return Response({'error': 'Day must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid day number'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        day_number = user_progress.current_day
        # Reset to day 5 if user is beyond available days (max 5 days per course)
        if day_number > 5:
            day_number = 5
            user_progress.current_day = 5
            user_progress.save()

    logger.info(f"[MainScreen] HSK={hsk_level}, Day={day_number}")

    # Get course - create minimal demo course if none exists
    course = Course.objects.filter(
        hsk_level=hsk_level,
        is_active=True
    ).first()

    if not course:
        logger.warning(f"[MainScreen] No active course found for HSK {hsk_level}, creating minimal course...")
        course = Course.objects.create(
            hsk_level=hsk_level,
            title=f'HSK {hsk_level} - Chinese Course',
            description=f'Complete Chinese course for HSK level {hsk_level}',
            total_days=5,
            is_active=True
        )

        # Create 5 course days
        for day_num in range(1, 6):
            CourseDay.objects.create(
                course=course,
                day_number=day_num,
                title=f'Day {day_num}: Chinese Learning',
                description=f'Learn Chinese on day {day_num}',
                estimated_minutes=15
            )

        logger.info(f"[MainScreen] Created minimal course with 5 days")

    logger.info(f"[MainScreen] Found course: {course.title}")

    # Get course day
    course_day = course.days.filter(day_number=day_number).first()
    if not course_day:
        logger.error(f"[MainScreen] Course day {day_number} not found")
        return Response({'error': 'Course day not found'}, status=status.HTTP_404_NOT_FOUND)

    logger.info(f"[MainScreen] Found course day: {course_day.title}")

    # Get or create sessions
    session_a = LearningSession.objects.filter(
        user=user,
        course_day=course_day,
        session_type='A'
    ).first()

    session_b = LearningSession.objects.filter(
        user=user,
        course_day=course_day,
        session_type='B'
    ).first()

    logger.info(f"[MainScreen] Session A: {'Yes' if session_a else 'No'}, Session B: {'Yes' if session_b else 'No'}")

    # Get due for review count
    due_counts = get_due_count(user)

    # Get learning words count
    total_learning = WordProgress.objects.filter(
        user=user,
        srs_level__in=[1, 2, 3, 4]
    ).count()

    response_data = {
        'current_course_day': {
            'id': course_day.id,
            'day_number': course_day.day_number,
            'title': course_day.title,
            'description': course_day.description,
            'estimated_minutes': course_day.estimated_minutes
        },
        'session_a': None,
        'session_b': None,
        'due_for_review': due_counts['due_now'],
        'total_learning_words': total_learning,
        'streak_days': user_progress.streak_days,
        'xp_total': user_progress.total_xp
    }

    if session_a:
        response_data['session_a'] = LearningSessionSerializer(session_a).data

    if session_b:
        response_data['session_b'] = LearningSessionSerializer(session_b).data

    logger.info(f"[MainScreen] Returning data with {len(response_data)} fields")

    return Response(response_data)


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_session(request):
    """
    Start a new learning session (A or B)
    """
    serializer = StartSessionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    course_day_id = serializer.validated_data['course_day_id']
    session_type = serializer.validated_data['session_type']
    user = request.user

    course_day = get_object_or_404(CourseDay, id=course_day_id)

    # Check if session already exists
    existing_session = LearningSession.objects.filter(
        user=user,
        course_day=course_day,
        session_type=session_type
    ).first()

    if existing_session:
        # Resume existing session
        session = existing_session
    else:
        # Create new session
        session = LearningSession.objects.create(
            user=user,
            course_day=course_day,
            session_type=session_type,
            current_step=1
        )

    # Get step 1 data (SRS Review) - call helper directly to avoid decorator issues
    return _get_step_1_data(session)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_session(request):
    """
    Complete a session and show summary
    """
    session_id = request.data.get('session_id')
    user = request.user

    session = get_object_or_404(LearningSession, id=session_id, user=user)

    # Mark as completed
    session.is_completed = True
    session.completed_at = timezone.now()
    session.current_step = 6  # 6 = completed
    session.save()

    # Check if both sessions A and B are completed
    session_a = LearningSession.objects.filter(
        user=user,
        course_day=session.course_day,
        session_type='A',
        is_completed=True
    ).exists()

    session_b = LearningSession.objects.filter(
        user=user,
        course_day=session.course_day,
        session_type='B',
        is_completed=True
    ).exists()

    is_day_completed = session_a and session_b

    # If both sessions completed, move to next day
    if is_day_completed:
        user_progress = user.progress
        if not user_progress:
            user_progress = UserCourseProgress.objects.create(user=user)
        user_progress.current_day += 1
        user_progress.save()

    # Get problematic words details
    problematic_words = []
    if session.problematic_words:
        words = Word.objects.filter(id__in=session.problematic_words)
        problematic_words = [
            {
                'id': w.id,
                'hanzi': w.hanzi,
                'pinyin': w.pinyin,
                'translation_ru': w.translation_ru,
                'translation_kz': w.translation_kz
            }
            for w in words
        ]

    response_data = {
        'session': LearningSessionSerializer(session).data,
        'words_learned': session.words_learned,
        'accuracy_percentage': session.accuracy_percentage,
        'problematic_words_count': len(session.problematic_words),
        'problematic_words': problematic_words,
        'time_spent_minutes': session.total_time_minutes,
        'xp_earned': session.xp_earned,
        'is_day_completed': is_day_completed
    }

    return Response(response_data)


# ============================================================================
# STEP DATA RETRIEVAL
# ============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_step_data(request, session_id):
    """
    Get data for the current step of a session
    """
    user = request.user
    session = get_object_or_404(LearningSession, id=session_id, user=user)

    step = session.current_step

    if step == 1:
        return _get_step_1_data(session)
    elif step == 2:
        return _get_step_2_data(session)
    elif step == 3:
        return _get_step_3_data(session)
    elif step == 4:
        return _get_step_4_data(session)
    elif step == 5:
        return _get_step_5_data(session)
    else:
        return Response({'error': 'Session completed'}, status=status.HTTP_400_BAD_REQUEST)


def _get_step_1_data(session):
    """
    Step 1: SRS Review (2 minutes)
    Get 10 words from previous lessons for review with SRS logic
    """
    # Mark step as started
    if not session.step_1_started_at:
        session.step_1_started_at = timezone.now()
        session.save()

    # Get 10 words due for review
    word_progress_list = get_srs_batch(session.user, batch_size=10)

    # Create SRS cards for this session
    cards = []
    for wp in word_progress_list:
        # Get 3 distractor words for multiple choice
        distractors = Word.objects.filter(
            hsk_level=wp.word.hsk_level
        ).exclude(id=wp.word.id).order_by('?')[:3]

        # Create options (correct word + 3 distractors)
        options = [{'word_id': wp.word.id, 'translation_ru': wp.word.translation_ru,
                    'translation_kz': wp.word.translation_kz}]
        for d in distractors:
            options.append({'word_id': d.id, 'translation_ru': d.translation_ru,
                          'translation_kz': d.translation_kz})

        # Shuffle options
        random.shuffle(options)

        # Create card - use filter().first() to handle potential duplicates
        card = SRSReviewCard.objects.filter(
            session=session,
            word=wp.word
        ).first()

        if not card:
            # Create new card if doesn't exist
            card = SRSReviewCard.objects.create(
                session=session,
                word=wp.word,
                options=options
            )

        cards.append(card)

    # If less than 10 words available, pad with random words
    if len(cards) < 10:
        existing_word_ids = [c.word.id for c in cards]
        additional_words = Word.objects.filter(
            hsk_level=session.user.profile.current_hsk_level
        ).exclude(id__in=existing_word_ids).order_by('?')[:(10 - len(cards))]

        for word in additional_words:
            distractors = Word.objects.filter(
                hsk_level=word.hsk_level
            ).exclude(id=word.id).order_by('?')[:3]

            options = [{'word_id': word.id, 'translation_ru': word.translation_ru,
                        'translation_kz': word.translation_kz}]
            for d in distractors:
                options.append({'word_id': d.id, 'translation_ru': d.translation_ru,
                              'translation_kz': d.translation_kz})
            random.shuffle(options)

            card = SRSReviewCard.objects.create(
                session=session,
                word=word,
                options=options
            )
            cards.append(card)

    # If no cards available, auto-complete step 1 and move to step 2
    if len(cards) == 0:
        # Mark step 1 as completed
        session.step_1_completed_at = timezone.now()
        session.current_step = 2
        session.step_2_started_at = timezone.now()
        session.save()
        # Auto-move to step 2
        return _get_step_2_data(session)

    response_data = {
        'step': 1,
        'step_type': 'SRS_REVIEW',
        'data': {
            'cards': [
                {
                    'id': card.id,
                    'word': {
                        'id': card.word.id,
                        'hanzi': card.word.hanzi,
                        'pinyin': card.word.pinyin,
                        'audio_url': card.word.audio_url
                    },
                    'options': card.options
                }
                for card in cards
            ],
            'total_cards': len(cards),
            'current_card_index': 0
        },
        'session': LearningSessionSerializer(session).data
    }

    return Response(response_data)


def _get_step_2_data(session):
    """
    Step 2: New Words (8 minutes)
    Get 5 new words to learn with mini-tests
    """
    # Mark step as started
    if not session.step_2_started_at:
        session.step_2_started_at = timezone.now()
        session.save()

    # Get new words from course day (not yet learned by user)
    learned_word_ids = WordProgress.objects.filter(
        user=session.user,
        srs_level__gt=0
    ).values_list('word_id', flat=True)

    new_words = session.course_day.new_words.exclude(
        id__in=learned_word_ids
    )[:5]

    # Initialize progress for these words
    words_data = []
    for word in new_words:
        # Create progress record
        NewWordLearningProgress.objects.get_or_create(
            session=session,
            word=word
        )

        words_data.append({
            'id': word.id,
            'hanzi': word.hanzi,
            'pinyin': word.pinyin,
            'translation_ru': word.translation_ru,
            'translation_kz': word.translation_kz,
            'audio_url': word.audio_url
        })

    # If no new words available, auto-complete step 2 and move to step 3
    if not words_data:
        # Mark step 2 as completed
        session.step_2_completed_at = timezone.now()
        session.current_step = 3
        session.step_3_started_at = timezone.now()
        session.save()
        # Auto-move to step 3
        return _get_step_3_data(session)

    response_data = {
        'step': 2,
        'step_type': 'NEW_WORDS',
        'data': {
            'words': words_data,
            'total_words': len(words_data),
            'current_word_index': 0
        },
        'session': LearningSessionSerializer(session).data
    }

    return Response(response_data)


def _get_step_3_data(session):
    """
    Step 3: Grammar (2 minutes)
    Get grammar rule with sentence building task
    """
    # Mark step as started
    if not session.step_3_started_at:
        session.step_3_started_at = timezone.now()
        session.save()

    # Get grammar task for this session
    grammar_task = GrammarTask.objects.filter(
        course_day=session.course_day,
        session_type=session.session_type
    ).first()

    if not grammar_task:
        # Fallback: get any grammar rule from course day
        grammar_rule = session.course_day.grammar_rules.first()
        if grammar_rule:
            # Create a simple grammar task
            grammar_task = GrammarTask.objects.create(
                course_day=session.course_day,
                session_type=session.session_type,
                grammar_rule=grammar_rule,
                task_prompt_ru=f"Постройте предложение используя шаблон: {grammar_rule.pattern}",
                task_prompt_kz=f"Үлгіні қолдана отырып, сөйлем құрыңыз: {grammar_rule.pattern}",
                components=[],
                correct_hanzi="",
                correct_pinyin="",
                correct_translation_ru="",
                correct_translation_kz=""
            )

    task_data = None
    if grammar_task:
        # Get examples from grammar rule
        examples = []
        for ex in grammar_task.grammar_rule.examples.all()[:2]:
            examples.append({
                'hanzi': ex.sentence_hanzi,
                'pinyin': ex.sentence_pinyin,
                'translation_ru': ex.translation_ru,
                'translation_kz': ex.translation_kz
            })

        task_data = {
            'id': grammar_task.id,
            'grammar_rule': {
                'id': grammar_task.grammar_rule.id,
                'title': grammar_task.grammar_rule.title,
                'pattern': grammar_task.grammar_rule.pattern,
                'explanation_ru': grammar_task.grammar_rule.explanation_ru,
                'explanation_kz': grammar_task.grammar_rule.explanation_kz,
                'examples': examples
            },
            'task_prompt_ru': grammar_task.task_prompt_ru,
            'task_prompt_kz': grammar_task.task_prompt_kz,
            'components': grammar_task.components
        }

    # If no grammar task available, auto-complete step 3 and move to step 4
    if not task_data:
        # Mark step 3 as completed
        session.step_3_completed_at = timezone.now()
        session.current_step = 4
        session.step_4_started_at = timezone.now()
        session.save()
        # Auto-move to step 4
        return _get_step_4_data(session)

    response_data = {
        'step': 3,
        'step_type': 'GRAMMAR',
        'data': task_data,
        'session': LearningSessionSerializer(session).data
    }

    return Response(response_data)


def _get_step_4_data(session):
    """
    Step 4: Dialogue (2 minutes)
    Get dialogue for listening comprehension
    """
    # Mark step as started
    if not session.step_4_started_at:
        session.step_4_started_at = timezone.now()
        session.save()

    # Get dialogue for this session
    dialogue = Dialogue.objects.filter(
        course_day=session.course_day,
        session_type=session.session_type
    ).first()

    dialogue_data = None
    if dialogue:
        dialogue_data = {
            'id': dialogue.id,
            'lines': dialogue.lines,
            'question_hanzi': dialogue.question_hanzi,
            'question_pinyin': dialogue.question_pinyin,
            'question_translation_ru': dialogue.question_translation_ru,
            'question_translation_kz': dialogue.question_translation_kz,
            'audio_url': dialogue.audio_url,
            'options': dialogue.options
        }

    # If no dialogue available, auto-complete step 4 and move to step 5
    if not dialogue_data:
        # Mark step 4 as completed
        session.step_4_completed_at = timezone.now()
        session.current_step = 5
        session.step_5_started_at = timezone.now()
        session.save()
        # Auto-move to step 5
        return _get_step_5_data(session)

    response_data = {
        'step': 4,
        'step_type': 'DIALOGUE',
        'data': dialogue_data,
        'session': LearningSessionSerializer(session).data
    }

    return Response(response_data)


def _get_step_5_data(session):
    """
    Step 5: Word Arrangement (1 minute)
    Get word arrangement exercise
    """
    # Mark step as started
    if not session.step_5_started_at:
        session.step_5_started_at = timezone.now()
        session.save()

    # Get arrangement exercise for this session
    exercise = WordArrangementExercise.objects.filter(
        course_day=session.course_day,
        session_type=session.session_type
    ).first()

    exercise_data = None
    if exercise:
        exercise_data = {
            'id': exercise.id,
            'target_hanzi': exercise.target_hanzi,
            'target_pinyin': exercise.target_pinyin,
            'target_translation_ru': exercise.target_translation_ru,
            'target_translation_kz': exercise.target_translation_kz,
            'audio_url': exercise.audio_url,
            'scrambled_words': exercise.scrambled_words,
            'hint_ru': exercise.hint_ru,
            'hint_kz': exercise.hint_kz
        }

    # If no exercise available, auto-complete session
    if not exercise_data:
        # Mark step 5 and session as completed
        session.step_5_completed_at = timezone.now()
        session.is_completed = True
        session.completed_at = timezone.now()
        session.current_step = 6
        session.save()

        # Return session completion data with step info for frontend
        response_data = {
            'step': 6,  # 6 = completed
            'step_type': 'COMPLETED',
            'data': None,
            'session': LearningSessionSerializer(session).data,
            'words_learned': session.words_learned,
            'accuracy_percentage': session.accuracy_percentage,
            'problematic_words_count': len(session.problematic_words),
            'problematic_words': [],
            'time_spent_minutes': session.total_time_minutes,
            'xp_earned': session.xp_earned,
            'is_day_completed': False
        }
        return Response(response_data)

    response_data = {
        'step': 5,
        'step_type': 'WORD_ARRANGEMENT',
        'data': exercise_data,
        'session': LearningSessionSerializer(session).data
    }

    return Response(response_data)


# ============================================================================
# STEP SUBMISSION
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_step_1(request):
    """
    Submit Step 1 (SRS Review) answers
    """
    session_id = request.data.get('session_id')
    card_id = request.data.get('card_id')
    selected_option_id = request.data.get('selected_option_id')
    time_spent_seconds = request.data.get('time_spent_seconds', 0)
    current_card_index = request.data.get('current_card_index', 0)  # Current 0-based index
    total_shown_cards = request.data.get('total_shown_cards', 0)  # Total cards shown to user

    user = request.user
    session = get_object_or_404(LearningSession, id=session_id, user=user)
    card = get_object_or_404(SRSReviewCard, id=card_id, session=session)

    # Check if answer is correct
    correct_word_id = card.word.id
    is_correct = (selected_option_id == correct_word_id)

    # Update card
    card.selected_option_id = selected_option_id
    card.is_correct = is_correct
    card.time_spent_seconds = time_spent_seconds
    card.completed_at = timezone.now()

    # Mark as problematic if incorrect
    if not is_correct:
        card.is_problematic = True
        # Ensure problematic_words is a list
        if session.problematic_words is None:
            session.problematic_words = []
        if card.word.id not in session.problematic_words:
            session.problematic_words.append(card.word.id)

    card.save()
    session.save()

    # Update SRS for this word
    word_progress = WordProgress.objects.filter(
        user=user,
        word=card.word
    ).first()

    if word_progress:
        # Quality rating based on correctness
        quality = 4 if is_correct else 1
        update_srs(word_progress, quality, time_spent_seconds)

    # Update session stats
    session.total_questions += 1
    if is_correct:
        session.correct_answers += 1
        session.xp_earned += 5
    session.save()

    # Check if all cards are completed
    # Use frontend data if provided, otherwise fallback to DB check
    if total_shown_cards > 0:
        # Frontend tells us this was the last card it showed
        is_step_completed = (current_card_index + 1 >= total_shown_cards)
    else:
        # Fallback: check DB
        remaining_cards = session.srs_cards.filter(completed_at__isnull=True).count()
        is_step_completed = (remaining_cards == 0)

    if is_step_completed:
        session.step_1_completed_at = timezone.now()
        session.current_step = 2
        session.save()
        print(f"Step 1 completed! Moving to step 2")

    # Get next card or step completion
    next_data = {}
    if not is_step_completed:
        next_card = session.srs_cards.filter(completed_at__isnull=True).first()
        if next_card:
            next_data = {
                'next_card': {
                    'id': next_card.id,
                    'word': {
                        'id': next_card.word.id,
                        'hanzi': next_card.word.hanzi,
                        'pinyin': next_card.word.pinyin,
                        'audio_url': next_card.word.audio_url
                    },
                    'options': next_card.options
                }
            }

    response_data = {
        'is_correct': is_correct,
        'is_step_completed': is_step_completed,
        'xp_earned': 5 if is_correct else 0,
        'next_step': 2 if is_step_completed else None,
        'session': LearningSessionSerializer(session).data,
        **next_data
    }

    print(f"Response: is_step_completed={response_data['is_step_completed']}, next_step={response_data['next_step']}")

    return Response(response_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_step_2(request):
    """
    Submit Step 2 (New Words) completion
    """
    session_id = request.data.get('session_id')
    words_data = request.data.get('words', [])

    user = request.user
    session = get_object_or_404(LearningSession, id=session_id, user=user)

    # Process each word
    correct_count = 0
    for word_answer in words_data:
        word_id = word_answer.get('word_id')
        is_correct = word_answer.get('is_correct')
        time_spent = word_answer.get('time_spent_seconds', 0)
        pronunciation_attempts = word_answer.get('pronunciation_attempts', 0)
        pronunciation_ok_count = word_answer.get('pronunciation_ok_count', 0)

        # Update progress
        progress = NewWordLearningProgress.objects.filter(
            session=session,
            word_id=word_id
        ).first()

        if progress:
            progress.is_correct = is_correct
            progress.time_spent_seconds = time_spent
            progress.pronunciation_attempts = pronunciation_attempts
            progress.pronunciation_ok_count = pronunciation_ok_count
            progress.completed_at = timezone.now()
            progress.save()

        if is_correct:
            correct_count += 1

        # Initialize SRS for new word
        word = Word.objects.filter(id=word_id).first()
        if word:
            initialize_word_progress(user, word)
            # Mark as learned (level 1)
            word_progress = WordProgress.objects.filter(
                user=user,
                word=word
            ).first()
            if word_progress:
                word_progress.srs_level = 1
                word_progress.next_review_date = timezone.now()
                word_progress.save()

    # Update session
    session.words_learned = len(words_data)
    session.total_questions += len(words_data)
    session.correct_answers += correct_count
    session.xp_earned += correct_count * 10
    session.step_2_completed_at = timezone.now()
    session.current_step = 3
    session.save()

    response_data = {
        'is_correct': True,  # Step is completed
        'is_step_completed': True,
        'xp_earned': correct_count * 10,
        'next_step': 3,
        'session': LearningSessionSerializer(session).data
    }

    return Response(response_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_step_3(request):
    """
    Submit Step 3 (Grammar) answer
    """
    session_id = request.data.get('session_id')
    built_sentence = request.data.get('built_sentence_hanzi', '')
    time_spent_seconds = request.data.get('time_spent_seconds', 0)

    user = request.user
    session = get_object_or_404(LearningSession, id=session_id, user=user)

    # Get grammar task
    grammar_task = GrammarTask.objects.filter(
        course_day=session.course_day,
        session_type=session.session_type
    ).first()

    is_correct = False
    if grammar_task:
        # Simple comparison (can be enhanced for more flexible matching)
        is_correct = (built_sentence.strip() == grammar_task.correct_hanzi.strip())

    # Create step progress record
    StepProgress.objects.create(
        session=session,
        step_type='GRAMMAR',
        data={'built_sentence': built_sentence},
        is_correct=is_correct,
        time_spent_seconds=time_spent_seconds,
        completed_at=timezone.now()
    )

    # Update session
    session.total_questions += 1
    if is_correct:
        session.correct_answers += 1
        session.xp_earned += 10
    session.step_3_completed_at = timezone.now()
    session.current_step = 4
    session.save()

    response_data = {
        'is_correct': is_correct,
        'is_step_completed': True,
        'xp_earned': 10 if is_correct else 0,
        'correct_answer': {'hanzi': grammar_task.correct_hanzi} if grammar_task else None,
        'next_step': 4,
        'session': LearningSessionSerializer(session).data
    }

    return Response(response_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_step_4(request):
    """
    Submit Step 4 (Dialogue) answer
    """
    session_id = request.data.get('session_id')
    selected_option_index = request.data.get('selected_option_index')
    time_spent_seconds = request.data.get('time_spent_seconds', 0)

    user = request.user
    session = get_object_or_404(LearningSession, id=session_id, user=user)

    # Get dialogue
    dialogue = Dialogue.objects.filter(
        course_day=session.course_day,
        session_type=session.session_type
    ).first()

    is_correct = False
    explanation = ''
    if dialogue:
        # Check if selected option is correct
        try:
            if selected_option_index is not None and 0 <= selected_option_index < len(dialogue.options):
                is_correct = dialogue.options[selected_option_index].get('is_correct', False)
        except Exception as e:
            print(f"Error checking dialogue option: {e}")

        # Get explanation based on user language
        try:
            if user.profile.preferred_language == 'kz':
                explanation = dialogue.explanation_kz or ''
            else:
                explanation = dialogue.explanation_ru or ''
        except Exception as e:
            print(f"Error getting explanation: {e}")
            explanation = ''

    # Create step progress record
    StepProgress.objects.create(
        session=session,
        step_type='DIALOGUE',
        data={'selected_option_index': selected_option_index},
        is_correct=is_correct,
        time_spent_seconds=time_spent_seconds,
        completed_at=timezone.now()
    )

    # Update session
    session.total_questions += 1
    if is_correct:
        session.correct_answers += 1
        session.xp_earned += 10
    session.step_4_completed_at = timezone.now()
    session.current_step = 5
    session.save()

    response_data = {
        'is_correct': is_correct,
        'is_step_completed': True,
        'xp_earned': 10 if is_correct else 0,
        'explanation': explanation,
        'next_step': 5,
        'session': LearningSessionSerializer(session).data
    }

    return Response(response_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_step_5(request):
    """
    Submit Step 5 (Word Arrangement) answer
    """
    session_id = request.data.get('session_id')
    arranged_word_ids = request.data.get('arranged_word_ids', [])
    time_spent_seconds = request.data.get('time_spent_seconds', 0)

    user = request.user
    session = get_object_or_404(LearningSession, id=session_id, user=user)

    # Get exercise
    exercise = WordArrangementExercise.objects.filter(
        course_day=session.course_day,
        session_type=session.session_type
    ).first()

    is_correct = False
    if exercise:
        # Check if arrangement is correct
        # This is a simple check - can be enhanced
        correct_order = [w.get('id') for w in exercise.scrambled_words]
        # For now, just check if all words are present (order validation would be more complex)
        is_correct = (sorted(arranged_word_ids) == sorted(correct_order))

    # Create step progress record
    StepProgress.objects.create(
        session=session,
        step_type='WORD_ARRANGEMENT',
        data={'arranged_word_ids': arranged_word_ids},
        is_correct=is_correct,
        time_spent_seconds=time_spent_seconds,
        completed_at=timezone.now()
    )

    # Update session
    session.total_questions += 1
    if is_correct:
        session.correct_answers += 1
        session.xp_earned += 10
    session.step_5_completed_at = timezone.now()
    session.current_step = 6  # Completed
    session.save()

    response_data = {
        'is_correct': is_correct,
        'is_step_completed': True,
        'xp_earned': 10 if is_correct else 0,
        'correct_answer': {'target_hanzi': exercise.target_hanzi} if exercise else None,
        'next_step': None,  # Session complete
        'session': LearningSessionSerializer(session).data
    }

    return Response(response_data)


# ============================================================================
# SRS REVIEW API
# ============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def srs_review_batch(request):
    """
    Get a batch of words due for SRS review
    Query params:
    - batch_size: number of words (default: 10)
    - hsk_level: optional HSK level filter
    """
    user = request.user
    batch_size = int(request.GET.get('batch_size', 10))
    hsk_level = int(request.GET.get('hsk_level')) if 'hsk_level' in request.GET else None

    word_progress_list = get_srs_batch(user, batch_size=batch_size, hsk_level=hsk_level)

    words_data = []
    for wp in word_progress_list:
        words_data.append({
            'id': wp.word.id,
            'hanzi': wp.word.hanzi,
            'pinyin': wp.word.pinyin,
            'translation_ru': wp.word.translation_ru,
            'translation_kz': wp.word.translation_kz,
            'audio_url': wp.word.audio_url,
            'srs_level': wp.srs_level,
            'total_reviews': wp.total_reviews,
            'accuracy': wp.accuracy
        })

    response_data = {
        'batch_id': str(uuid.uuid4()),
        'batch_number': 1,
        'total_batches': 1,
        'words': words_data,
        'total_due': len(words_data)
    }

    return Response(response_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def srs_mistakes_batch(request):
    """
    Get a batch of words user struggled with (mistakes review)
    Query params:
    - batch_size: number of words (default: 20)
    - hsk_level: optional HSK level filter
    """
    user = request.user
    batch_size = int(request.GET.get('batch_size', 20))
    hsk_level = int(request.GET.get('hsk_level')) if 'hsk_level' in request.GET else None

    word_progress_list = get_mistakes_batch(user, batch_size=batch_size, hsk_level=hsk_level)

    words_data = []
    for wp in word_progress_list:
        words_data.append({
            'id': wp.word.id,
            'hanzi': wp.word.hanzi,
            'pinyin': wp.word.pinyin,
            'translation_ru': wp.word.translation_ru,
            'translation_kz': wp.word.translation_kz,
            'audio_url': wp.word.audio_url,
            'srs_level': wp.srs_level,
            'total_reviews': wp.total_reviews,
            'accuracy': wp.accuracy,
            'correct_reviews': wp.correct_reviews
        })

    response_data = {
        'batch_id': str(uuid.uuid4()),
        'batch_number': 1,
        'total_batches': 1,
        'words': words_data,
        'total_due': len(words_data)
    }

    return Response(response_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def srs_submit_review(request):
    """
    Submit SRS review results
    Body:
    {
        "batch_id": "uuid",
        "reviews": [
            {"word_id": 1, "quality": 4, "time_spent_seconds": 5},
            ...
        ]
    }
    """
    from vocab.models import WordProgress

    user = request.user
    data = request.data
    batch_id = data.get('batch_id')
    reviews = data.get('reviews', [])

    if not reviews:
        return Response(
            {'error': 'No reviews provided'},
            status=status.HTTP_400_BAD_REQUEST
        )

    updated_words = []
    reviews_processed = 0

    for review in reviews:
        word_id = review.get('word_id')
        quality = review.get('quality')
        time_spent_seconds = review.get('time_spent_seconds', 0)

        try:
            word_progress = WordProgress.objects.get(user=user, word_id=word_id)
            old_srs_level = word_progress.srs_level
            old_interval = word_progress.interval_days

            update_srs(word_progress, quality, time_spent_seconds)

            updated_words.append({
                'word_id': word_id,
                'old_srs_level': old_srs_level,
                'new_srs_level': word_progress.srs_level,
                'old_interval': old_interval,
                'new_interval': word_progress.interval_days,
                'next_review_date': word_progress.next_review_date.isoformat() if word_progress.next_review_date else None
            })
            reviews_processed += 1
        except WordProgress.DoesNotExist:
            continue

    # Calculate XP earned
    xp_earned = sum(r.get('quality', 0) for r in reviews if r.get('quality', 0) >= 3) * 2

    response_data = {
        'reviews_processed': reviews_processed,
        'words_updated': updated_words,
        'xp_earned': xp_earned
    }

    return Response(response_data)


# ============================================================================
# ADMIN: CREATE DEMO DATA
# ============================================================================

@api_view(['POST'])
@permission_classes([])
def create_demo_data(request):
    """
    Create demo course data (HSK 1 with basic words)
    Protected by secret key to prevent abuse
    """
    from course.models import Course, CourseDay
    from vocab.models import Word

    # Simple secret key protection
    SECRET_KEY = 'drag-n-scroll-demo-2026'
    provided_key = request.data.get('secret_key') or request.GET.get('secret_key')

    if provided_key != SECRET_KEY:
        return Response(
            {'error': 'Unauthorized: Invalid secret key'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        # Check if course already exists
        existing = Course.objects.filter(hsk_level=1, is_active=True).first()
        force = request.data.get('force', False)

        if existing and not force:
            return Response({
                'message': 'Demo course already exists',
                'course': {
                    'id': existing.id,
                    'title': existing.title,
                    'hsk_level': existing.hsk_level
                },
                'hint': 'Set force=true to overwrite existing course'
            })

        # Delete existing course if force=true
        if existing and force:
            # Delete course and all related objects will be cascade deleted
            existing.delete()

        # Create HSK 1 Course
        course = Course.objects.create(
            hsk_level=1,
            title="HSK 1 - Начальный уровень",
            description="Базовый курс китайского языка для начинающих",
            is_active=True
        )

        # Create Day 1
        course_day = CourseDay.objects.create(
            course=course,
            day_number=1,
            title="Урок 1: Приветствие и знакомство",
            description="Научимся здороваться и представляться",
            estimated_minutes=15
        )

        # Create basic words
        words_data = [
            {
                'hanzi': '你好',
                'pinyin': 'nǐ hǎo',
                'translation_ru': 'Привет',
                'translation_kz': 'Сәлем',
                'hsk_level': 1
            },
            {
                'hanzi': '我',
                'pinyin': 'wǒ',
                'translation_ru': 'Я',
                'translation_kz': 'Мен',
                'hsk_level': 1
            },
            {
                'hanzi': '你',
                'pinyin': 'nǐ',
                'translation_ru': 'Ты',
                'translation_kz': 'Сен',
                'hsk_level': 1
            },
            {
                'hanzi': '谢谢',
                'pinyin': 'xièxie',
                'translation_ru': 'Спасибо',
                'translation_kz': 'Рахмет',
                'hsk_level': 1
            },
            {
                'hanzi': '再见',
                'pinyin': 'zàijiàn',
                'translation_ru': 'До свидания',
                'translation_kz': 'Сау бол',
                'hsk_level': 1
            }
        ]

        created_words = []
        for word_data in words_data:
            # Use get_or_create to avoid duplicate key errors
            word, created = Word.objects.get_or_create(
                hanzi=word_data['hanzi'],
                pinyin=word_data['pinyin'],
                defaults=word_data
            )
            course_day.new_words.add(word)
            created_words.append({
                'id': word.id,
                'hanzi': word.hanzi,
                'pinyin': word.pinyin
            })

        # Create grammar rule
        from vocab.models import GrammarRule, GrammarExample
        grammar_rule, _ = GrammarRule.objects.get_or_create(
            hsk_level=1,
            title="Порядок слов в предложении",
            defaults={
                'pattern': "Подлежащее + Сказуемое + Дополнение",
                'explanation_ru': "В китайском языке порядок слов строгий: сначала подлежащее, потом сказуемое, затем дополнение.",
                'explanation_kz': "Қытай тілінде сөз тәртірі қатаң: бастауыш, айтылымы, толықтауыш."
            }
        )

        # Add grammar examples (check if they exist)
        if not grammar_rule.examples.exists():
            GrammarExample.objects.create(
                grammar_rule=grammar_rule,
                sentence_hanzi="我很好。",
                sentence_pinyin="Wǒ hěn hǎo.",
                translation_ru="Я очень хорошо.",
                translation_kz="Мен өте жақсымын."
            )
            GrammarExample.objects.create(
                grammar_rule=grammar_rule,
                sentence_hanzi="你好吗？",
                sentence_pinyin="Nǐ hǎo ma?",
                translation_ru="Как дела?",
                translation_kz="Қалың қалай?"
            )
        course_day.grammar_rules.add(grammar_rule)

        # Create grammar tasks for sessions A and B
        GrammarTask.objects.create(
            course_day=course_day,
            session_type='A',
            grammar_rule=grammar_rule,
            task_prompt_ru="Постройте предложение: Я + спасибо",
            task_prompt_kz="Сөйлем құрастырыңыз: Мен + рахмет",
            components=[
                {'id': 'w1', 'hanzi': '我', 'pinyin': 'wǒ'},
                {'id': 'w2', 'hanzi': '很', 'pinyin': 'hěn'},
                {'id': 'w3', 'hanzi': '好', 'pinyin': 'hǎo'}
            ],
            correct_hanzi="我很好",
            correct_pinyin="Wǒ hěn hǎo",
            correct_translation_ru="Я очень хорошо",
            correct_translation_kz="Мен өте жақсымын"
        )

        GrammarTask.objects.create(
            course_day=course_day,
            session_type='B',
            grammar_rule=grammar_rule,
            task_prompt_ru="Постройте предложение: Ты + хорошо",
            task_prompt_kz="Сөйлем құрастырыңыз: Сен + жақсы",
            components=[
                {'id': 'w1', 'hanzi': '你', 'pinyin': 'nǐ'},
                {'id': 'w2', 'hanzi': '好', 'pinyin': 'hǎo'},
                {'id': 'w3', 'hanzi': '吗', 'pinyin': 'ma'}
            ],
            correct_hanzi="你好吗",
            correct_pinyin="Nǐ hǎo ma",
            correct_translation_ru="Как дела (ты хорошо)?",
            correct_translation_kz="Қалың қалай (сен жақсысың ба)?"
        )

        # Create dialogues for sessions A and B
        Dialogue.objects.create(
            course_day=course_day,
            session_type='A',
            lines=[
                {'speaker': 'A', 'hanzi': '你好！', 'pinyin': 'Nǐ hǎo!', 'translation': 'Привет!'},
                {'speaker': 'B', 'hanzi': '你好！', 'pinyin': 'Nǐ hǎo!', 'translation': 'Привет!'},
                {'speaker': 'A', 'hanzi': '我很好。', 'pinyin': 'Wǒ hěn hǎo.', 'translation': 'Я хорошо.'},
                {'speaker': 'B', 'hanzi': '谢谢！', 'pinyin': 'Xièxie!', 'translation': 'Спасибо!'}
            ],
            question_hanzi=" Speaker B говорит '谢谢'?",
            question_pinyin="Speaker B says '谢谢'?",
            question_translation_ru="Что говорит Speaker B?",
            question_translation_kz="Speaker B не айтады?",
            audio_url="",
            options=[
                {'translation_ru': 'Да', 'translation_kz': 'Иә', 'is_correct': True},
                {'translation_ru': 'Нет', 'translation_kz': 'Жоқ', 'is_correct': False}
            ],
            explanation_ru="В диалоге Speaker B говорит '谢谢' (спасибо).",
            explanation_kz="Диалогта Speaker B '谢谢' (рахмет) дейді."
        )

        Dialogue.objects.create(
            course_day=course_day,
            session_type='B',
            lines=[
                {'speaker': 'A', 'hanzi': '你好吗？', 'pinyin': 'Nǐ hǎo ma?', 'translation': 'Как дела?'},
                {'speaker': 'B', 'hanzi': '我很好。', 'pinyin': 'Wǒ hěn hǎo.', 'translation': 'Я хорошо.'},
                {'speaker': 'A', 'hanzi': '再见！', 'pinyin': 'Zàijiàn!', 'translation': 'До свидания!'},
                {'speaker': 'B', 'hanzi': '再见！', 'pinyin': 'Zàijiàn!', 'translation': 'До свидания!'}
            ],
            question_hanzi="Сколько раз говорят '再见'?",
            question_pinyin="How many times do they say '再见'?",
            question_translation_ru="Сколько раз говорят '再见'?",
            question_translation_kz="'再见' қанша рет айтылады?",
            audio_url="",
            options=[
                {'text': '1 раз', 'text_kz': '1 рет', 'is_correct': False},
                {'text': '2 раза', 'text_kz': '2 рет', 'is_correct': True}
            ],
            explanation_ru="Оба собеседника говорят '再见' один раз = 2 раза.",
            explanation_kz="Екі сөйлесуші де бір реттен '再见' айтады = 2 рет."
        )

        # Create word arrangement exercises for sessions A and B
        WordArrangementExercise.objects.create(
            course_day=course_day,
            session_type='A',
            target_hanzi="你好",
            target_pinyin="Nǐ hǎo",
            target_translation_ru="Привет",
            target_translation_kz="Сәлем",
            audio_url="",
            scrambled_words=[
                {'id': 'w1', 'hanzi': '好', 'pinyin': 'hǎo'},
                {'id': 'w2', 'hanzi': '你', 'pinyin': 'nǐ'}
            ],
            hint_ru="Порядок: ты → привет",
            hint_kz="Тәртіп: сен → сәлем"
        )

        WordArrangementExercise.objects.create(
            course_day=course_day,
            session_type='B',
            target_hanzi="谢谢",
            target_pinyin="Xièxie",
            target_translation_ru="Спасибо",
            target_translation_kz="Рахмет",
            audio_url="",
            scrambled_words=[
                {'id': 'w1', 'hanzi': '谢', 'pinyin': 'xiè'},
                {'id': 'w2', 'hanzi': '谢', 'pinyin': 'xie'}
            ],
            hint_ru="Оба иероглифа одинаковые",
            hint_kz="Екі иероглиф бірдей"
        )

        return Response({
            'message': 'Demo course created successfully',
            'course': {
                'id': course.id,
                'title': course.title,
                'hsk_level': course.hsk_level
            },
            'day': {
                'id': course_day.id,
                'day_number': course_day.day_number,
                'title': course_day.title
            },
            'words_created': len(created_words),
            'words': created_words,
            'grammar_tasks': 2,
            'dialogues': 2,
            'exercises': 2
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': f'Failed to create demo data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([])
def create_full_demo_course(request):
    """Create complete demo course with 5 lessons"""
    from django.core.management import call_command

    try:
        call_command('create_full_demo_course')

        return Response({
            'status': 'success',
            'message': 'Full demo course created successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])
def refresh_demo_course_content(request):
    """Delete and recreate HSK 1 course with full content"""
    from course.models import Course, CourseDay
    from learning.models import LearningSession

    try:
        # Delete old empty course days and their sessions
        CourseDay.objects.filter(course__hsk_level=1).delete()
        LearningSession.objects.filter(course_day__course__hsk_level=1).delete()

        # Create fresh course with content
        from django.core.management import call_command
        call_command('create_full_demo_course')

        return Response({
            'status': 'success',
            'message': 'HSK 1 course refreshed with full content'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
