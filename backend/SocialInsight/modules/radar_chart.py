import matplotlib.pyplot as plt
import japanize_matplotlib
import numpy as np
import io
from SocialInsight.models import QandA, Scores

ATTRIBUTE_CHOICES = [
    ('empathy', '共感力'),
    ('organization', '組織理解'),
    ('influence', '影響力'),
    ('visioning', 'ビジョニング'),
    ('team', 'チームワーク力'),
    ('inspiration', '啓発力'),
    ('perseverance', '忍耐力'),
]

def generate_radar_chart(user, session_id):
    try:
        session_id = int(session_id)  # セッションIDを整数に変換
    except ValueError:
        raise ValueError(f"無効なセッションID: {session_id}")

    # QandAデータを取得
    qanda_sessions = QandA.objects.filter(session__session_id=session_id, user=user)
    if not qanda_sessions.exists():
        raise ValueError(f"指定されたセッションID {session_id} の QandA データが見つかりません")
    qanda_session = qanda_sessions.first()

    # Scoresデータを取得
    try:
        user_scores = Scores.objects.get(qanda_session__session_id=session_id, user=user)
    except Scores.DoesNotExist:
        raise ValueError(f"指定されたセッションID {session_id} の Scores データが見つかりません")

    # 全ユーザーのスコアを取得
    all_scores = Scores.objects.all()

    empathy_scores = [score.empathy for score in all_scores if score.empathy is not None]
    organization_scores = [score.organization for score in all_scores if score.organization is not None]
    visioning_scores = [score.visioning for score in all_scores if score.visioning is not None]
    influence_scores = [score.influence for score in all_scores if score.influence is not None]
    inspiration_scores = [score.inspiration for score in all_scores if score.inspiration is not None]
    team_scores = [score.team for score in all_scores if score.team is not None]
    perseverance_scores = [score.perseverance for score in all_scores if score.perseverance is not None]

    avg_empathy = np.mean(empathy_scores) if empathy_scores else 0
    avg_organization = np.mean(organization_scores) if organization_scores else 0
    avg_visioning = np.mean(visioning_scores) if visioning_scores else 0
    avg_influence = np.mean(influence_scores) if influence_scores else 0
    avg_inspiration = np.mean(inspiration_scores) if inspiration_scores else 0
    avg_team = np.mean(team_scores) if team_scores else 0
    avg_perseverance = np.mean(perseverance_scores) if perseverance_scores else 0

    categories = [label for _, label in ATTRIBUTE_CHOICES]

    user_values = [
        user_scores.empathy, user_scores.organization, user_scores.influence,
        user_scores.visioning, user_scores.team, user_scores.inspiration, user_scores.perseverance
    ]

    avg_values = [
        avg_empathy, avg_organization, avg_influence, avg_visioning, avg_team, avg_inspiration, avg_perseverance
    ]

    # レーダーチャートを描画
    n = len(categories)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    user_values += user_values[:1] 
    avg_values += avg_values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    user_color = '#22FFFF'
    avg_color = '#FF00FF'

    ax.fill(angles, user_values, color=user_color, alpha=0.25)
    ax.plot(angles, user_values, color=user_color, linewidth=2, label='あなたの成績')

    ax.fill(angles, avg_values, color=avg_color, alpha=0.25)
    ax.plot(angles, avg_values, color=avg_color, linewidth=2, label='全ユーザーの平均値')

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=8, color='black')
    ax.set_rgrids([20, 40, 60, 80, 100], labels=["20", "40", "60", "80", "100"], angle=0, color="gray")
    ax.set_position([0.2, 0.2, 0.6, 0.6])

    for label, angle in zip(ax.get_xticklabels(), angles):
        label.set_horizontalalignment('center')
        x_offset = np.cos(angle) * 0.1  # (x方向)
        y_offset = np.sin(angle) * 0.01  # (y方向)
        label.set_position((label.get_position()[0] + x_offset, label.get_position()[1] + y_offset))

    ax.spines['polar'].set_color('lightgray')
    ax.spines['polar'].set_alpha(0.5)  # 透明度を設定 (0.0 = 完全に透明, 1.0 = 不透明)

    plt.title(f'{user_scores.user.username}-第{session_id}回目の成績')

    plt.legend(loc='upper left', bbox_to_anchor=(-0.1, 1.1), fontsize=8)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    # バイナリデータを保存するためのバッファを作成
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    plt.close()
    buffer.seek(0)
    return buffer
