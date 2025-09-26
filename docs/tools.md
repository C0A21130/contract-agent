# Tool

[tools.py](/tools/tools.py)はコントラクトエージェントが使用する3つの主要なツールを定義している

## Put token

**機能**: スマートコントラクトを呼び出してNFTを発行・転送する

**処理の流れ**:

- コントラクトの発行元アドレスを取得 (contract.get_address())
- 指定された名前でNFTを発行 (contract.mint())
- 発行されたNFTを指定アドレスに転送 (contract.transfer())

## Fetch tokens

**機能**: スマートコントラクトを呼び出しNFTの取引履歴を取得する

**処理内容**:

- contract.fetch_tokens() を呼び出して全てのNFT取引履歴を取得
    - ERC721のTransfer Eventを取得する
- 戻り値: Tokenオブジェクトのリスト
    - from_address: 転送元アドレス
    - to_address: 転送先アドレス
    - token_id: トークンID
    - token_name: トークン名

## Reporting
- **機能**: エージェントの最終的状態や行動の結果を日本語のレポートとして出力する
- **レポート内容**:
    - 発行されたNFT一覧
    - 発行したNFTの情報
    - NFTを発行した理由
    - 自身の情報
