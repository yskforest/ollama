# local_llm (Local LLM Environment)

Ollama, Open WebUI, Open Notebookを使用したローカルLLM環境の構築セットアップです。

## 前提条件 (Prerequisites)

- [Docker](https://docs.docker.com/get-docker/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (GPUを使用する場合)

## 使い方 (Usage)

1. コンテナの起動:
   ```bash
   docker compose up -d
   ```

2. サービスの利用:
   - **Open WebUI**: [http://localhost:8081](http://localhost:8081)
     - 初回はアカウント作成が必要です（ローカル保存のみ）。
   - **Open Notebook**: [http://localhost:8502](http://localhost:8502)
     - AI搭載のノートブック環境。

3. モデルのダウンロード:
   ```bash
   # 例: gemma2:9bをプルする場合
   docker compose exec ollama ollama pull gemma2:9b
   ```

## メンテナンス

### 画像・モデルの更新
Ollamaでプル済みの全モデルを更新する場合:

```bash
docker compose exec ollama bash -c "ollama list | tail -n +2 | awk '{print $1}' | xargs -n1 ollama pull"
```

### コンテクスト長の変更
```bash
ollama show gpt-oss:20b-131k
ollama run gpt-oss:20b
/set parameter num_ctx 131072
/save gpt-oss:20b-131k
```

## IDE設定

### VS Code
- [Continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue) プラグインを使用することで、Ollama上のモデルを使用してコード解析や生成が可能です。

## 参考
- [Ollama Library](https://ollama.com/library)
  - Ollamaで利用可能なモデルの一覧
