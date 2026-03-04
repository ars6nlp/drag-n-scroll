#!/usr/bin/env python
"""
Create complete demo course data for all 5 lessons
"""

from django.core.management.base import BaseCommand
from course.models import Course, CourseDay
from vocab.models import Word, GrammarRule, GrammarExample
from learning.models import Dialogue, WordArrangementExercise


class Command(BaseCommand):
    help = 'Create complete demo course with 5 lessons'

    def handle(self, *args, **options):
        self.stdout.write('🎓 Creating complete HSK 1 demo course...')

        # Get or create course
        course, created = Course.objects.get_or_create(
            hsk_level=1,
            is_active=True,
            defaults={
                'title': 'HSK 1 - Начальный уровень',
                'description': 'Полный курс китайского языка для начинающих',
                'total_days': 5
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created course'))
        else:
            # Clear existing days
            course.days.all().delete()
            self.stdout.write(self.style.WARNING('✓ Cleared existing course days'))

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
            ('弟弟', 'dìdi', 'Младший брат', 'Сіңлi ұлкен', 1),
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

        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(created_words)} words'))

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
                        'pinyin': '',  # Could add later if needed
                        'translation_ru': dialogue_data['ru'],
                        'translation_kz': ''
                    }
                ],
                question_hanzi=dialogue_data['zh'],
                question_pinyin='',
                question_translation_ru=dialogue_data['ru'],
                question_translation_kz='',
                audio_url='',
                options=[],
                explanation_ru='Прослушайте диалог и выберите правильный ответ.',
                explanation_kz='Диалогты тыңыңынды талға.'
            )

            # Create word arrangement exercise
            target_sentence = self._get_target_sentence(lesson['day'])
            WordArrangementExercise.objects.create(
                course_day=course_day,
                session_type='A',
                target_hanzi=target_sentence,
                target_pinyin='',
                target_translation_ru=self._get_translation_ru(lesson['day']),
                target_translation_kz='',
                audio_url='',
                scrambled_words=self._scramble_sentence(target_sentence),
                hint_ru=self._get_hint_ru(lesson['day']),
                hint_kz=''
            )

            self.stdout.write(self.style.SUCCESS(f'✓ Created Lesson {lesson["day"]}: {lesson["title"]}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Demo course created successfully!'))
        self.stdout.write('\n📚 Course includes:')
        self.stdout.write('  - 5 lessons (Days 1-5)')
        self.stdout.write('  - 30+ words')
        self.stdout.write('  - 5 dialogues')
        self.stdout.write('  - 5 word arrangement exercises')

    def _get_target_sentence(self, day):
        sentences = {
            1: '你好 你 好 吗',
            2: '我 有 三 个 苹果',
            3: '这 是 我 的 家',
            4: '我 们 吃 米饭',
            5: '今 天 是 星期 一'
        }
        return sentences.get(day, '你好 世界')

    def _scramble_sentence(self, sentence):
        words = sentence.split()
        import random
        random.shuffle(words)
        return ' '.join(words)

    def _get_translation_ru(self, day):
        translations = {
            1: 'Привет, как дела?',
            2: 'У меня три яблока',
            3: 'Это мой дом',
            4: 'Мы едим рис',
            5: 'Сегодня понедельник'
        }
        return translations.get(day, 'Привет мир')

    def _get_hint_ru(self, day):
        hints = {
            1: 'Порядок слов: приветствие + ты + хороший + вопросительная частица',
            2: 'Сначала подлежащее, потом сказуемое, потом дополнение',
            3: 'Указательное местоимение "это" + глагол "быть" + притяжательное местоимение',
            4: '"Мы" + глагол + объект',
            5: '"Сегодня" + глагол "быть" + день недели'
        }
        return hints.get(day, 'Собери предложение')
