#!/usr/bin/env python3
"""
Enhanced JSON URL Processor with Individual URL Summarization
各URLを個別に要約してから統合するJSONプロセッサー
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
from loguru import logger

class IndividualJSONUrlProcessor:
    """
    各URLを個別に要約してから統合するJSONプロセッサー
    """
    
    def __init__(self):
        self.session = requests.Session()
        # 最新のUser-Agentと追加ヘッダーで403エラーを回避
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.max_content_length = 5000  # 各URLの最大コンテンツ長を削減
        self.request_timeout = 20  # タイムアウトを少し延長
        self.batch_size = 3  # バッチサイズをさらに削減して安定性向上
        self.max_retries = 2  # リトライ回数追加
        
        # LLM summarizer初期化を試行
        self.llm_summarizer = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """LLM要約機能を初期化"""
        try:
            from src.summarizer_enhanced import LLMSummarizer
            from config.settings import Settings
            from config.llama2_config import LLAMA2_MODEL_PATH
            
            settings = Settings()
            model_path = Path(LLAMA2_MODEL_PATH)
            
            if model_path.exists():
                logger.info("🤖 Initializing LLM for individual URL summarization...")
                self.llm_summarizer = LLMSummarizer(
                    model_path=str(model_path),
                    settings=settings
                )
                logger.success("✅ LLM summarizer initialized for individual processing")
            else:
                logger.warning("⚠️ LLM model not found - using basic summarization")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize LLM: {e}")
    
    def process_json_file_individually(self, json_file_path: Path) -> Dict[str, Any]:
        """JSONファイル内の各URLを個別に処理して要約（バッチ処理対応）"""
        try:
            logger.info(f"📄 Processing JSON file with optimized individual URL summarization: {json_file_path}")
            
            # JSONファイルを読み込み
            with open(json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # URLを抽出
            urls = self._extract_urls_from_json(json_data)
            logger.info(f"🔗 Found {len(urls)} URLs to process individually (batch size: {self.batch_size})")
            
            # バッチ処理で各URLを個別に処理
            individual_summaries = []
            successful_count = 0
            total_batches = (len(urls) + self.batch_size - 1) // self.batch_size
            
            for batch_num in range(total_batches):
                start_idx = batch_num * self.batch_size
                end_idx = min(start_idx + self.batch_size, len(urls))
                batch_urls = urls[start_idx:end_idx]
                
                logger.info(f"🔄 Processing batch {batch_num + 1}/{total_batches} ({len(batch_urls)} URLs)")
                
                # バッチ内の各URLを処理
                for i, url_info in enumerate(batch_urls):
                    url_idx = start_idx + i + 1
                    logger.info(f"🌐 Processing URL {url_idx}/{len(urls)}: {url_info['url']}")
                    
                    try:
                        # URLの内容を取得
                        content = self._fetch_url_content(url_info['url'])
                        if content:
                            # 個別に要約
                            summary = self._summarize_individual_url(url_info, content)
                            individual_summaries.append(summary)
                            successful_count += 1
                            logger.success(f"✅ Completed processing: {summary['name']}")
                        else:
                            logger.warning(f"⚠️ Failed to fetch: {url_info['url']}")
                            
                        # メモリ解放とレート制限
                        self._cleanup_memory()
                        time.sleep(0.5)  # レート制限を短縮
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing URL {url_info['url']}: {e}")
                        continue
                
                # バッチ処理後のメモリクリーンアップ
                logger.info(f"🧹 Cleaning up memory after batch {batch_num + 1}")
                self._cleanup_memory()
                
                # バッチ間の短い休憩
                if batch_num < total_batches - 1:
                    time.sleep(1)
            
            # 個別要約を統合
            logger.info(f"📝 Integrating {len(individual_summaries)} individual summaries...")
            integrated_summary = self._integrate_individual_summaries(
                individual_summaries, 
                json_file_path,
                len(urls),
                successful_count
            )
            
            return {
                'source_file': str(json_file_path),
                'total_urls': len(urls),
                'successful_summaries': successful_count,
                'individual_summaries': individual_summaries,
                'integrated_summary': integrated_summary,
                'processing_type': 'optimized_individual_url_summarization',
                'batch_size': self.batch_size
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing JSON file individually: {e}")
            raise
    
    def _summarize_individual_url(self, url_info: Dict[str, str], content: str) -> Dict[str, Any]:
        """個別URLの内容を要約"""
        try:
            # LLMによる要約
            if self.llm_summarizer and len(content) > 100:
                try:
                    logger.info(f"🤖 Creating LLM summary for: {url_info.get('name', 'Document')}")
                    
                    # コンテンツが長すぎる場合は適度に切り詰め
                    summary_content = content[:1500] if len(content) > 1500 else content
                    
                    summary = self.llm_summarizer.summarize_english_to_english(
                        summary_content,
                        summary_type="brief"  # 処理時間短縮のためbrief使用
                    )
                    
                    if summary and len(summary.strip()) > 10:
                        logger.success(f"✅ LLM summary generated for {url_info.get('name', 'Document')}")
                        return {
                            'name': url_info.get('name', 'Document'),
                            'url': url_info['url'],
                            'source': url_info.get('source', 'unknown'),
                            'category': url_info.get('category', 'Document'),
                            'summary': summary,
                            'content_length': len(content),
                            'summary_type': 'llm_generated'
                        }
                except Exception as e:
                    logger.warning(f"⚠️ LLM summarization failed for {url_info['url']}: {e}")
            
            # フォールバック: 基本的な要約
            basic_summary = self._create_basic_summary(content)
            
            return {
                'name': url_info.get('name', 'Document'),
                'url': url_info['url'],
                'source': url_info.get('source', 'unknown'),
                'category': url_info.get('category', 'Document'),
                'summary': basic_summary,
                'content_length': len(content),
                'summary_type': 'basic_extraction'
            }
            
        except Exception as e:
            logger.error(f"❌ Error summarizing URL {url_info['url']}: {e}")
            return {
                'name': url_info.get('name', 'Document'),
                'url': url_info['url'],
                'source': url_info.get('source', 'unknown'),
                'category': url_info.get('category', 'Document'),
                'summary': f"Error processing content: {str(e)}",
                'content_length': 0,
                'summary_type': 'error'
            }
    
    def _create_basic_summary(self, content: str) -> str:
        """基本的な要約を作成"""
        if not content or len(content) < 50:
            return "Content too short for summarization."
        
        # 文章を分割
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        
        # 最初の3文を要約として使用
        summary_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        summary = '. '.join(summary_sentences)
        
        if summary and not summary.endswith('.'):
            summary += '.'
        
        # 最大400文字に制限
        if len(summary) > 200:
            summary = summary[:200] + "..."
        
        return summary if summary else "Unable to generate basic summary."
    
    def _cleanup_memory(self):
        """メモリクリーンアップを実行"""
        try:
            import gc
            gc.collect()  # ガベージコレクション実行
            
            # LLMのメモリクリーンアップ（可能な場合）
            if hasattr(self.llm_summarizer, 'model') and hasattr(self.llm_summarizer.model, '_ctx'):
                # llama-cpp-pythonのコンテキストリセット
                pass  # 必要に応じて追加
                
        except Exception as e:
            logger.debug(f"Memory cleanup warning: {e}")
    
    def _integrate_individual_summaries(
        self, 
        individual_summaries: List[Dict[str, Any]], 
        source_file: Path, 
        total_urls: int, 
        successful_count: int
    ) -> str:
        """個別要約を統合して最終的な要約を作成"""
        
        integration_parts = []
        
        # ヘッダー
        header = f"""# Individual URL Processing Results
## Source File: {source_file}
## Processing Summary: {successful_count}/{total_urls} URLs individually processed and summarized

## Individual URL Summaries:

"""
        integration_parts.append(header)
        
        # 各個別要約
        for i, summary_data in enumerate(individual_summaries, 1):
            individual_section = f"""
### {i}. {summary_data['name']}
- **URL**: {summary_data['url']}
- **Source**: {summary_data['source']}
- **Category**: {summary_data['category']}
- **Content Length**: {summary_data['content_length']} characters
- **Summary Type**: {summary_data['summary_type']}

**Summary:**
{summary_data['summary']}

---
"""
            integration_parts.append(individual_section)
        
        # 統合要約（LLMが利用可能な場合）
        if self.llm_summarizer and len(individual_summaries) > 1:
            try:
                # 全ての個別要約を組み合わせ
                combined_summaries = "\n\n".join([
                    f"{s['name']}: {s['summary']}" for s in individual_summaries
                ])
                
                if len(combined_summaries) > 2000:
                    combined_summaries = combined_summaries[:2000] + "..."
                
                logger.info("🤖 Creating optimized integrated summary from individual summaries...")
                integrated_summary = self.llm_summarizer.summarize_english_to_english(
                    combined_summaries,
                    summary_type="brief"  # 統合要約も高速化
                )
                
                if integrated_summary and len(integrated_summary.strip()) > 10:
                    integration_parts.append(f"""
## Integrated Summary:

{integrated_summary}

---
""")
                    logger.success("✅ Integrated summary created from individual summaries")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to create integrated summary: {e}")
        
        # 統計情報
        stats = f"""
## Processing Statistics:
- Total URLs found: {total_urls}
- Successfully processed: {successful_count}
- Success rate: {(successful_count/total_urls*100):.1f}% if total_urls > 0 else 0.0%
- LLM summaries: {sum(1 for s in individual_summaries if s['summary_type'] == 'llm_generated')}
- Basic summaries: {sum(1 for s in individual_summaries if s['summary_type'] == 'basic_extraction')}
"""
        integration_parts.append(stats)
        
        return "".join(integration_parts)
    
    def _extract_urls_from_json(self, json_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """JSONデータからURL情報を抽出"""
        urls = []
        
        # fpga_documents構造を処理
        if 'fpga_documents' in json_data:
            for doc in json_data['fpga_documents']:
                if isinstance(doc, dict) and 'url' in doc:
                    urls.append({
                        'url': doc['url'],
                        'name': doc.get('title', doc.get('name', f"FPGA Document {len(urls)+1}")),
                        'source': 'fpga_documents',
                        'category': doc.get('category', 'FPGA Documentation')
                    })
        
        # sources構造を処理
        if 'sources' in json_data:
            for source_name, source_data in json_data['sources'].items():
                if isinstance(source_data, dict) and 'documents' in source_data:
                    for doc in source_data['documents']:
                        if 'url' in doc:
                            urls.append({
                                'url': doc['url'],
                                'name': doc.get('name', doc.get('title', f"Document from {source_name}")),
                                'source': source_name,
                                'category': doc.get('category', 'Document')
                            })
        
        # 直接的なURLリストも処理
        if 'urls' in json_data:
            for url_item in json_data['urls']:
                if isinstance(url_item, str):
                    urls.append({
                        'url': url_item,
                        'name': f"Document_{len(urls)+1}",
                        'source': 'direct_url',
                        'category': 'Document'
                    })
                elif isinstance(url_item, dict) and 'url' in url_item:
                    urls.append({
                        'url': url_item['url'],
                        'name': url_item.get('name', f"Document_{len(urls)+1}"),
                        'source': url_item.get('source', 'direct_url'),
                        'category': url_item.get('category', 'Document')
                    })
        
        return urls
    
    def _fetch_url_content(self, url: str) -> Optional[str]:
        """URLから内容を取得（リトライ機能付き）"""
        import time
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"🌐 Fetching (attempt {attempt + 1}/{self.max_retries + 1}): {url}")
                
                # 特定サイト向けの最適化
                headers = {}
                if 'intel.com' in url:
                    headers.update({
                        'Referer': 'https://www.intel.com/',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache'
                    })
                elif 'arxiv.org' in url:
                    headers.update({
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                    })
                
                response = self.session.get(url, timeout=self.request_timeout, headers=headers)
                response.raise_for_status()
                
                # HTMLからテキストを抽出
                if 'text/html' in response.headers.get('content-type', ''):
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 不要な要素を除去
                    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                        element.decompose()
                    
                    # メインコンテンツを抽出
                    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|body'))
                    
                    if main_content:
                        text = main_content.get_text(separator=' ', strip=True)
                    else:
                        text = soup.get_text(separator=' ', strip=True)
                    
                    # テキストをクリーンアップ
                    text = re.sub(r'\s+', ' ', text)
                    text = re.sub(r'\n\s*\n', '\n\n', text)
                    
                else:
                    # プレーンテキストとして処理
                    text = response.text
                
                # 長すぎる場合は切り詰め
                if len(text) > self.max_content_length:
                    text = text[:self.max_content_length] + "..."
                    logger.debug(f"✂️ Truncated content for {url} to {self.max_content_length} characters")
                
                return text
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    wait_time = (attempt + 1) * 2  # 指数バックオフ
                    logger.warning(f"⚠️ Request failed for {url} (attempt {attempt + 1}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"❌ All retry attempts failed for {url}: {e}")
                    return None
            except Exception as e:
                logger.warning(f"⚠️ Error processing {url}: {e}")
                return None
        
        return None  # すべての試行が失敗した場合
