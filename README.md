# local_llm (Local LLM Environment)
Ollama, Open WebUI, Open Notebookを使用したローカルLLM環境の構築セットアップです。

## quic reference
```bash
docker compose up -d

# モデルのDL
docker compose exec ollama ollama pull gemma4:26b

# Ollamaでプル済みの全モデルを更新する場合:
docker compose exec ollama bash -c "ollama list | tail -n +2 | awk '{print $1}' | xargs -n1 ollama pull"

# コンテクスト長の変更
ollama show gpt-oss:20b-131k
ollama run gpt-oss:20b
/set parameter num_ctx 131072
/save gpt-oss:20b-131k

# モデルのカスタマイズ
cd /workscape/model
ollama create gemma4:26b-ci -f gemma4ci.Modelfile

```

## cli agent
```bash
docker compose run --rm cliagent

# continue cli headless
cn --config config.json -p "現在のリポジトリの最新のコミット内容を確認し、内容を.mdファイルに保存してください。"

opencode
```

## IDE設定
### VS Code
- [Continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue) プラグインを使用することで、Ollama上のモデルを使用してコード解析や生成が可能です。

## 参考
- [Ollama Library](https://ollama.com/library)
  - Ollamaで利用可能なモデルの一覧
