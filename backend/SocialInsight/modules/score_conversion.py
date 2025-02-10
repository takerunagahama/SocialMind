import numpy as np
from SocialInsight.models import QandA, Scores, Session

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

def score_to_deviation(user, session_id):
    # Session のデータ取得
    session = Session.objects.filter(session_id=session_id, user=user).first()
    if not session:
        raise ValueError(f"指定したセッションID {session_id} が見つかりません")

    # QandA データ取得
    qanda_sessions = QandA.objects.filter(session=session)
    if not qanda_sessions.exists():
        raise ValueError(f"指定したセッションID {session_id} に関連する QandA が見つかりません")

    # Scores データ取得
    user_scores = Scores.objects.filter(qanda_session=session, user=user).first()
    if not user_scores:
        raise ValueError(f"指定したセッションID {session_id} に関連するスコアが見つかりません")


    # すべてのスコアを取得
    all_scores = Scores.objects.all()
    if not all_scores.exists():
        raise ValueError('スコアデータが存在しません')

    # 偏差値計算の準備
    score_fields = [field[0] for field in ATTRIBUTE_CHOICES]
    score_data = {field: [getattr(score, field) for score in all_scores] for field in score_fields}

    score_stats = {
        field: {'mean': np.mean(scores), 'std': np.std(scores)}
        for field, scores in score_data.items()
    }

    # 偏差値計算
    deviation_values = {}
    for field in score_fields:
        user_score_value = getattr(user_scores, field)
        mean = score_stats[field]['mean']
        std = score_stats[field]['std']

        deviation_value = 50 if std == 0 else 50 + 10 * (user_score_value - mean) / std
        deviation_values[field] = deviation_value

    return deviation_values, user_scores