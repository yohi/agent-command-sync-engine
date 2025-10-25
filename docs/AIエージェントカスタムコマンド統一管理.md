

# **ポリ-エージェント開発における統合コマンドフレームワークの設計：ClaudeCode、Codex、GeminiCLIのためのクロスプラットフォーム戦略**

## **序論**

### **ポリ-エージェント・ワークフローの台頭**

現代のソフトウェア開発環境は、単一のツールで完結する時代から、複数の特化したAIエージェントを組み合わせる「ポリ-エージェント」の時代へと移行しつつある。開発者が特定のタスクに最適なプログラミング言語を選択するように、コード生成、リファクタリング、デバッグ、ドキュメンテーションといった各々のタスクにおいて、それぞれ異なる強みを持つAIエージェントを使い分けるワークフローが主流になり始めている。この動向は、生産性を飛躍的に向上させる可能性を秘めている一方で、新たな課題、すなわちツールの断片化という問題を生み出している。

### **統合の戦略的必要性**

開発者がClaudeCode、Codex、GeminiCLIといった複数のAIエージェントを日常的に利用する環境において、各エージェントが独自のカスタムコマンドシステムを持つことは、深刻な非効率性を生む。同じ目的のコマンドをエージェントごとに再定義する必要があり、これは単なる手間の問題にとどまらない。コマンドの挙動に微妙な差異が生じ、一貫性が失われることで、開発者の認知負荷は増大する。したがって、コマンドシステムを統一することは、単なる利便性の向上ではなく、ポリ-エージェント環境における生産性とスケーラビリティを維持するための戦略的必須要件である。

### **統一における中心的課題の概観**

本レポートでは、3つの主要なAIエージェントCLIにまたがるカスタムコマンドの統一管理システムを構築する上で直面する、技術的な障壁を詳細に分析し、解決策を提示する。主な課題は以下の通りである。

1. **互換性のないファイルフォーマット**: ClaudeCodeとCodexがMarkdown (.md) を採用する一方、GeminiCLIはTOML (.toml) を使用しており、根本的な非互換性が存在する 1。  
2. **発散するディレクトリ構造とスコープ**: 各エージェントは、ユーザーレベルとプロジェクトレベルでコマンドを探索する仕組みを持つが、その実装、特にCodex CLIの現状の制約には大きな差異がある 4。  
3. **矛盾する構文**: 引数やシェルコマンド実行のためのプレースホルダー構文がエージェントごとに異なり、単純なファイル共有を不可能にしている 2。  
4. **サードパーティフレームワークの統合**: SuperClaudeのような拡張フレームワークは、独自のインストーラーを通じてコマンドを配置するため、統一管理の枠組みに組み込むための特別な配慮が必要となる 9。

### **アーキテクチャに関する基本方針**

これらの課題を解決するためには、シンボリックリンクのような単純なファイルシステムレベルのアプローチでは不十分である。本レポートが提示する中心的なアーキテクチャは、普遍的なソースフォーマットから各エージェント固有のフォーマットへとコマンドを変換・配備する、プログラム的な「同期エンジン」の構築である。さらに、将来的な展望として、各エージェントが共通して投資を進めているモデルコンテキストプロトコル（MCP）を活用した、より高度で洗練されたアーキテクチャについても論じる。

---

## **第1章 AIエージェントのコマンドアーキテクチャ比較分析**

統一フレームワークを設計する上で、まず各AIエージェントCLIが持つコマンドシステムの内部構造、機能、そして制約を正確に理解することが不可欠である。本章では、ClaudeCode、Codex CLI、GeminiCLIの3つのシステムを詳細に比較分析する。

### **1.1 ClaudeCode: 成熟し、拡張性に富んだシステム**

ClaudeCodeのコマンドシステムは、その成熟度と拡張性の高さにおいて際立っている。

* **コマンドの定義**: カスタムコマンドはMarkdown (.md) ファイルとして定義される。ファイル名（拡張子を除く）がそのままコマンド名となる、直感的な仕組みを採用している 1。  
* **階層的なスコープ**: ClaudeCodeの最大の強みは、明確に定義されたコマンドの探索階層にある。ユーザーのホームディレクトリ配下の \~/.claude/commands/ に配置されたコマンドは、全てのプロジェクトで利用可能な「パーソナルコマンド」として機能する。一方、プロジェクトのルートディレクトリ配下の .claude/commands/ に配置されたコマンドは、そのプロジェクト内でのみ有効な「プロジェクトコマンド」となり、Gitを通じてチームメンバーと共有できる。同じ名前のコマンドが存在する場合、プロジェクトコマンドがパーソナルコマンドを上書きする仕様となっており、これにより明確な優先順位が確立されている 1。  
* **構文と機能**: プロンプト内では、$1、$2 のような位置引数や、全ての引数を一括で受け取る $ARGUMENTS プレースホルダーが利用可能である 8。また、\! を接頭辞として付与することで、シェルコマンドを直接実行し、その標準出力をプロンプトに埋め込むことができる 1。@ を用いたファイルコンテンツの参照もサポートされている 8。さらに、ファイルの先頭にYAMLフロントマターを記述することで、description（説明）や allowed-tools（許可ツール）といったメタデータを定義でき、高度な制御が可能となっている 8。  
* **エコシステムとの統合**: このシステムは拡張性を前提に設計されており、プラグインやMCPサーバーが独自のカスタムコマンドを動的に追加する仕組みを備えている 1。これは、ClaudeCodeが単なるツールではなく、統合を前提としたプラットフォームであることを示している。

### **1.2 Codex CLI: ユーザー中心で進化を続ける実装**

Codex CLIのコマンドシステムは、ClaudeCodeと同様のアプローチを取りつつも、いくつかの重要な違いと制約が存在する。

* **コマンドの定義**: ClaudeCodeと同様に、コマンドはMarkdown (.md) ファイルとして定義される 3。  
* **スコープの制約**: 現時点での最大の制約は、プロジェクトレベルのスコープをサポートしていない点である。コマンドはユーザーのホームディレクトリ配下の \~/.codex/prompts/ からのみ読み込まれる 5。  
* **プロジェクトスコープへの潜在的需要**: この制約は、開発者の実際のワークフローとの間に乖離を生じさせている。GitHubのIssueには、プロジェクト固有のコマンドをサポートするための機能リクエスト（例：{project root}/.codex/prompts/ からの読み込み）が提出されている 7。これは単なる機能不足ではなく、プロジェクトのソースコードと共にプロンプトをバージョン管理したいという、開発者の根源的な要求の表れである。したがって、我々が設計する統一アーキテクチャは、この将来的な機能追加を予期し、対応可能な前方互換性のある設計でなければならない。  
* **構文と機能**: システムは活発な開発の途上にある。初期の実装は基本的なものだったが、引数プレースホルダー ($ARGUMENTS, $1..$9) やメタデータのためのフロントマターサポートを追加する提案やプルリクエストが進行中であり、将来的にはClaudeCodeとの機能的パリティが高まることが期待される 15。

### **1.3 GeminiCLI: モダンで構造化されたフレームワーク**

GeminiCLIは、他の2つのエージェントとは一線を画す、モダンで構造化されたアプローチを採用している。

* **コマンドの定義**: コマンド定義にはTOML (.toml) フォーマットが採用されている。これにより、prompt \= "..." や description \= "..." といったキーと値のペアによる、より厳格で構造化された定義が強制される 2。  
* **ClaudeCodeと同等のスコープ**: スコープの扱いにおいては、ClaudeCodeの強力なモデルを踏襲している。ユーザーグローバルな \~/.gemini/commands/ と、プロジェクトローカルな .gemini/commands/ の両方をサポートしており、個人利用とチームベースのワークフローの両方に適している 2。  
* **機能的な名前空間**: サブディレクトリの扱いが決定的な違いを生んでいる。例えば、git/commit.toml というパスに配置されたコマンドは、/git:commit という名前で呼び出される。これにより、コマンドの衝突を確実に防ぐ、真に機能的な名前空間が実現される 2。これは、単に整理目的でしかないClaudeCodeやCodexのサブディレクトリとは本質的に異なる、より堅牢な仕組みである。  
* **独自の構文**: 引数には {{args}}、シェルコマンド実行には \!{...} という独自の構文を採用しており、他のエージェントとの間でコマンドを共有するには明示的な変換処理が必要となる 2。  
* **エコシステムとの統合**: ClaudeCodeと同様にMCPとの深い統合が図られており、接続されたMCPサーバーが公開するプロンプトから自動的にスラッシュコマンドを生成する能力を持つ 。また、公式な「拡張機能（extensions）」フレームワークも提供されている 17。

---

## **第2章 統一への中心的課題とアーキテクチャ要件**

前章の比較分析から、3つのエージェントCLIのコマンドシステムを統一する上で克服すべき具体的な技術的課題が明らかになる。本章では、これらの課題を明確に定義し、成功するソリューションが満たすべきアーキテクチャ要件を導出する。

### **2.1 三つの非互換性**

統一を阻む根本的な要因は、ファイルフォーマット、構文、そして名前空間のセマンティクスという3つの領域における非互換性である。

* **ファイルフォーマットの相違**: ClaudeCodeとCodexが採用する柔軟なMarkdown (.md) と、GeminiCLIが採用する構造化されたTOML (.toml) との間の根本的な違い。  
* **構文の不一致**: 引数プレースホルダー ($ARGUMENTS vs {{args}}) とシェルコマンド実行 (\! vs \!{...}) の構文が異なり、単純なテキストレベルでの互換性がない。  
* **セマンティクスの不一致**: ClaudeCode/Codexにおけるサブディレクトリが単なる整理目的（装飾的）であるのに対し、GeminiCLIではコロン (:) を用いた衝突回避のための名前空間（機能的）として扱われる。

### **2.2 スコープの非対称性**

アーキテクチャ上の最大の障害は、Codex CLIがプロジェクトレベルのスコープをサポートしていない点である 7。統一システムは、この非対称性を巧みに処理する必要がある。例えば、当面の対策として全てのコマンドをCodexのユーザーレベルディレクトリに配備しつつ、将来的な機能追加に備えてプロジェクトレベルへの配備も可能な設計にしておく、といった戦略が考えられる。

### **2.3 サードパーティ統合のジレンマ: SuperClaudeの事例**

SuperClaudeのようなフレームワークは、pip や npm といったパッケージマネージャーと、SuperClaude install のような専用のインストールコマンドを用いて、自身のコマンドファイルを管理する 9。

このインストールプロセスは、我々が構築する統一システムの観点からは、内部が窺い知れない「ブラックボックス」として機能する。インストーラーは、我々の直接的な制御が及ばない形で、エージェント固有のディレクトリ（例：\~/.claude/commands/sc/）にファイルを配置する 9。このプロセスを単純に妨げることはできない。したがって、我々のシステムは、この外部からの操作に「反応」する形で設計されなければならない。これは、単にコマンドの配置を妨げるのではなく、(1) サードパーティのインストーラーを実行させ、(2) 新たにインストールされたコマンドを「発見」し、(3) それらを我々の中央リポジトリに「取り込み」、管理と変換の対象とする、という多段階のプロセスを意味する。この発想の転換により、問題は「防止」から「事後的な統合と調整」へと変化する。

### **2.4 アーキテクチャ要件の抽出と比較マトリクス**

これまでの分析に基づき、実用的なソリューションは以下の要件を**必ず**満たさなければならない。

1. エージェントに依存しない、普遍的なソースフォーマットを利用すること。  
2. プログラムによる変換と同期のレイヤーを実装すること。  
3. 各エージェントの異なるスコープルールをインテリジェントに処理すること。  
4. サードパーティのインストーラーから提供されるコマンドを統合するための明確なワークフローを提供すること。

以下の比較マトリクスは、第1章の分析結果を要約し、次章で詳述するアーキテクチャ設計の論理的根拠を視覚的に示すものである。この表は、3つのツールのドキュメントに散在する情報を一つの高密度な成果物に凝縮し、フォーマット、構文、スコープにおける根本的な非互換性を一目で明らかにする。これにより、なぜプログラムによる変換が不可欠であるかが自明となり、提案するアーキテクチャの複雑さが正当化される。

**表1: AIエージェント コマンドシステム機能比較マトリクス**

| 機能 | ClaudeCode | Codex CLI | GeminiCLI |
| :---- | :---- | :---- | :---- |
| **コマンドファイル形式** | Markdown (.md) | Markdown (.md) 3 | TOML (.toml) |
| **ユーザーレベルスコープ** | \~/.claude/commands/ 4 | \~/.codex/prompts/ 5 | \~/.gemini/commands/ 6 |
| **プロジェクトレベルスコープ** | 対応 (.claude/commands/) | 非対応 (機能リクエストあり 7) | 対応 (.gemini/commands/) |
| **引数構文** | $ARGUMENTS, $1 8 | $ARGUMENTS, $1 (提案中 15) | {{args}} 6 |
| **シェル実行構文** | \!git status 8 | (プロンプトファイル内では非対応) | \!{git status} |
| **名前空間** | サブディレクトリ (装飾的) | サブディレクトリ (装飾的) | サブディレクトリ (機能的、: を使用) |
| **設定ファイル** | settings.json 14 | config.toml 19 | settings.json 20 |
| **拡張性** | プラグイン, MCP | MCP 21 | 拡張機能, MCP 17 |

---

## **第3章 統合コマンドセンターの設計：段階的アーキテクチャアプローチ**

本章では、分析からソリューションへと移行し、考えられる戦略を評価した上で、詳細かつ堅牢なアーキテクチャを提示する。

### **3.1 戦略1: シンボリックリンクアプローチ – 実現可能性の評価**

このアプローチは、中央にコマンド管理用のディレクトリを一つ作成し、各エージェントのコマンドディレクトリ（例：\~/.claude/commands/）からそこへシンボリックリンクを張るというものである。

この戦略は、その単純さにもかかわらず、根本的な欠陥を抱えている。ファイルフォーマットの非互換性（.md vs .toml）や構文の不一致（$ARGUMENTS vs {{args}}）を全く解決できない。したがって、真の統一システムとしては機能不全であり、採用することはできない。ただし、ClaudeCodeとCodexの間で互換性のあるMarkdownコマンドを共有するといった、限定的な用途でのみ有効である可能性は残る 12。

### **3.2 戦略2: 中央リポジトリと同期エンジン（推奨アーキテクチャ）**

本レポートが推奨する核心的な提案は、コマンド管理に対する「ビルド時」アプローチである。これは、コマンドを直接配置するのではなく、普遍的なソースから各エージェント専用のファイルを生成し、配備（デプロイ）する仕組みを指す。

#### **3.2.1 「信頼できる唯一の情報源」: 普遍的なコマンド定義**

まず、エージェントに依存しない普遍的なコマンドフォーマットを定義する。最も理想的な選択肢は、拡張されたYAMLフロントマターを持つMarkdown (.md) ファイルである。Markdownの本文はプロンプトとしてそのまま利用し、フロントマターに各エージェント固有のメタデータや設定を格納する。

**普遍的フォーマットの例 (my-command.md):**

YAML

\---  
description: "git statusを説明するための普遍的なコマンド"  
\# Gemini固有のメタデータ  
gemini:  
  \# 現時点では特になし  
\# Claude固有のメタデータ  
claude:  
  allowed-tools:  
    \- "Bash(git status:\*)"  
\# Codex固有のメタデータ  
codex:  
  \# 将来的なフロントマター対応のためのプレースホルダー  
\---  
\`\!{SHELL:git status}\` の出力に基づいて、リポジトリの現在の状態を説明してください。  
ユーザーは次の引数を渡しました: {ARGS}

このフォーマットでは、{ARGS} や {SHELL:...} のような抽象的なプレースホルダーを使用する。これらのプレースホルダーは、後述する同期エンジンによって、各エージェント固有の構文へと変換される。

#### **3.2.2 同期スクリプト: 変換エンジン**

次に、この普遍的フォーマットを解釈し、各エージェント用のファイルを生成するスクリプト（Python、Node.js、あるいはシェルスクリプト）のロジックを設計する。スクリプトは以下のステップを実行する。

1. **スキャン**: ソースリポジトリ内の全ての .md ファイルを再帰的に探索する。  
2. **パース**: 各ファイルについて、YAMLフロントマターとMarkdown本文を解析する。  
3. **変換と生成**:  
   * **ClaudeCode用**: {ARGS} を $ARGUMENTS に、{SHELL:cmd} を \!cmd に置換する。ClaudeCode固有のフロントマターを持つ最終的な .md ファイルを生成する。  
   * **Codex用**: ClaudeCodeと同様の変換を行い、.md ファイルを生成する。  
   * **GeminiCLI用**: TOML構造を生成する。description をフロントマターから設定する。プロンプト本文を変換し、{ARGS} を {{args}} に、{SHELL:cmd} を \!{cmd} に置換する。最終的な .toml ファイルを生成する。  
4. **配備**: 生成されたファイルを、各エージェントの適切なディレクトリ（\~/.claude/commands、\~/.codex/prompts など）に配置する。その際、名前空間のルールを遵守する（GeminiCLIのためにはサブディレクトリを作成し、パス区切り文字 / を : に変換する）。

#### **3.2.3 スコープの管理**

同期スクリプトは、--scope=project や \--scope=user といったフラグを受け付けるべきである。これにより、出力先をプロジェクトローカルなディレクトリ（例：./.gemini/commands/）にするか、ユーザーグローバルなディレクトリ（例：\~/.gemini/commands/）にするかを制御できる。

### **3.3 高度な代替案: 統一コマンドMCPサーバー**

3つのエージェント全てがMCP（Model Context Protocol）への投資を強化しているという事実は、この技術が将来の標準となることを示唆している 1。これは、よりエレガントで将来性のある解決策が可能であることを意味する。ディスク上のファイルを操作する方法は、設定の変更が反映されるまでに再起動が必要であったり、環境による差異が生じやすかったりする脆さを持つ。それに対し、エージェント公式の拡張プロトコルであるMCPを利用することで、ソリューションをファイルシステム層からアプリケーションプロトコル層へと引き上げることができる。

具体的には、コマンド定義をホストする単一のローカルMCPサーバーを構築する。各CLIエージェントが起動時にこのサーバーに接続すると、MCPプロトコルを通じて利用可能なコマンド（プロンプト）が動的に発見され、スラッシュコマンドとして利用可能になる。

* **アーキテクチャ概要**:  
  * 軽量なローカルサーバー（例：Node.js/Express、Python/FastAPI）。  
  * 利用可能な「プロンプト」（我々のコマンド）をMCPフォーマットで記述して返すエンドポイント。  
  * サーバーは、戦略2で定義した普遍的なコマンドソースディレクトリから定義を読み込む。  
* **利点**: エージェントの再起動なしでコマンドが動的に読み込まれる。設定が各エージェントの設定ファイル（settings.json や config.toml）にMCPサーバーを追加するだけで完結する。ツール開発者のアーキテクチャ方針と合致している。  
* **欠点**: 実装の複雑性が高い。MCPの「プロンプトをコマンドとして扱う」機能が、ファイルベースのコマンド定義ほど表現力豊かでない可能性がある。特にCodex CLIにおけるサポートが他のエージェントに比べて成熟していない可能性がある。  
* **推奨**: このMCPサーバーアプローチを、長期的な目標である「フェーズ2」または「エンタープライズ級」ソリューションと位置づける。そして、同期エンジンアプローチを、即座に価値を提供し、かつ実現可能な「フェーズ1」として実装することを推奨する。

---

## **第4章 SuperClaudeのようなサードパーティフレームワークの統合**

フレームワークによってインストールされるコマンドを統一管理の枠組みに組み込むことは、特有の課題を伴う。本章では、この課題に対する具体的かつ実行可能な戦略を提示する。

### **4.1 「インストールをソースとする」パターン**

ここでの基本原則は、フレームワークのインストールプロセス自体を、管理対象となるコマンドの「新たなソース」として扱うことである。

### **4.2 ラッパースクリプトによるワークフロー**

プロセス全体を統括するマスターセットアップスクリプト（例：setup-environment.sh）を導入する。このスクリプトは以下の手順を自動的に実行する。

1. **フレームワークのインストール**: スクリプトはまず、pipx install SuperClaude && SuperClaude install のような標準的なインストールコマンドを呼び出す 9。  
2. **コマンドの取り込み（Ingest）**: インストール完了後、スクリプトはフレームワークがコマンドを配置したディレクトリ（例：\~/.claude/commands/sc/）をスキャンし、全ての .md ファイルを特定する。  
3. **中央リポジトリへのコピー**: 特定したコマンドファイルを、バージョン管理下にある中央コマンドリポジトリ内の専用サブディレクトリ（例：central-commands/\_frameworks/superclaude/）にコピーする。  
4. **同期の実行**: 最後に、スクリプトは第3章で設計したメインの同期エンジンを実行し、取り込んだコマンドを含む全ての中央リポジトリのコマンドを各エージェント用に変換・配備する。

### **4.3 非互換性の取り扱いと手動での適応**

このアプローチの限界を明確に認識することが極めて重要である。SuperClaudeから取り込まれたコマンドは、ClaudeCodeでの動作を前提に記述されている。同期スクリプトはこれらのファイルをCodex用にコピーすることはできるが、完全な動作は保証されない。そして、GeminiのTOMLフォーマットへ自動的に変換することは**不可能**である。

したがって、最善の策は、中央リポジトリに取り込まれたフレームワークのコマンドを、クロスエージェント互換性が必要な場合の「手動変換のためのソース素材」と見なすことである。これにより、ユーザーは現実的な期待値を持つことができる。

---

## **第5章 実装ガイドと運用上のベストプラクティス**

本章では、これまでに設計したアーキテクチャを、エンドユーザーが実行可能なステップバイステップのガイドに落とし込む。

### **5.1 中央コマンドリポジトリのセットアップ**

Gitで管理する中央リポジトリとして、以下のディレクトリ構造を推奨する。

/unified-ai-commands  
├── commands/              \# ユーザー定義の普遍的コマンド  
│   ├── git/  
│   │   └── commit.md  
│   └── review.md  
├── frameworks/            \# 取り込まれたフレームワークのコマンド  
│   └── superclaude/  
│       └── sc/  
│           └── plan.md  
├── sync.py                \# 同期エンジンスクリプト  
└── Makefile               \# 自動化のためのショートカット

この構造により、ユーザーが自作したコマンドと、フレームワークから取り込んだコマンドが明確に分離され、管理が容易になる。

### **5.2 同期スクリプトの実践**

同期スクリプトの核心部分について、Pythonによる実装例を以下に示す。このスニペットは、YAMLフロントマターの解析、構文変換のための文字列置換、そして最終的なTOML/Markdownフォーマットへの書き出しといった主要なロジックを実証する。

Python

import os  
import re  
import yaml  
import toml  
from pathlib import Path

SOURCE\_DIR \= Path("commands")  
FRAMEWORK\_DIR \= Path("frameworks")  
TARGET\_BASE\_USER \= Path.home()

def sync\_commands(scope="user"):  
    \#... スコープに応じたターゲットパスの設定...

    \# ユーザー定義コマンドとフレームワークコマンドをスキャン  
    source\_files \= list(SOURCE\_DIR.rglob("\*.md")) \+ list(FRAMEWORK\_DIR.rglob("\*.md"))

    for src\_path in source\_files:  
        with open(src\_path, 'r', encoding='utf-8') as f:  
            content \= f.read()

        \# フロントマターと本文を分離  
        parts \= content.split('---', 2)  
        frontmatter \= yaml.safe\_load(parts) if len(parts) \> 1 else {}  
        body \= parts.strip() if len(parts) \> 2 else content

        \# ターゲットパスを計算  
        relative\_path \= src\_path.relative\_to(SOURCE\_DIR if src\_path.is\_relative\_to(SOURCE\_DIR) else FRAMEWORK\_DIR)

        \# 1\. ClaudeCode 用の生成  
        claude\_body \= body.replace("{ARGS}", "$ARGUMENTS")  
        claude\_body \= re.sub(r"\!{SHELL:(.\*?)}", r"\!\\1", claude\_body)  
        \#... claude\_target\_path を計算し、フロントマターと結合して書き込み...

        \# 2\. Codex 用の生成  
        codex\_body \= claude\_body \# 現状はClaudeと互換  
        \#... codex\_target\_path を計算し、書き込み...

        \# 3\. Gemini 用の生成  
        gemini\_body \= body.replace("{ARGS}", "{{args}}")  
        gemini\_body \= re.sub(r"\!{SHELL:(.\*?)}", r"\!{\\1}", gemini\_body)  
        gemini\_toml\_data \= {  
            "description": frontmatter.get("description", ""),  
            "prompt": gemini\_body  
        }  
        \#... gemini\_target\_path (名前空間':'を含む)を計算し、TOMLとして書き込み...

if \_\_name\_\_ \== "\_\_main\_\_":  
    sync\_commands(scope="user") \# or "project"

### **5.3 自動化とワークフローへの統合**

この同期プロセスを日常のワークフローにシームレスに組み込むことで、その真価が発揮される。

* **Makefile / npm scripts**: make sync-user や make sync-project のような単純なコマンドをMakefileやpackage.jsonに定義することで、同期スクリプトの実行を簡略化する。  
* **Gitフック**: post-merge や post-checkout といったGitフックを設定することを強く推奨する。これにより、git pull やブランチの切り替えで中央コマンドリポジトリが更新されるたびに、同期スクリプトが自動的に実行される。結果として、ローカルのCLI環境は、バージョン管理されている「信頼できる唯一の情報源」と常に同期が保たれる状態になる。

### **5.4 長期的なメンテナンスと発展**

* **バージョニング**: 中央コマンドリポジトリ自体をセマンティックバージョニングで管理し、変更内容を追跡可能にすることが望ましい。  
* **CLIの進化への追随**: 各CLIツールは継続的にアップデートされる。例えば、Codexがプロジェクトレベルのスコープをサポートした場合、同期スクリプトを修正して対応する必要がある。スクリプトをモジュール化し、各エージェントの生成ロジックを分離しておくことで、このような変更に容易に対応できる。  
* **MCPサーバーへの移行**: 長期的な視点では、このファイルベースの同期システムは、第3章で述べたMCPサーバーベースのアーキテクチャへの移行パスと考えるべきである。普遍的なコマンド定義は、MCPサーバーが提供するプロンプトのデータソースとして再利用できるため、これまでの投資が無駄になることはない。

---

## **結論**

### **提言の要約**

本レポートは、ClaudeCode、Codex CLI、GeminiCLIという3つの主要なAIエージェントCLIにまたがるカスタムコマンドを統一的に管理するための、堅牢かつ実践的なアーキテクチャを提示した。単純なシンボリックリンクによるアプローチが、ファイルフォーマットや構文の非互換性により機能不全に陥ることを示した上で、\*\*「中央リポジトリと同期エンジン」\*\*を中核とするアーキテクチャを推奨する。このアプローチは、普遍的なソースフォーマットから各エージェント固有のコマンドファイルをプログラムによって生成・配備するものであり、現状の技術的制約下で最も効果的なソリューションである。また、SuperClaudeのようなサードパーティフレームワークについては、そのインストールプロセスをコマンドソースとして扱い、ラッパースクリプトを通じて中央リポジトリに取り込むという統合パターンを提案した。

### **未来は統合される**

本レポートで設計したようなカスタムフレームワークの必要性は、ポリ-エージェント・ワークフローが標準となるにつれて、今後ますます高まっていくだろう。この動向の根底にあるのは、AIツール統合の流れである。各ツールがMCPのような共通のプロトコルを採用し始めている事実は、将来的には、ファイルシステムレベルでの操作に頼るのではなく、プロトコル駆動型のシームレスな統合が主流になることを示唆している。本レポートで提案したアーキテクチャは、その未来への移行を円滑に進めるための重要な布石となる。

### **最終的な行動喚起**

開発者は、まずファイルベースの同期エンジンを実装することから始めるべきである。このアプローチは、直ちに価値を提供し、日々のワークフローにおける非効率性を解消する。同時に、このシステムは、将来的にMCPベースのより高度なアーキテクチャへと移行するための強固な基盤を構築するものであり、長期的な視点からも賢明な投資と言えるだろう。

#### **引用文献**

1. Slash commands \- Claude Docs, 10月 25, 2025にアクセス、 [https://docs.claude.com/en/docs/claude-code/slash-commands](https://docs.claude.com/en/docs/claude-code/slash-commands)  
2. Gemini CLI: Custom slash commands | Google Cloud Blog, 10月 25, 2025にアクセス、 [https://cloud.google.com/blog/topics/developers-practitioners/gemini-cli-custom-slash-commands](https://cloud.google.com/blog/topics/developers-practitioners/gemini-cli-custom-slash-commands)  
3. How does Codex create a custom prompt for reuse? | by 陳仕偉| Sep, 2025 \- Medium, 10月 25, 2025にアクセス、 [https://areckkimo.medium.com/how-does-codex-create-a-custom-prompt-for-reuse-7ec5135b93d1](https://areckkimo.medium.com/how-does-codex-create-a-custom-prompt-for-reuse-7ec5135b93d1)  
4. How to Add Custom Slash Commands in Claude Code \- AI Engineer Guide, 10月 25, 2025にアクセス、 [https://aiengineerguide.com/blog/claude-code-custom-command/](https://aiengineerguide.com/blog/claude-code-custom-command/)  
5. Codex CLI added custom prompts : r/ClaudeCode \- Reddit, 10月 25, 2025にアクセス、 [https://www.reddit.com/r/ClaudeCode/comments/1n3a2rt/codex\_cli\_added\_custom\_prompts/](https://www.reddit.com/r/ClaudeCode/comments/1n3a2rt/codex_cli_added_custom_prompts/)  
6. Gemini CLI Tutorial Series — Part 7 : Custom slash commands | by Romin Irani \- Medium, 10月 25, 2025にアクセス、 [https://medium.com/google-cloud/gemini-cli-tutorial-series-part-7-custom-slash-commands-64c06195294b](https://medium.com/google-cloud/gemini-cli-tutorial-series-part-7-custom-slash-commands-64c06195294b)  
7. Look for custom prompts in {project root}/.codex/prompts/ first · Issue \#4734 · openai/codex, 10月 25, 2025にアクセス、 [https://github.com/openai/codex/issues/4734](https://github.com/openai/codex/issues/4734)  
8. How to Create Custom Slash Commands in Claude Code \- BioErrorLog Tech Blog (en), 10月 25, 2025にアクセス、 [https://en.bioerrorlog.work/entry/claude-code-custom-slash-command](https://en.bioerrorlog.work/entry/claude-code-custom-slash-command)  
9. SuperClaude-Org/SuperClaude\_Framework: A ... \- GitHub, 10月 25, 2025にアクセス、 [https://github.com/SuperClaude-Org/SuperClaude\_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework)  
10. @bifrost\_inc/superclaude \- npm Package Security Analysis \- S... \- Socket.dev, 10月 25, 2025にアクセス、 [https://socket.dev/npm/package/@bifrost\_inc/superclaude](https://socket.dev/npm/package/@bifrost_inc/superclaude)  
11. Claude Code Slash Commands: Boost Your Productivity with Custom Automation, 10月 25, 2025にアクセス、 [https://alexop.dev/tils/claude-code-slash-commands-boost-productivity/](https://alexop.dev/tils/claude-code-slash-commands-boost-productivity/)  
12. Claude Code Custom Slash Commands Hierarchy \- Dan Corin, 10月 25, 2025にアクセス、 [https://www.danielcorin.com/til/anthropic/custom-slash-commands-hierarchy/](https://www.danielcorin.com/til/anthropic/custom-slash-commands-hierarchy/)  
13. Claude Code: Best practices for agentic coding \- Anthropic, 10月 25, 2025にアクセス、 [https://www.anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)  
14. Claude Code settings, 10月 25, 2025にアクセス、 [https://docs.claude.com/en/docs/claude-code/settings](https://docs.claude.com/en/docs/claude-code/settings)  
15. Custom prompts \- passing arguments · Issue \#2890 · openai/codex \- GitHub, 10月 25, 2025にアクセス、 [https://github.com/openai/codex/issues/2890](https://github.com/openai/codex/issues/2890)  
16. Gemini CLI Custom Slash Commands \- AI Engineer Guide, 10月 25, 2025にアクセス、 [https://aiengineerguide.com/blog/gemini-cli-custom-slash-commands/](https://aiengineerguide.com/blog/gemini-cli-custom-slash-commands/)  
17. Now open for building: Introducing Gemini CLI extensions, 10月 25, 2025にアクセス、 [https://blog.google/technology/developers/gemini-cli-extensions/](https://blog.google/technology/developers/gemini-cli-extensions/)  
18. SuperClaude \- PyPI, 10月 25, 2025にアクセス、 [https://pypi.org/project/SuperClaude/](https://pypi.org/project/SuperClaude/)  
19. Configuring Codex \- OpenAI Developers, 10月 25, 2025にアクセス、 [https://developers.openai.com/codex/local-config/](https://developers.openai.com/codex/local-config/)  
20. Google Gemini CLI Cheatsheet \- Philschmid, 10月 25, 2025にアクセス、 [https://www.philschmid.de/gemini-cli-cheatsheet](https://www.philschmid.de/gemini-cli-cheatsheet)  
21. Configuring Codex \- OpenAI Developers, 10月 25, 2025にアクセス、 [https://developers.openai.com/codex/local-config](https://developers.openai.com/codex/local-config)  
22. Hands-on with Gemini CLI \- Google Codelabs, 10月 25, 2025にアクセス、 [https://codelabs.developers.google.com/gemini-cli-hands-on](https://codelabs.developers.google.com/gemini-cli-hands-on)  
23. Gemini CLI | Gemini Code Assist \- Google for Developers, 10月 25, 2025にアクセス、 [https://developers.google.com/gemini-code-assist/docs/gemini-cli](https://developers.google.com/gemini-code-assist/docs/gemini-cli)