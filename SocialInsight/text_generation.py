from openai import OpenAI
import os
from .models import QandA
import random
import json
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

# APIキーの取得
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

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

def generate_prompt(attribute):
    """
    質問文とモデル回答を生成するためのプロンプトを作成する関数。
    """
    return (
        f"{attribute_labels[attribute]}を評価するための質問を1つだけ簡潔な問題を日本語で作成し、"
        "その質問に対する論理的で一般的な回答を100文字程度で提供してください。"
        "戻り値は配列形式で返してください。順番は['question_text', 'model_answer']とし、"
        "配列の各要素は文字列で囲んでください。"
        "質問文には「質問：」は絶対につけないこと。"
        "大学生と社会人がこたえられるような質問にすること。"
        f"評価基準は次の通りです:{evaluation_criteria[attribute]}"
    )

def generate_question_and_model_answer(attribute):
    """
    指定された属性に基づいて質問文とモデル回答を生成する関数。
    """
    prompt = generate_prompt(attribute)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=300
        )
        response_content = response.choices[0].message.content.strip()
        
        # JSONパースに変更
        question, model_answer = json.loads(response_content)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        question, model_answer = "N/A", "N/A"
    except Exception as e:
        logger.error(f"Error in API request or response parsing: {e}")
        question, model_answer = "N/A", "N/A"
    
    attribute_label = attribute_labels[attribute]
    
    logger.info(f"Generated question and answer for attribute {attribute_label}: {question}, {model_answer}")
    
    return question, model_answer, attribute_label
