# shogi image solver web

将棋アプリのスクリーンショット画像をアップロードすると、次の一手/詰み手順を表示します。

現状、将棋クエストの詰めチャレ・一字駒（裏赤）に対応しています。

## 実行方法

以下の手順で、GCP無料枠e2-microでも動きました。(debian-11-bullseyeイメージ)

```
sudo apt-get update
sudo apt-get install -y git
sudo apt-get install -y docker.io
sudo apt-get install -y docker-compose
git clone https://github.com/akiraqa/shogiimgsolverweb
cd shogiimgsolverweb/
sudo docker-compose up -d
```

コンテナ起動したら、
`http://サーバ名/`でアクセスすると、画像アップロードする画面が表示されます。

詰めチャレ画像をアップロードすると、結果画面を表示します。

## 内容

python+flask+uWSGI+nginxをdockerで動かします。

詰将棋を解く部分は[やねうら王](https://github.com/yaneurao/YaneuraOu)詰将棋エンジンをDockerfileでビルドしています。

詰めチャレ画像を棋譜に解析する処理は
[shogiimgsolver](https://github.com/akiraqa/shogiimgsolver) で行っています。

