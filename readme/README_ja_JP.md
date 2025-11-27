# AgentBay Dify プラグイン

[English](../README.md) | [中文文档](README_zh.md)

## はじめに

**AgentBay**は、Alibaba Cloud WuYingが提供するクラウドサンドボックスサービスで、Linux、Windows、ブラウザなどの隔離されたコンピューティング環境を提供し、AI Agentがコードの実行、ファイル操作、ブラウザ自動化などの複雑なタスクを安全に実行できるようにします。
AgentBayの詳細情報と使用方法については、公式ウェブサイトの情報をご参照ください：https://www.aliyun.com/product/agentbay


**本プラグインの価値:**

従来のAI Agentはテキストベースのやり取りに限定され、実際の計算タスクを実行できませんでした。本プラグインはAgentBayを統合することで、Difyアプリケーションに「実際の行動能力」を付与します:

- 🔧 **コード実行**: 隔離環境でPython、Shellスクリプトを実行し、データ分析、ファイル変換などを処理
- 🌐 **ブラウザ自動化**: Webブラウジング、フォーム入力、データスクレイピング、Web操作を自動化
- 📁 **ファイル操作**: クラウドファイルの読み書き、ドキュメントやログの処理
- 🖥️ **デスクトップ自動化**: Windowsアプリケーションを制御し、RPAワークフローを実現
- ☁️ **クラウドベース**: すべての操作はクラウドで実行され、セキュリティが隔離され、ローカル環境は不要

**典型的なユースケース:**
- データ分析Agent: Pythonスクリプトを実行してユーザーがアップロードしたデータを分析
- WebスクレイピングAgent: 自動的にWebサイトにアクセスして情報を抽出
- 自動テストAgent: Webアプリケーションの自動テストを実行
- ドキュメント処理Agent: ファイル形式の一括変換と処理
- RPAオフィスAgent: 反復的なデスクトップ操作を自動化

## 機能

### セッション管理
- 様々なクラウド環境を作成（Linux、Browser、Code、Windows、Mobile）
- すべてのアクティブセッションを表示・管理
- セッションを安全に削除してリソースをクリーンアップ

### コマンド＆コード実行
- クラウド環境でShellコマンドを実行
- Pythonや他のプログラミング言語を実行
- 設定可能な実行タイムアウト

### ファイル操作
- ファイルの読み書き
- ディレクトリ内容のリスト表示

### ブラウザ自動化
- Webナビゲーション、要素操作（クリック、入力、スクロール）
- ページスクリーンショット、コンテンツ抽出
- 要素分析、ローディング待機

### デスクトップUI自動化
- デスクトップスクリーンショット
- マウスクリック、キーボード入力

## クイックスタート

### APIキーの取得
[AgentBayコンソール](https://agentbay.console.aliyun.com/service-management)にアクセスしてAPIキーを取得してください。

### プラグインの設定
Difyにプラグインをインストールした後、APIキーパラメータを設定します。

### 基本的な使用方法

**1. セッションの作成**
```
ツール: session_create
パラメータ:
- image_id: linux_latest (オプション、デフォルトはlinux_latest)
  オプション: browser_latest, code_latest, windows_latest, mobile_latest
```

**2. 操作の実行**

コマンド実行:
```
ツール: command_execute
パラメータ:
- session_id: <セッションID>
- command: "ls -la"
- timeout_ms: 30000 (オプション)
```

ファイル操作:
```
ツール: file_operations
パラメータ:
- session_id: <セッションID>
- action: read (またはwrite、list)
- file_path: /path/to/file (read/writeの場合必須)
```

ブラウザ自動化:
```
ツール: browser_automation
パラメータ:
- session_id: <セッションID>
- action: navigate (またはclick、type、screenshotなど)
- url: https://example.com (navigateの場合必須)
```

**3. リソースのクリーンアップ**
```
ツール: session_delete
パラメータ:
- session_id: <セッションID>
- sync_context: false (オプション)
```

## デモサンプル

プラグインの機能を紹介するすぐに使えるデモサンプルを提供しています。これらのサンプルは [demo ディレクトリ](https://github.com/5101good/agentbay-dify-plugin/tree/main/demo) にあります。

> **注意**：これらのデモは参考および教育目的のみのシンプルなサンプルです。

以下の手順でDifyにこれらのサンプルをインポートできます：
1. [demo ディレクトリ](https://github.com/5101good/agentbay-dify-plugin/tree/main/demo) からデモファイル（Dify DSL形式）をダウンロード
2. Difyで「スタジオ」に移動し、「DSLファイルをインポート」をクリック
3. ダウンロードしたデモファイルを選択してインポート
4. インポートしたワークフローでAgentBay APIキーを設定
5. デモを実行してプラグインの動作を確認

## ツールリファレンス

### session_create
新しいクラウド環境セッションを作成します。5つの環境タイプをサポート: `linux_latest`（デフォルト）、`browser_latest`（ブラウザ）、`code_latest`（開発）、`windows_latest`（Windows）、`mobile_latest`（モバイル）。後続の操作に使用するsession_idを返します。

### session_list
現在のアカウントでこのプラグインによって作成されたすべてのアクティブセッションをリストし、セッションID、環境タイプなどの情報を表示します。

### session_delete
指定されたセッションを削除し、クラウドリソースを解放します。操作完了後は速やかにクリーンアップすることを推奨します。

### command_execute
セッション内でShellコマンドを実行します。カスタム作業ディレクトリとタイムアウトをサポート。Linux/Windows環境でのコマンドライン操作に適しています。

### code_execute
セッション内でコードを実行します。Pythonやその他のプログラミング言語をサポート。作業ディレクトリを指定でき、データ処理、自動化スクリプトなどに適しています。

### file_operations
統合ファイル操作ツール。`action`パラメータで操作タイプを指定:
- **read**: ファイル内容を読み取る
- **write**: ファイルに書き込む（存在しないファイルは自動作成）
- **list**: ディレクトリ内容をリスト表示

### browser_automation
フル機能のブラウザ自動化ツール。`browser_latest`環境が必要です。`action`パラメータで複数の操作をサポート:
- **navigate**: Webページにアクセス
- **click/type**: ページ要素と対話（CSSセレクタで位置指定）
- **scroll**: ページスクロール
- **screenshot**: ページスクリーンショットをキャプチャ（フルページまたはビューポートをサポート）
- **get_content**: ページHTMLコンテンツを取得
- **analyze_elements**: ページ構造を分析して正しいセレクタを見つける
- **wait_element/wait**: 要素を待機または遅延

### ui_operations
デスクトップUI自動化ツール。Windows、ブラウザなどのグラフィカル環境に適しています。`action`パラメータでサポート:
- **screenshot**: デスクトップスクリーンショットをキャプチャ
- **click**: 指定座標でクリック
- **type**: テキストを入力
- **key**: 指定キーを押す（例: Enter、Tabなど）

## ユースケース

**Web自動化テスト**
1. browser_latestセッションを作成
2. browser_automationを使用してナビゲートと対話
3. スクリーンショットで結果を検証
4. セッションを削除

**データ処理**
1. code_latestセッションを作成
2. file_operationsを使用してデータファイルをアップロード
3. code_executeを使用して分析スクリプトを実行
4. file_operationsを使用して結果をダウンロード
5. セッションを削除

**システム運用**
1. linux_latestセッションを作成
2. command_executeを使用してチェックコマンドを実行
3. file_operationsを使用してログを読み取る
4. セッションを削除

## 既知の問題

**⚠️ Dify公式クラウドプラットフォームでは使用できません**

ネットワーク制限により、Dify公式クラウドプラットフォーム（cloud.dify.ai）からAgentBayサービスにアクセスできないため、プラグインの初期化が失敗します。

**解決策**：セルフホストされたDifyインスタンスでこのプラグインを使用してください。

## リンク

- [AgentBayコンソール](https://agentbay.console.aliyun.com)
- [AgentBay SDK](https://github.com/aliyun/wuying-agentbay-sdk)

## お問い合わせ

- GitHub Issues
- Email: 5101good@gmail.com

## 免責事項
本プラグインは技術ツールとして提供されており、使用時は以下の点にご注意ください：

1. **合法的な使用**: すべての操作が法律および規制に準拠していることを確認し、違法な目的で使用しないでください
2. **データ責任**: ユーザーは処理するデータに責任を負い、機密情報の処理は避けることをお勧めします
3. **サービス依存**: Alibaba Cloud WuYing AgentBayサービス利用規約に従う必要があります
4. **リスク自己負担**: 使用にはデータ損失、サービス中断などのリスクがあり、ユーザーが自己責任で負担します
5. **責任制限**: 開発者は使用によって生じるいかなる損失についても責任を負いません

本プラグインを使用することで、上記の条項に同意したものとみなされます。
