"""
JSON URL Processor for LocalLLM
JSONファイルからURLを抽出し、各URLの内容を要約するプロセッサー
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import time
import re
from bs4 import BeautifulSoup
from loguru import logger


class JSONUrlProcessor:
    """JSONファイルからURLを抽出して要約処理を行うクラス"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.max_content_length = 50000  # 最大コンテンツ長
        self.request_timeout = 30  # リクエストタイムアウト（秒）
        
    def process_json_file(self, json_file_path: Path) -> Dict[str, Any]:
        """JSONファイルを処理してURL一覧を抽出し、各URLの内容を取得"""
        try:
            logger.info(f"📄 Processing JSON file: {json_file_path}")
            
            # JSONファイルを読み込み
            with open(json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # URLを抽出
            urls = self._extract_urls_from_json(json_data)
            logger.info(f"🔗 Found {len(urls)} URLs to process")
            
            # 各URLの内容を取得
            url_contents = []
            for i, url_info in enumerate(urls, 1):
                logger.info(f"🌐 Processing URL {i}/{len(urls)}: {url_info['url']}")
                
                content = self._fetch_url_content(url_info['url'])
                if content:
                    url_contents.append({
                        'name': url_info.get('name', f"Document_{i}"),
                        'url': url_info['url'],
                        'source': url_info.get('source', 'unknown'),
                        'category': url_info.get('category', 'Document'),
                        'content': content,
                        'content_length': len(content)
                    })
                    logger.success(f"✅ Successfully fetched: {url_info.get('name', 'Document')} ({len(content)} chars)")
                else:
                    logger.warning(f"⚠️ Failed to fetch: {url_info['url']}")
                
                # レート制限のため少し待機
                time.sleep(1)
            
            return {
                'source_file': str(json_file_path),
                'total_urls': len(urls),
                'successful_fetches': len(url_contents),
                'url_contents': url_contents,
                'metadata': json_data.get('scan_info', {})
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing JSON file: {e}")
            raise
    
    def _extract_urls_from_json(self, json_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """JSONデータからURL情報を抽出"""
        urls = []
        
        # sources構造を処理
        if 'sources' in json_data:
            for source_name, source_data in json_data['sources'].items():
                if 'documents' in source_data:
                    for doc in source_data['documents']:
                        if 'url' in doc:
                            urls.append({
                                'name': doc.get('name', 'Unknown Document'),
                                'url': doc['url'],
                                'source': source_name,
                                'category': doc.get('category', 'Document'),
                                'file_type': doc.get('file_type', 'html')
                            })
        
        # その他の構造も処理（柔軟性のため）
        urls.extend(self._recursive_url_search(json_data))
        
        # 重複を除去
        seen_urls = set()
        unique_urls = []
        for url_info in urls:
            if url_info['url'] not in seen_urls:
                seen_urls.add(url_info['url'])
                unique_urls.append(url_info)
        
        return unique_urls
    
    def _recursive_url_search(self, data: Any, urls: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """再帰的にURL文字列を検索"""
        if urls is None:
            urls = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'url' and isinstance(value, str) and value.startswith('http'):
                    # 既に追加済みでなければ追加
                    if not any(u['url'] == value for u in urls):
                        urls.append({
                            'name': data.get('name', 'Extracted URL'),
                            'url': value,
                            'source': data.get('source', 'extracted'),
                            'category': data.get('category', 'Document'),
                            'file_type': data.get('file_type', 'html')
                        })
                else:
                    self._recursive_url_search(value, urls)
        elif isinstance(data, list):
            for item in data:
                self._recursive_url_search(item, urls)
        
        return urls
    
    def _fetch_url_content(self, url: str) -> Optional[str]:
        """URLからコンテンツを取得してテキストに変換"""
        try:
            logger.debug(f"🌐 Fetching: {url}")
            
            response = self.session.get(url, timeout=self.request_timeout)
            response.raise_for_status()
            
            # Content-Typeをチェック
            content_type = response.headers.get('content-type', '').lower()
            
            if 'text/html' in content_type:
                return self._extract_text_from_html(response.text, url)
            elif 'application/pdf' in content_type:
                logger.warning(f"⚠️ PDF content detected for {url}, skipping (PDF processing requires separate handler)")
                return None
            elif 'text/' in content_type:
                return response.text[:self.max_content_length]
            else:
                logger.warning(f"⚠️ Unsupported content type: {content_type} for {url}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ Error processing {url}: {e}")
            return None
    
    def _extract_text_from_html(self, html_content: str, url: str) -> str:
        """HTMLコンテンツからテキストを抽出"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 不要な要素を除去
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # メインコンテンツを取得
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|body'))
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)
            
            # テキストをクリーンアップ
            text = re.sub(r'\s+', ' ', text)  # 複数の空白を1つに
            text = re.sub(r'\n\s*\n', '\n\n', text)  # 複数の改行を整理
            
            # 長すぎる場合は切り詰め
            if len(text) > self.max_content_length:
                text = text[:self.max_content_length] + "..."
                logger.debug(f"✂️ Truncated content for {url} to {self.max_content_length} characters")
            
            return text
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting text from HTML for {url}: {e}")
            return ""
    
    def create_summary_content(self, url_data: Dict[str, Any]) -> str:
        """URL処理結果から要約用のコンテンツを作成"""
        
        summary_parts = []
        
        # ヘッダー情報
        header = f"""# JSON URL Processing Results
## Source File: {url_data['source_file']}
## Processing Summary: {url_data['successful_fetches']}/{url_data['total_urls']} URLs successfully processed

"""
        summary_parts.append(header)
        
        # 各URLの内容
        for i, url_content in enumerate(url_data['url_contents'], 1):
            url_section = f"""
## Document {i}: {url_content['name']}
**Source:** {url_content['source']}
**Category:** {url_content['category']}
**URL:** {url_content['url']}
**Content Length:** {url_content['content_length']} characters

### Content:
{url_content['content']}

---
"""
            summary_parts.append(url_section)
        
        combined_content = "\n".join(summary_parts)
        
        # メタデータ追加
        if url_data.get('metadata'):
            metadata_section = f"""
## Source Metadata
```json
{json.dumps(url_data['metadata'], indent=2, ensure_ascii=False)}
```
"""
            combined_content += metadata_section
        
        return combined_content


# テスト関数
def test_json_url_processor():
    """JSON URL プロセッサーのテスト"""
    
    # テスト用のJSONファイルパス
    json_file = Path("e:/Nautilus/Desktop/fpga_documents.json")
    
    if not json_file.exists():
        logger.error(f"❌ Test JSON file not found: {json_file}")
        return False
    
    try:
        processor = JSONUrlProcessor()
        
        logger.info("🧪 Testing JSON URL Processor")
        logger.info(f"📄 Processing: {json_file}")
        
        # JSONファイルを処理
        result = processor.process_json_file(json_file)
        
        # 要約コンテンツを作成
        summary_content = processor.create_summary_content(result)
        
        # 結果を出力ファイルに保存
        output_dir = Path("output/json_url_test")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"fpga_documents_processed_{int(time.time())}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        logger.success(f"✅ JSON URL processing completed!")
        logger.info(f"📊 Results:")
        logger.info(f"   📁 Source: {result['source_file']}")
        logger.info(f"   🔗 Total URLs: {result['total_urls']}")
        logger.info(f"   ✅ Successful: {result['successful_fetches']}")
        logger.info(f"   📄 Output: {output_file}")
        logger.info(f"   📝 Content Length: {len(summary_content)} characters")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ JSON URL processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_json_url_processor()
