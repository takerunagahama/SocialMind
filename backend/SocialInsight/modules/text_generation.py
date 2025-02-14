import boto3
from SocialInsight.models import QandA
import os
import json
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

# APIキーの取得
client = boto3.client("bedrock-runtime", region_name="ap-northeast-1")
modelId = 'anthropic.claude-3-5-sonnet-20240620-v1:0'

attribute_labels = {
    "empathy": "共感力",
    "organization": "組織理解",
    "visioning": "ビジョニング",
    "influence": "影響力",
    "inspiration": "啓発力",
    "team": "チームで目標を達成する力",
    "perseverance": "忍耐力"
}

evaluation_criteria = {
    "empathy": "他者の感情や視点を理解し、その立場に立って共感し、適切な対応を取る能力。",
    "organization": "組織の目標、ビジョン、文化、価値観、役割を理解し、効果的に行動する能力。",
    "visioning": "未来の状態を明確に描き、その実現に向けた具体的な戦略や計画を策定する能力。",
    "influence": "他者に働きかけ、ポジティブな変化を促す能力。",
    "inspiration": "新たな知識や視点を提供し、他者の成長や発展を促す能力。",
    "team": "チームメンバーと協力し、共通の目標を達成する能力。",
    "perseverance": "困難や挫折に直面しても諦めず、粘り強く取り組み続ける能力。"
}

def generate_prompt(attribute, status, has_part_time_job):
    status_description = {
        'high_schooler': '高校での自身の経験（部活、学校行事',
        'undergrad': '大学での自身の経験（ゼミ、インターン',
        'worker': '社会人が実務経験に基づいて答えられるように',
    }

    # アルバイトの有無を考慮
    if status in ['high_schooler', 'undergrad']:
        if has_part_time_job:
            status_description[status] += '、アルバイトなど）に基づいて答えらえるように'
        else:
            status_description[status] += 'など）に基づいて答えられるように'

    return (
        f"{attribute_labels[attribute]}を評価するための質問を1つだけ簡潔に作成してください。\n"
        "質問文には『質問：』などの余計な文字を含めないこと。\n"
        f"{status_description.get(status, '適切に')}答えられる内容にすること。\n"
        "質問内容は必ず日本語で生成する事。\n\n"
        "また、一般的な回答として、社会的知性値（SQ）を中央値50とした場合の"
        "スコアがちょうど50点相当となる論理的な回答を100文字程度で示してください。\n"
        "50点相当の回答とは、基本的な論理性がありつつも、具体例・詳細な説明が不足している回答を指します。\n\n"
        "出力形式は **必ず** 以下のJSON配列形式とし、余計な説明は一切含めないこと。\n"
        '["質問文", "モデル回答"]\n\n'
        f"評価基準は次の通りです: {evaluation_criteria[attribute]}"
    )


def generate_question_and_model_answer(attribute, status, has_part_time_job):
    """
    指定された属性に基づいて質問文とモデル回答を生成する関数。

    """
    print(f"デバッグ確認: status={status}")
    logger.info(f"変数確認 for attribute: {attribute}, status: {status}")

    prompt = generate_prompt(attribute, status, has_part_time_job)
    messages=[ {"role": "user","content": [{"text": prompt}]}]
    inferenceConfig = {
    "temperature": 0,
    "maxTokens": 300,
}
    try:
        response = client.converse(
            modelId=modelId ,
            messages=messages,
            inferenceConfig=inferenceConfig
)
        logger.info(f"Raw response: {response}")

        response_content = response["output"]["message"]["content"][0]["text"]
        
        question, model_answer = json.loads(response_content)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        question, model_answer = "N/A", "N/A"
    except Exception as e:
        logger.error(f"Error in API request or response parsing: {e}")
        question, model_answer = "N/A", "N/A"
        
    logger.info(f"Generated question and answer for attribute: {question}, {model_answer}")
    
    return question, model_answer
