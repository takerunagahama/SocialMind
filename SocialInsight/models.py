from django.db import models, transaction
from django.contrib.auth.models import User

ATTRIBUTE_CHOICES = [
    ('empathy', '共感力'),
    ('organization', '組織理解'),
    ('visioning', 'ビジョニング'),
    ('influence', '影響力'),
    ('inspiration', '啓発力'),
    ('team', 'チームワーク力'),
    ('perseverance', '忍耐力'),
    ('total', '合計点'),
]

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)  # 完了状態を示すフィールド
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 新規作成時に session_id をインクリメント
        if not self.pk:
            with transaction.atomic():
                last_session = Session.objects.filter(user=self.user).order_by('-session_id').first()
                self.session_id = (last_session.session_id + 1) if last_session else 1
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'session_id')


class QandA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.TextField()
    model_answer = models.TextField()
    user_answer = models.TextField()
    attribute = models.CharField(max_length=20, choices=ATTRIBUTE_CHOICES)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='qanda_set')

    class Meta:
        verbose_name = "Q and A"
        verbose_name_plural = "Q and A"

class Scores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    qanda_session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='scores')
    empathy = models.IntegerField(default=0)
    organization = models.IntegerField(default=0)
    visioning = models.IntegerField(default=0)
    influence = models.IntegerField(default=0)
    inspiration = models.IntegerField(default=0)
    team = models.IntegerField(default=0)
    perseverance = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_new_score(cls, user, new_scores, qanda_session):
        """
        新しいスコアを作成するクラスメソッド
        """
        return cls.objects.create(
            user=user,
            qanda_session=qanda_session,
            empathy=new_scores.get('empathy', 0),
            organization=new_scores.get('organization', 0),
            visioning=new_scores.get('visioning', 0),
            influence=new_scores.get('influence', 0),
            inspiration=new_scores.get('inspiration', 0),
            team=new_scores.get('team', 0),
            perseverance=new_scores.get('perseverance', 0),
            total=new_scores.get('total', 0),
        )

    class Meta:
        verbose_name = "Scores"
        verbose_name_plural = "Scores"


class Messages(models.Model):
    TYPE_CHOICES = [
        ('strength', '強み'),
        ('improvement', '改善点'),
    ]

    attribute = models.CharField(max_length=20, choices=ATTRIBUTE_CHOICES)
    category = models.CharField(max_length=20, choices=TYPE_CHOICES, default='')
    message = models.TextField(default='')
    training_name = models.TextField()
    training_content = models.TextField()

    class Meta:
        verbose_name = "Messages"
        verbose_name_plural = "Messages"

class Profile(models.Model):
    STATUS_CHOICES = (
        ('student', '学生'),
        ('worker', '社会人'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length = 20,
        choices = STATUS_CHOICES,
        default = 'student'
    )

    def __str__(self):
        return f'{self.user.username}のプロフィール'