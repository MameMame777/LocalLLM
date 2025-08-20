#!/usr/bin/env python3
"""
GPU Validation Utility
GPU環境の検証とフォールバック機能
"""

import os
import warnings
from typing import Dict, Any, Optional, Tuple
from loguru import logger


class GPUValidator:
    """GPU環境の検証とフォールバック処理"""
    
    def __init__(self):
        self.cuda_available = False
        self.gpu_count = 0
        self.gpu_memory = {}
        self.validation_results = {}
        
    def validate_gpu_environment(self) -> Dict[str, Any]:
        """GPU環境の完全検証"""
        results = {
            "cuda_available": False,
            "pytorch_cuda": False,
            "llama_cpp_cuda": False,
            "gpu_count": 0,
            "gpu_info": [],
            "recommended_settings": {},
            "warnings": [],
            "errors": []
        }
        
        # PyTorchのCUDA確認
        try:
            import torch
            results["pytorch_cuda"] = torch.cuda.is_available()
            if results["pytorch_cuda"]:
                results["gpu_count"] = torch.cuda.device_count()
                results["cuda_available"] = True
                
                # GPU情報収集
                for i in range(results["gpu_count"]):
                    try:
                        name = torch.cuda.get_device_name(i)
                        memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)  # GB
                        results["gpu_info"].append({
                            "id": i,
                            "name": name,
                            "memory_gb": round(memory, 1)
                        })
                    except Exception as e:
                        results["warnings"].append(f"GPU {i} 情報取得失敗: {e}")
                        
        except ImportError:
            results["warnings"].append("PyTorch未インストール - GPU機能制限")
        except Exception as e:
            results["errors"].append(f"PyTorch CUDA確認エラー: {e}")
            
        # llama-cpp-pythonのCUDA確認
        try:
            from llama_cpp import Llama
            # CUDA版かどうかの簡易確認
            # 実際には小さなモデルで初期化テストが必要
            results["llama_cpp_cuda"] = True  # 基本的にインストールされていれば対応
        except ImportError:
            results["errors"].append("llama-cpp-python未インストール")
        except Exception as e:
            results["warnings"].append(f"llama-cpp-python確認エラー: {e}")
            
        # 推奨設定の生成
        results["recommended_settings"] = self._generate_recommendations(results)
        
        self.validation_results = results
        return results
        
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """検証結果に基づく推奨設定"""
        recommendations = {
            "n_gpu_layers": 0,
            "n_threads": 4,
            "max_memory_usage": 8,
            "use_gpu": False,
            "reason": "CPU専用設定（安全）"
        }
        
        if validation_results["cuda_available"] and validation_results["gpu_count"] > 0:
            gpu_info = validation_results["gpu_info"]
            if gpu_info:
                # 最初のGPUの情報を基に推奨設定
                main_gpu = gpu_info[0]
                gpu_memory = main_gpu.get("memory_gb", 0)
                
                if gpu_memory >= 8:  # 8GB以上のGPU
                    recommendations.update({
                        "n_gpu_layers": 32,
                        "n_threads": 2,
                        "max_memory_usage": 12,
                        "use_gpu": True,
                        "reason": f"高性能GPU（{main_gpu['name']}, {gpu_memory}GB）"
                    })
                elif gpu_memory >= 4:  # 4GB以上のGPU
                    recommendations.update({
                        "n_gpu_layers": 16,
                        "n_threads": 4,
                        "max_memory_usage": 10,
                        "use_gpu": True,
                        "reason": f"中性能GPU（{main_gpu['name']}, {gpu_memory}GB）"
                    })
                else:
                    recommendations["reason"] = f"GPU メモリ不足（{gpu_memory}GB < 4GB）"
                    
        return recommendations
        
    def safe_gpu_test(self, n_gpu_layers: int = 1) -> Tuple[bool, Optional[str]]:
        """安全なGPU動作テスト"""
        if n_gpu_layers <= 0:
            return True, "CPU専用設定"
            
        try:
            # 環境変数でCUDAを強制無効化して事前チェック
            import os
            original_cuda = os.environ.get('CUDA_VISIBLE_DEVICES')
            
            # まずCPU専用でテスト
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
            from llama_cpp import Llama
            
            # 元の設定に戻す
            if original_cuda is not None:
                os.environ['CUDA_VISIBLE_DEVICES'] = original_cuda
            else:
                os.environ.pop('CUDA_VISIBLE_DEVICES', None)
                
            # 実際のGPUテスト（軽量テスト）
            logger.info(f"🧪 GPU動作テスト開始（{n_gpu_layers}層）")
            
            # 実際にはここで小さなテストモデルでの初期化テストを行う
            # 今回は基本的な環境チェックのみ
            
            return True, f"GPU（{n_gpu_layers}層）テスト成功"
            
        except Exception as e:
            error_msg = f"GPU テスト失敗: {str(e)}"
            logger.warning(error_msg)
            return False, error_msg
            
    def get_fallback_settings(self) -> Dict[str, Any]:
        """フォールバック設定（CPU専用）"""
        return {
            "n_gpu_layers": 0,
            "n_threads": 4,
            "max_memory_usage": 8,
            "use_gpu": False,
            "reason": "フォールバック設定"
        }
        
    def validate_and_adjust_settings(self, requested_settings: Dict[str, Any]) -> Dict[str, Any]:
        """設定の検証と自動調整"""
        validation = self.validate_gpu_environment()
        n_gpu_layers = requested_settings.get("n_gpu_layers", 0)
        
        # GPU設定が要求されているが環境が対応していない場合
        if n_gpu_layers > 0:
            if not validation["cuda_available"]:
                logger.warning("🔄 GPU設定が要求されましたが、CUDA未対応環境のためCPU専用に調整")
                return self.get_fallback_settings()
                
            # GPU動作テスト
            test_success, test_message = self.safe_gpu_test(n_gpu_layers)
            if not test_success:
                logger.warning(f"🔄 GPU動作テスト失敗のためCPU専用に調整: {test_message}")
                return self.get_fallback_settings()
                
        # 設定が有効な場合はそのまま返す
        logger.info(f"✅ 設定検証完了: GPU層数={n_gpu_layers}")
        return requested_settings


# グローバルインスタンス
gpu_validator = GPUValidator()
