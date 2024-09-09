from django.db import models
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Session'

class QandA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.TextField()
    model_answer = models.TextField()
    user_answer = models.TextField()
    attribute = models.CharField(max_length=20, choices=ATTRIBUTE_CHOICES)
    session_id = models.IntegerField()

    def __str__(self):
        return f'{self.user.username}-第{self.session_id}回目({self.attribute})'

    class Meta:
        verbose_name = "Q and A"
        verbose_name_plural = "Q and A"

class Scores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    qanda_session = models.ForeignKey(QandA, on_delete=models.CASCADE, related_name='scores', default = 1)
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
        return cls.objects.create(
            user = user,
            qand_session = qanda_session,
            empathy = new_scores.get('empathy', 0),
            organization = new_scores.get('organization', 0),
            visioning = new_scores.get('visioning', 0),
            influence = new_scores.get('influence', 0),
            inspiration = new_scores.get('inspiration', 0),
            team = new_scores.get('team', 0),
            perseverance = new_scores.get('perseverance', 0),
            total = new_scores.get('total', 0),
        )

    def __str__(self):
        return f'{self.user.username}: {self.total}({self.qanda_session})'

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

    def __str__(self):
        return f'{self.get_attribute_display()}-{self.get_category_display()}'

    class Meta:
        verbose_name = "Messages"
        verbose_name_plural = "Messages"