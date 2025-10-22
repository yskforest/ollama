# local_llm

## setup
```bash
docker compose compose up -d

# localhost:8081

docker compose exec ollama bash
ollama pull gemma3:12B

# imageの更新
ollama list | tail -n +2 | awk '{print $1}' | xargs -n1 ollama pull
```

## vscodeでの設定
- continuneプラグインでollama上のモデルを使用してコード解析できる

## memo
- https://ollama.com/library
  - ollmaでpull可能なモデルリスト
