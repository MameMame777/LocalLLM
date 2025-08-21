# LocalLLM API サーバー 使用ガイド

別プロジェクトからLocalLLMの要約機能を利用するための完全ガイドです。

## 🌐 APIサーバーの特徴

LocalLLMには以下のAPIサーバー機能が実装されています：

### 1. FastAPI ベースのWebサーバー (`document_api.py`)
- **URL**: `http://localhost:8000`
- **フォーマット**: RESTful API
- **ドキュメント**: `http://localhost:8000/docs` (Swagger UI)

### 2. 対応エンドポイント

#### ヘルスチェック
```
GET /health
```
レスポンス:
```json
{
  "status": "healthy",
  "timestamp": 1692672000.0
}
```

#### API情報
```
GET /
```
レスポンス:
```json
{
  "service": "LocalLLM Document Processing API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "process_single": "/api/v1/process",
    "process_batch": "/api/v1/batch",
    "get_task": "/api/v1/task/{task_id}",
    "health": "/health"
  }
}
```

#### 単一ドキュメント処理
```
POST /api/v1/process
```

**リクエスト例（テキストコンテンツ）:**
```json
{
  "content": "ここに要約したいテキストを入力...",
  "language": "ja",
  "max_length": 150,
  "use_llm": false,
  "auto_detect_language": true,
  "output_format": "markdown"
}
```

**リクエスト例（URL）:**
```json
{
  "url": "https://example.com/article.html",
  "language": "ja",
  "max_length": 200,
  "use_llm": true,
  "auto_detect_language": true,
  "output_format": "markdown"
}
```

**レスポンス例:**
```json
{
  "status": "success",
  "content": "処理されたマークダウンコンテンツ...",
  "summary": "要約されたテキスト...",
  "metadata": {
    "processing_time": 3.45
  }
}
```

#### バッチ処理
```
POST /api/v1/batch
```

**リクエスト例:**
```json
{
  "urls": [
    "https://example1.com/doc1.html",
    "https://example2.com/doc2.html"
  ],
  "language": "ja",
  "max_length": 150,
  "use_llm": false,
  "auto_detect_language": true,
  "parallel_workers": 4
}
```

**レスポンス例:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Batch processing started for 2 documents"
}
```

#### タスク状況確認
```
GET /api/v1/task/{task_id}
```

**レスポンス例:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 1.0,
  "created_at": 1692672000.0,
  "completed_at": 1692672120.0,
  "total_urls": 2,
  "completed_urls": 2,
  "results": [
    {
      "url": "https://example1.com/doc1.html",
      "status": "success",
      "summary": "文書1の要約...",
      "processing_time": 2.3
    },
    {
      "url": "https://example2.com/doc2.html",
      "status": "success",
      "summary": "文書2の要約...",
      "processing_time": 1.8
    }
  ],
  "errors": []
}
```

## 🚀 APIサーバーの起動方法

```bash
# LocalLLMプロジェクトディレクトリで実行
cd "e:\Nautilus\workspace\pythonworks\LocalLLM"

# 必要な依存関係をインストール
pip install fastapi uvicorn

# APIサーバーを起動
python src\api\document_api.py
```

サーバー起動後、以下のURLでアクセス可能：
- API: `http://localhost:8000`
- ドキュメント: `http://localhost:8000/docs`

## 🔧 外部プロジェクトからの使用例

### Python での使用例

```python
import requests
import time
from typing import Dict, Any, List

class LocalLLMClient:
    """LocalLLM APIクライアント"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """APIサーバーが利用可能かチェック"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def summarize_text(self, text: str, language: str = "ja", 
                      max_length: int = 150, use_llm: bool = False) -> Dict[str, Any]:
        """テキストを要約"""
        payload = {
            "content": text,
            "language": language,
            "max_length": max_length,
            "use_llm": use_llm,
            "auto_detect_language": True,
            "output_format": "markdown"
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/process",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def summarize_url(self, url: str, language: str = "ja", 
                     max_length: int = 150, use_llm: bool = False) -> Dict[str, Any]:
        """URLのコンテンツを要約"""
        payload = {
            "url": url,
            "language": language,
            "max_length": max_length,
            "use_llm": use_llm,
            "auto_detect_language": True,
            "output_format": "markdown"
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/process",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def batch_process(self, urls: List[str], language: str = "ja", 
                     max_length: int = 150, use_llm: bool = False,
                     parallel_workers: int = 4) -> str:
        """複数URLをバッチ処理（タスクIDを返す）"""
        payload = {
            "urls": urls,
            "language": language,
            "max_length": max_length,
            "use_llm": use_llm,
            "auto_detect_language": True,
            "parallel_workers": parallel_workers
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/batch",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        return result["task_id"]
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """タスクの状況を確認"""
        response = self.session.get(f"{self.base_url}/api/v1/task/{task_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def wait_for_batch_completion(self, task_id: str, 
                                 check_interval: int = 2) -> Dict[str, Any]:
        """バッチ処理の完了を待機"""
        while True:
            status = self.get_task_status(task_id)
            
            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                raise Exception(f"Batch processing failed: {status.get('error', 'Unknown error')}")
            
            print(f"Progress: {status['progress']:.1%}")
            time.sleep(check_interval)

# 使用例
def main():
    # クライアント初期化
    client = LocalLLMClient()
    
    # ヘルスチェック
    if not client.health_check():
        print("APIサーバーが利用できません")
        return
    
    # テキスト要約
    text_result = client.summarize_text(
        "ここに要約したいテキストを入力...",
        language="ja",
        max_length=100,
        use_llm=True
    )
    print(f"テキスト要約: {text_result['summary']}")
    
    # URL要約
    url_result = client.summarize_url(
        "https://example.com/article",
        language="ja",
        max_length=150
    )
    print(f"URL要約: {url_result['summary']}")
    
    # バッチ処理
    urls = [
        "https://example1.com/doc1",
        "https://example2.com/doc2"
    ]
    task_id = client.batch_process(urls, language="ja", use_llm=True)
    print(f"バッチ処理開始: {task_id}")
    
    # 完了を待機
    final_result = client.wait_for_batch_completion(task_id)
    print(f"バッチ処理完了: {len(final_result['results'])}件")
    
    for result in final_result['results']:
        print(f"- {result['url']}: {result['summary'][:100]}...")

if __name__ == "__main__":
    main()
```

### JavaScript/Node.js での使用例

```javascript
const axios = require('axios');

class LocalLLMClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.client = axios.create({ timeout: 30000 });
    }
    
    async healthCheck() {
        try {
            const response = await this.client.get(`${this.baseUrl}/health`);
            return response.status === 200;
        } catch {
            return false;
        }
    }
    
    async summarizeText(text, options = {}) {
        const payload = {
            content: text,
            language: options.language || 'ja',
            max_length: options.maxLength || 150,
            use_llm: options.useLLM || false,
            auto_detect_language: true,
            output_format: 'markdown'
        };
        
        const response = await this.client.post(
            `${this.baseUrl}/api/v1/process`,
            payload
        );
        return response.data;
    }
    
    async summarizeUrl(url, options = {}) {
        const payload = {
            url: url,
            language: options.language || 'ja',
            max_length: options.maxLength || 150,
            use_llm: options.useLLM || false,
            auto_detect_language: true,
            output_format: 'markdown'
        };
        
        const response = await this.client.post(
            `${this.baseUrl}/api/v1/process`,
            payload
        );
        return response.data;
    }
    
    async batchProcess(urls, options = {}) {
        const payload = {
            urls: urls,
            language: options.language || 'ja',
            max_length: options.maxLength || 150,
            use_llm: options.useLLM || false,
            auto_detect_language: true,
            parallel_workers: options.parallelWorkers || 4
        };
        
        const response = await this.client.post(
            `${this.baseUrl}/api/v1/batch`,
            payload
        );
        return response.data.task_id;
    }
    
    async getTaskStatus(taskId) {
        const response = await this.client.get(`${this.baseUrl}/api/v1/task/${taskId}`);
        return response.data;
    }
}

// 使用例
async function main() {
    const client = new LocalLLMClient();
    
    // ヘルスチェック
    if (!(await client.healthCheck())) {
        console.log('APIサーバーが利用できません');
        return;
    }
    
    // テキスト要約
    const textResult = await client.summarizeText(
        'ここに要約したいテキストを入力...',
        { language: 'ja', maxLength: 100, useLLM: true }
    );
    console.log(`テキスト要約: ${textResult.summary}`);
    
    // URL要約
    const urlResult = await client.summarizeUrl(
        'https://example.com/article',
        { language: 'ja', maxLength: 150 }
    );
    console.log(`URL要約: ${urlResult.summary}`);
}

main().catch(console.error);
```

## 📋 パラメータ仕様

### 共通パラメータ

| パラメータ | 型 | デフォルト | 説明 |
|-----------|---|----------|------|
| `language` | string | "ja" | 出力言語（ja/en） |
| `max_length` | integer | 150 | 要約の最大文字数 |
| `use_llm` | boolean | false | LLM使用（高品質だが低速） |
| `auto_detect_language` | boolean | true | 自動言語検出 |
| `output_format` | string | "markdown" | 出力形式 |

### use_llm の使い分け

- **false**: 高速処理、基本的な要約
- **true**: 高品質要約、LLMによる深い理解

## 🔧 トラブルシューティング

### APIサーバーに接続できない
1. APIサーバーが起動しているか確認
2. ポート8000が使用可能か確認
3. ファイアウォール設定を確認

### 要約品質が低い
1. `use_llm: true` を設定
2. `max_length` を増やす
3. `language` を適切に設定

### 処理が遅い
1. `use_llm: false` に設定
2. `parallel_workers` を調整
3. `max_length` を減らす

## 🎯 まとめ

LocalLLMのAPIサーバーを使用することで、別プロジェクトから簡単に要約機能を利用できます。RESTful APIなので、あらゆるプログラミング言語から呼び出し可能です。

**主な利点:**
- シンプルなREST API
- 同期・非同期処理の両対応
- バッチ処理による効率化
- 豊富な設定オプション
- Swagger UIによる詳細ドキュメント
