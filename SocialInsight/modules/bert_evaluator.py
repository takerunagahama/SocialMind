import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

def calculate_bert_score(model_answer, user_answer):
    # BERTのtokenizerとモデルを初期化
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')

    # テキストをBERTでembedding
    def get_embeddings(text):
        inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)

        with torch.no_grad():
            outputs = model(**inputs)

        return outputs.last_hidden_state[:, 0, :].numpy()
    

    embedding_model = get_embeddings(model_answer)
    embedding_user = get_embeddings(user_answer)

    similarity = cosine_similarity(embedding_model, embedding_user)[0][0]

    score = (similarity + 1) * 50

    return round(score, 2) 