# Test

## Overview
本文書は、Contract Agentプロジェクトのテスト設計について記述する。
プロジェクトは以下の2つの主要なテストファイルを含む：
- `test_tools.py`: スマートコントラクトツールの単体テスト
- `test_agent.py`: エージェントの統合テスト

## test_tools.py

スマートコントラクトツールの基本機能をテスト

### test_put_token
**目的**: NFT発行機能のテスト

**テスト手順**:
1. `get_tools`関数でツールを取得
2. `put_token_tool`でNFTをミント
   - 送信先: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
   - トークン名: "Test Token"
3. 返されたtoken_idを検証

**期待結果**: 
- token_idがNullでないこと
- token_idが-1でないこと（エラーでないこと）

### test_fetch_token
**目的**: トークン取得機能のテスト

**テスト手順**:
1. `get_tools`関数でツールを取得
2. `fetch_token_tool`（tools[1]）でトークンリストを取得
   - 対象アドレス: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
3. 取得したトークンリストを検証

**期待結果**:
- 返り値がlist型であること
- リストの長さが0より大きいこと
- リスト内の各要素がToken型であること

### test_reporting
**目的**: レポート生成機能のテスト

**テストケース**:
| ケース | token_list | token | reason | owner | 説明 |
|--------|------------|-------|--------|-------|------|
| 1 | "Token1, Token2, Token3" | "New Gaming NFT" | "Reward for completing quest" | `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` | 複数トークン存在 |
| 2 | "Digital Art Collection" | "Masterpiece #001" | "Artist collaboration event" | `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` | 単一トークン存在 |
| 3 | "" | "First Token" | "Initial mint" | `0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC` | トークンリスト空 |

**テスト手順**:
1. `get_tools`関数でツールを取得
2. `reporting_tool`（tools[2]）でレポートを生成
3. 生成されたレポートが期待する内容を含むことを確認

**期待結果**:
- レポートがstring型であること
- 各パラメータが正しい日本語形式で含まれていること
- `UnboundLocalError`が発生しないこと

**例外処理テスト**:
- `UnboundLocalError`が発生した場合、適切なエラーメッセージでテストが失敗すること

## test_agent.py

ContractAgentクラスの統合テストを実施する。

### test_agent_for_put_token
**目的**: トークンミント後のテスト

**テストケース**:
| ケース | トークン数 | ステータス | 期待結果 |
|--------|------------|------------|----------|
| 1 | 1つのトークン | "putToken" | NFT発行完了メッセージ |
| 2 | 2つのトークン | "putToken" | NFT発行完了メッセージ |

**テスト設定**:
```python
# Case 1: 単一トークンの場合
State(
    messages=[],
    tokens=[
        Token(
            from_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
            to_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
            token_id=1,
            token_name="TEST TOKEN",
        )
    ],
    address="",
    token_name="",
    status="putToken",
)
```

**テスト手順**:
1. ContractAgentインスタンスを作成
2. 各テストケースのStateで`get_agent`を実行しエージェントを初期化
3. レスポンスを検証

**期待結果**:
- `response.messages[0].content`がstring型であること
- `response.tokens`が空でないこと(入力したstate.tokenと同等のデータ)
- `response.status`が"reporting"であること
- メッセージに"NFTが発行されました"が含まれること

### test_agent_for_fetch_tokens
**目的**: トークン取得機能のテスト

**テスト設定**:
```python
State(
    messages=[],
    tokens=[],
    address="",
    token_name="",
    status="fetchTokens",
)
```

**テスト手順**:
1. ContractAgentインスタンスを作成
2. 空のトークンリストから開始してトークンを取得
3. レスポンスとトークンの詳細を検証

**期待結果**:
- `response.tokens`がNullでないこと
- `response.status`が"putToken"または"reporting"のいずれかであること
- 各トークンについて：
  - `from_address`がstring型であること
  - `to_address`がstring型であること
  - `token_id`がint型であること
  - `token_name`がstring型であること

### test_agent_for_reporting
**目的**: 様々なシナリオでのレポート生成機能のテスト

**テストケース**:

| ケース | トークン数 | 説明 | 期待ステータス |
|--------|------------|------|----------------|
| 1 | 0個 | NFTを発行していない場合 | "__end__" |
| 2 | 1個 | 1つのNFTを発行している場合 | "__end__" |
| 3 | 3個 | 複数のNFTを発行している場合 | "__end__" |

**詳細テストケース**:

**Case 1: NFTを発行していない場合**
```python
State(
    messages=[],
    tokens=[],
    address="",
    token_name="",
    status="reporting",
)
```

**Case 2: 1つのNFTを発行している場合**
```python
State(
    messages=[],
    tokens=[
        Token(
            from_address="0x0000000000000000000000000000000000000000",
            to_address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
            token_id=1,
            token_name="Gaming Achievement NFT",
        )
    ],
    address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    token_name="Gaming Achievement NFT",
    status="reporting",
)
```

**Case 3: 複数のNFTを発行している場合**
```python
State(
    messages=[],
    tokens=[
        Token(...),  # Gaming Achievement NFT
        Token(...),  # Art Collection NFT
        Token(...),  # Rare Digital Asset
    ],
    address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    token_name="New Token to Issue",
    status="reporting",
)
```

**テスト手順**:
1. ContractAgentインスタンスを作成
2. 各テストケースのStateで`get_agent`を実行
3. レスポンスとトークン数を検証

**期待結果**:
- `response.messages`がNullでないこと
- `response.status`が"__end__"であること
- `len(response.messages) > 0`であること
- 入力されたトークン数と期待されるトークン数が一致すること

**デバッグ出力**:
- テストケースの説明
- レスポンス全体
- 期待されるトークン数と実際のトークン数
- トークンリストが空でない場合は各トークンの詳細情報

## テスト実行方法

**個別テスト実行**
```bash
# tools テスト
pytest test/test_tools.py

# agent テスト
pytest test/test_agent.py

# 特定のテスト関数
pytest test/test_tools.py::test_put_token
```
