import numpy as np
from SocialInsight.models import QandA, Scores

ATTRIBUTE_CHOICES = [
    ('empathy', '共感力'),
    ('organization', '組織理解'),
    ('influence', '影響力'),
    ('visioning', 'ビジョニング'),
    ('team', 'チームワーク力'),
    ('inspiration', '啓発力'),
    ('perseverance', '忍耐力'),
    ('total', '合計点'),
]

def score_to_deviation(session_id):
    try:
        qanda_sessions = QandA.objects.filter(session_id=session_id)
        if not qanda_sessions.exists():
            raise ValueError('指定したセッションIDのデータが見つかりません')

        qanda_session = qanda_sessions.first()
    except QandA.DoesNotExist:
        raise ValueError('指定したセッションIDのデータが見つかりません')

    try:
        user_scores = Scores.objects.get(qanda_session=qanda_session)
    except Scores.DoesNotExist:
        raise ValueError('指定したセッションIDのスコアが見つかりません')

    all_scores = Scores.objects.all()

    score_fields = [field[0] for field in ATTRIBUTE_CHOICES]

    score_data = {field: [getattr(score, field) for score in all_scores] for field in score_fields}

    # 各スコアの平均値と標準偏差を計算
    score_stats = {field: {'mean': np.mean(scores), 'std': np.std(scores)} for field, scores in score_data.items()}

    deviation_values = {}

    for field in score_fields:
        user_score_value = getattr(user_scores, field)
        mean = score_stats[field]['mean']
        std = score_stats[field]['std']

        # 標準偏差が0の場合は偏差値を50に設定
        if std == 0:
            deviation_value = 50
        else:
            deviation_value = 50 + 10 * (user_score_value - mean) / std
        
        deviation_values[field] = deviation_value

    return deviation_values, user_scores

