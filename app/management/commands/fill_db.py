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

        # 1. Создание пользователей (ratio)
        self.stdout.write('Creating users...')
        users = []
        for i in range(ratio):
            username = fake.unique.user_name()
            email = fake.email()
            password = 'password123'
            user = User(username=username, email=email)
            user.set_password(password)
            users.append(user)

        User.objects.bulk_create(users, ignore_conflicts=True)

        # Получаем всех пользователей из БД
        users_list = list(User.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(users_list)} users'))

        # Создаем профили для пользователей (сигналы могут создать автоматически, но лучше явно)
        profiles = []
        for user in users_list:
            if not hasattr(user, 'profile'):
                profile = Profile(user=user)
                profiles.append(profile)
        Profile.objects.bulk_create(profiles, ignore_conflicts=True)

        # 2. Создание тегов (ratio)
        self.stdout.write('Creating tags...')
        tags = []
        for i in range(ratio):
            tag_name = fake.unique.word()
            tags.append(Tag(name=tag_name))

        Tag.objects.bulk_create(tags, ignore_conflicts=True)
        tags_list = list(Tag.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(tags_list)} tags'))

        # 3. Создание вопросов (ratio * 10)
        self.stdout.write('Creating questions...')
        questions_count = ratio * 10
        questions = []
        question_batch_size = 10000

        for i in range(questions_count):
            title = fake.sentence(nb_words=10)
            text = fake.paragraph(nb_sentences=5)
            author = random.choice(users_list)
            question = Question(title=title, text=text, author=author)
            questions.append(question)

            if len(questions) >= question_batch_size:
                Question.objects.bulk_create(questions)
                questions = []
                self.stdout.write(f'  Created {i+1} questions...')

        if questions:
            Question.objects.bulk_create(questions)

        questions_list = list(Question.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(questions_list)} questions'))

        # Добавляем теги к вопросам (ManyToMany)
        self.stdout.write('Adding tags to questions...')
        for question in questions_list:
            num_tags = random.randint(1, 5)
            question_tags = random.sample(tags_list, min(num_tags, len(tags_list)))
            question.tags.add(*question_tags)

        # 4. Создание ответов (ratio * 100)
        self.stdout.write('Creating answers...')
        answers_count = ratio * 100
        answers = []
        answer_batch_size = 50000

        for i in range(answers_count):
            text = fake.paragraph(nb_sentences=3)
            author = random.choice(users_list)
            question = random.choice(questions_list)
            is_correct = random.choice([True, False]) if random.random() < 0.1 else False
            answer = Answer(text=text, author=author, question=question, is_correct=is_correct)
            answers.append(answer)

            if len(answers) >= answer_batch_size:
                Answer.objects.bulk_create(answers)
                answers = []
                self.stdout.write(f'  Created {i+1} answers...')

        if answers:
            Answer.objects.bulk_create(answers)

        answers_list = list(Answer.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(answers_list)} answers'))

        # 5. Создание лайков вопросов (ratio * 100)
        self.stdout.write('Creating question likes...')
        likes_count = ratio * 100
        question_likes = []
        like_batch_size = 50000

        for i in range(likes_count):
            user = random.choice(users_list)
            question = random.choice(questions_list)
            value = random.choice([1, -1])
            try:
                question_like = QuestionLike(user=user, question=question, value=value)
                question_likes.append(question_like)
            except IntegrityError:
                pass

            if len(question_likes) >= like_batch_size:
                QuestionLike.objects.bulk_create(question_likes, ignore_conflicts=True)
                question_likes = []
                self.stdout.write(f'  Created {i+1} question likes...')

        if question_likes:
            QuestionLike.objects.bulk_create(question_likes, ignore_conflicts=True)

        # Обновляем рейтинг вопросов
        self.stdout.write('Updating questions rating...')
        from django.db.models import Sum
        for question in questions_list:
            rating_sum = question.question_likes.aggregate(Sum('value'))['value__sum'] or 0
            question.rating = rating_sum
        Question.objects.bulk_update(questions_list, ['rating'])

        # 6. Создание лайков ответов (ratio * 100)
        self.stdout.write('Creating answer likes...')
        answer_likes = []

        for i in range(likes_count):
            user = random.choice(users_list)
            answer = random.choice(answers_list)
            value = random.choice([1, -1])
            try:
                answer_like = AnswerLike(user=user, answer=answer, value=value)
                answer_likes.append(answer_like)
            except IntegrityError:
                pass

            if len(answer_likes) >= like_batch_size:
                AnswerLike.objects.bulk_create(answer_likes, ignore_conflicts=True)
                answer_likes = []
                self.stdout.write(f'  Created {i+1} answer likes...')

        if answer_likes:
            AnswerLike.objects.bulk_create(answer_likes, ignore_conflicts=True)

        # Обновляем рейтинг ответов
        self.stdout.write('Updating answers rating...')
        for answer in answers_list:
            rating_sum = answer.answer_likes.aggregate(Sum('value'))['value__sum'] or 0
            answer.rating = rating_sum
        Answer.objects.bulk_update(answers_list, ['rating'])

        self.stdout.write(self.style.SUCCESS('Database filled successfully!'))
