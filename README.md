# SocialMind

## 概要
このプロジェクトは、Djangoフレームワークを使用して構築された社会的知性値を測定する診断アプリです。  
問題とそれに対するモデル回答の生成、ユーザーの回答の点数化はすべてOpenAIのChatGPT4とGoogleのBERTによって算出されます。  
そのため人間によるバイアスが介入することなく、一貫した診断を行うことが可能となっています。  
アプリケーションはDockerコンテナ上で動作し、WSL2環境でも動作するように構築されています。

## 機能
- AIによる質問、モデル回答、ユーザー回答の診断結果の表示
- ユーザーの診断履歴の保存と表示
- 管理者サイトから結果の管理が可能

## 構築環境
- **OS:** Ubuntu 24.04.1 LTS(WSL2使用)
- **コンテナ管理:** Docker 25.0.2
- **python:** 3.11
- **フレームワーク:** Django 5.1.1
- **データベース:** MySQL 8.0(Dockerコンテナ内で動作)
- **その他:** WSL2(Windows Subsystem for Linux 2)でLinux環境を利用

## セットアップ手順
### 前提条件
1. Ubuntu 24.04 環境(WSL2)
2. DockerとDocker Composeがインストールされていること

### インストール手順
1. リポジトリのクローン  
    ```
    git clone git@github.com:Tsuchiya0436/SocialMind.git
    cd SocialMind
    ```
    リポジトリのリンクはこちら: [https://github.com/Tsuchiya0436/SocialMind.git](https://github.com/Tsuchiya0436/SocialMind.git)

2. Dockerコンテナのビルドと起動  
    ```
    docker compose up --build
    ```
3. マイグレーションの実行
    ```
    docker compose exec web python3 manage.py migrate
    ```
4. 管理者アカウントの作成
    ```
    docker compose exec web python3 manage.py createsuperuser
    ```
5. ブラウザで以下のURLにアクセスしてアプリケーションを確認  
    ```
    http://localhost:8000
    ```
## 使用方法
1. アプリケーションを起動した後、ブラウザで`http://localhost:8000`にアクセスします。
2. ユーザーが診断ページで7つの領域(共感力、組織理解、ビジョニング、影響力、啓発力、チームワーク力、忍耐力)を測定する20問分の回答を入力し、結果を表示します。
3. 管理者としてログインすると、診断結果の管理や分析などが可能です。