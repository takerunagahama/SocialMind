import boto3
import os
import json
import logging

logger = logging.getLogger(__name__)

client = boto3.client("bedrock-runtime", region_name="ap-northeast-1")
modelId = 'anthropic.claude-3-5-sonnet-20240620-v1:0'

evaluation_criteria = {
    "empathy": "他者の感情や視点を理解し、その立場に立って共感し、適切な対応を取る能力。",
    "organization": "組織の目標、ビジョン、文化、価値観、役割を理解し、効果的に行動する能力。",
    "visioning": "未来の状態を明確に描き、その実現に向けた具体的な戦略や計画を策定する能力。",
    "influence": "他者に働きかけ、ポジティブな変化を促す能力。",
    "inspiration": "新たな知識や視点を提供し、他者の成長や発展を促す能力。",
    "team": "チームメンバーと協力し、共通の目標を達成する能力。",
    "perseverance": "困難や挫折に直面しても諦めず、粘り強く取り組み続ける能力。"
}

def generate_prompt(model_answer, user_answer, attribute):
    criteria_text = evaluation_criteria[attribute]
    return (
        f"次の能力に関する評価を行います：{criteria_text}\n\n"
        f"【モデルの回答】\n{model_answer}\n\n"
        f"【ユーザーの回答】\n{user_answer}\n\n"
        "上記の2つの回答について、文意の一致度、具体例や詳細な説明の有無、文章のまとまり（構成）を評価してください。\n"
        "それぞれの評価は0～100の数値で行ってください。\n"
        "出力は必ず以下の JSON 形式で返してください:\n"
        "```\n"
        "{\n"
        '  "score": <文意一致度>,\n'
        '  "detail_score": <具体例・詳細説明の評価>,\n'
        '  "coherence_score": <文章のまとまりの評価>\n'
        "}\n"
        "```\n"
        "絶対に余計な文章や解説は含めないでください。"
    )

def calculate_gpt_score(model_answer, user_answer, attribute):
    prompt = generate_prompt(model_answer, user_answer, attribute)
    messages = [
    {"role": "assistant","content": [{"text": "あなたはプロの評価者です。"}]},
    {"role": "user","content": [{"text": prompt}]}
]
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
        logger.info(f"GPT Raw Response: {response}")

        response_content = response["output"]["message"]["content"][0]["text"]
        if not response_content:
            logger.error("GPTから空のレスポンスが返されました")
            return {"error": "GPTのレスポンスが空です"}

        logger.info(f"GPT Parsed Response Content: {response_content}")

        # ここでコードブロック記号を除去
        if response_content.startswith("```") and response_content.endswith("```"):
            response_content = response_content[3:-3].strip()

        try:
            gpt_response = json.loads(response_content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {e}, Response Content: {response_content}")
            return {"error": "GPTのレスポンスの解析に失敗しました"}

        if not all(key in gpt_response for key in ["score", "detail_score", "coherence_score"]):
            logger.error(f"期待するキーが不足しています: {gpt_response}")
            return {"error": "GPTのレスポンスに必要なキーが含まれていません"}

        score = gpt_response.get("score", 0)
        detail_score = gpt_response.get("detail_score", 0)
        coherence_score = gpt_response.get("coherence_score", 0)

        avg_score = (score + detail_score + coherence_score) / 3

        return {
            "avg_score": avg_score,
            "score": score,
            "detail_score": detail_score,
            "coherence_score": coherence_score
        }

    except Exception as e:
        logger.error(f"エラー発生: {e}")
        return {"error": "スコア計算中にエラーが発生しました"}

