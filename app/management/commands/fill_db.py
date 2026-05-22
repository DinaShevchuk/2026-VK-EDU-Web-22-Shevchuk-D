import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError
from faker import Faker
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike

fake = Faker()


class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент наполнения')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']

        self.stdout.write(self.style.SUCCESS(f'Starting to fill DB with ratio={ratio}'))

        # 1. Создание пользователей
        self.stdout.write('Creating users...')
        users = []
        for i in range(ratio):
            username = fake.unique.user_name()
            email = fake.email()
            user = User(username=username, email=email)
            user.set_password('password123')
            users.append(user)

        User.objects.bulk_create(users, ignore_conflicts=True)
        users_list = list(User.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(users_list)} users'))

        # Создаем профили
        profiles = []
        for user in users_list:
            if not hasattr(user, 'profile'):
                profile = Profile(user=user)
                profiles.append(profile)
        Profile.objects.bulk_create(profiles, ignore_conflicts=True)

        # 2. Создание тегов
        self.stdout.write('Creating tags...')
        tags = []
        tag_names = ['python', 'django', 'javascript', 'react', 'vue', 'html', 'css', 'java', 'cpp', 'go', 'rust', 'php', 'laravel', 'flask', 'fastapi', 'sql', 'postgresql', 'docker', 'kubernetes', 'git']
        for name in tag_names[:ratio]:
            tags.append(Tag(name=name))

        Tag.objects.bulk_create(tags, ignore_conflicts=True)
        tags_list = list(Tag.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(tags_list)} tags'))

        # 3. Создание вопросов
        self.stdout.write('Creating questions...')
        questions = []
        for i in range(ratio * 10):
            questions.append(Question(
                title=fake.sentence(nb_words=8).rstrip('.'),
                text=fake.paragraph(nb_sentences=5),
                author=random.choice(users_list)
            ))
        Question.objects.bulk_create(questions)
        questions_list = list(Question.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(questions_list)} questions'))

        # 4. Добавляем теги ко всем вопросам
        self.stdout.write('Adding tags to questions...')
        for q in questions_list:
            num_tags = random.randint(1, 3)
            selected_tags = random.sample(tags_list, min(num_tags, len(tags_list)))
            q.tags.add(*selected_tags)

        # 5. Создание ответов
        self.stdout.write('Creating answers...')
        answers = []
        for i in range(ratio * 100):
            answers.append(Answer(
                text=fake.paragraph(nb_sentences=3),
                author=random.choice(users_list),
                question=random.choice(questions_list),
                is_correct=random.choice([True, False]) if random.random() > 0.9 else False
            ))
        Answer.objects.bulk_create(answers)
        answers_list = list(Answer.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(answers_list)} answers'))

        # 6. Создание лайков
        self.stdout.write('Adding likes...')
        likes_questions = []
        likes_answers = []

        for q in questions_list:
            num_likes = random.randint(0, 10)
            for _ in range(num_likes):
                user = random.choice(users_list)
                value = random.choice([1, -1])
                try:
                    likes_questions.append(QuestionLike(user=user, question=q, value=value))
                except IntegrityError:
                    pass

        for a in answers_list[:5000]:  # Ограничим для скорости
            num_likes = random.randint(0, 5)
            for _ in range(num_likes):
                user = random.choice(users_list)
                value = random.choice([1, -1])
                try:
                    likes_answers.append(AnswerLike(user=user, answer=a, value=value))
                except IntegrityError:
                    pass

        QuestionLike.objects.bulk_create(likes_questions, ignore_conflicts=True)
        AnswerLike.objects.bulk_create(likes_answers, ignore_conflicts=True)

        # 7. Обновляем рейтинги
        self.stdout.write('Updating ratings...')
        from django.db.models import Sum
        for q in questions_list:
            rating_sum = q.question_likes.aggregate(Sum('value'))['value__sum'] or 0
            q.rating = rating_sum
        Question.objects.bulk_update(questions_list, ['rating'])

        for a in answers_list:
            rating_sum = a.answer_likes.aggregate(Sum('value'))['value__sum'] or 0
            a.rating = rating_sum
        Answer.objects.bulk_update(answers_list, ['rating'])

        self.stdout.write(self.style.SUCCESS('Database filled successfully!'))
