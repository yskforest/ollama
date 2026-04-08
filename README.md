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

### opencode/crush
- 下記３つある
  - https://github.com/anomalyco/opencode
  - https://github.com/charmbracelet/crush
  - https://github.com/opencode-ai/opencode
- anomalyco/opencodeが無難と思われる

## continueの設定
```yml
name: Local Config
version: 1.0.0
schema: v1
models:
  - name: gpt-oss:20b
    provider: ollama
    model: gpt-oss:20b
    roles:
      - chat
      - edit
      - apply
  - name: qwen2.5-coder:1.5b
    provider: ollama
    model: qwen2.5-coder:1.5b
    roles:
      - autocomplete
  - name: bge-m3:latest
    provider: ollama
    model: bge-m3:latest
    roles:
      - embed
```

```bash
cn --config config.json -p "現在のリポジトリの最新のコミット内容を確認し、内容を.mdファイルに保存してください。"
```

```Dockerfile
# ベースモデルとしてQ4_K_M量子化されたQwen2.5-Coder-32Bを指定
FROM qwen2.5-coder:32b-instruct-q4_K_M

# RTX 3090の24GB VRAMに確実に収めつつ、実用的な長文脈を維持するため
# コンテキスト長を16,384トークンに厳密にハードコードする。
# これにより、OpenCodeからの呼び出し時もこのコンテキストが適用される。
PARAMETER num_ctx 16384

# コーディングタスクにおいては、幻覚（Hallucination）を抑え、
# 決定論的で予測可能な論理展開、および正確なJSONフォーマットの出力を促すため、
# temperatureを低く設定する。推奨値は0.0〜0.1の範囲である。
PARAMETER temperature 0.1

# コード生成において重要なシンボル（括弧やセミコロン）や
# 共通の構文パターンが不自然に抑制されるのを防ぐため、
# 繰り返しペナルティ(repeat_penalty)はデフォルトの1.1付近か、わずかに下げる。
PARAMETER repeat_penalty 1.05

# エージェントが大規模なコードブロックや複雑なツール呼び出しのJSONを生成する際に、
# 出力が途中で切り捨てられる（Truncation）のを防ぐため、出力トークンの上限を増枠する。
# PARAMETER num_predict 8192

# 共通ルールの設定（SYSTEMプロンプト）
# すべてのCIリクエストで適用される「エージェントの基本ルール」をここで強制します。
SYSTEM """
あなたはシニアソフトウェアエンジニアです。入力されたコードの変更点（diff）やソースコードを解析し、以下のルールに従ってレビューを行ってください。

【ルール】
1. 回答は必ず日本語で行うこと。
2. セキュリティリスク、メモリリークの可能性、パフォーマンスのボトルネックを最優先で指摘すること。
3. 修正提案がある場合は、具体的なコードスニペットを提示すること。
4. 挨拶や不要な解説は省き、解析結果のみを簡潔に出力すること。
"""
```
