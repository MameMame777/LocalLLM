#!/usr/bin/env python3
"""
Academic Document Processing GUI
Specialized interface for academic papers and technical documents
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from academic.academic_processor import AcademicDocumentProcessor

class AcademicGUI:
    """学術・技術文書処理専用GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Academic Document Processor - 学術論文・技術文書専用処理システム")
        self.root.geometry("1400x900")
        
        # プロセッサー初期化
        self.processor = AcademicDocumentProcessor()
        self.current_file = None
        self.processing_thread = None
        
        # スタイル設定
        self.setup_styles()
        
        # GUI構築
        self.create_widgets()
        
    def setup_styles(self):
        """スタイル設定"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # カスタムスタイル
        style.configure('Academic.TFrame', background='#f8f9fa')
        style.configure('Academic.TLabel', background='#f8f9fa', font=('Arial', 10))
        style.configure('Academic.TButton', font=('Arial', 10, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#2c3e50')
        style.configure('Section.TLabel', font=('Arial', 11, 'bold'), foreground='#34495e')
        
    def create_widgets(self):
        """GUI要素作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, style='Academic.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 上部: ファイル選択・設定エリア
        self.create_file_selection_area(main_frame)
        
        # 中央: 処理結果表示エリア
        self.create_results_area(main_frame)
        
        # 下部: 詳細分析エリア
        self.create_analysis_area(main_frame)
        
        # 右側: 構造解析エリア
        self.create_structure_area(main_frame)
        
    def create_file_selection_area(self, parent):
        """ファイル選択・設定エリア"""
        # ファイル選択フレーム
        file_frame = ttk.LabelFrame(parent, text="📁 ファイル選択", style='Academic.TFrame')
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # ファイル選択
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_select_frame, text="論文ファイル:", style='Academic.TLabel').pack(side=tk.LEFT)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=80)
        self.file_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        
        ttk.Button(file_select_frame, text="参照", command=self.browse_file, style='Academic.TButton').pack(side=tk.RIGHT)
        
        # 処理設定フレーム
        settings_frame = ttk.Frame(file_frame)
        settings_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 文書タイプ設定
        ttk.Label(settings_frame, text="文書タイプ:", style='Academic.TLabel').pack(side=tk.LEFT)
        self.doc_type_var = tk.StringVar(value="auto")
        doc_type_combo = ttk.Combobox(settings_frame, textvariable=self.doc_type_var, 
                                     values=["auto", "research_paper", "technical_report", "patent", "manual"], 
                                     state="readonly", width=15)
        doc_type_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # 詳細レベル設定
        ttk.Label(settings_frame, text="詳細レベル:", style='Academic.TLabel').pack(side=tk.LEFT)
        self.detail_level_var = tk.StringVar(value="standard")
        detail_combo = ttk.Combobox(settings_frame, textvariable=self.detail_level_var,
                                   values=["brief", "standard", "detailed", "comprehensive"],
                                   state="readonly", width=15)
        detail_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # 処理ボタン
        self.process_button = ttk.Button(settings_frame, text="🎓 論文解析開始", 
                                        command=self.start_processing, style='Academic.TButton')
        self.process_button.pack(side=tk.RIGHT, padx=(20, 0))
        
        # プログレスバー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(file_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # ステータス
        self.status_var = tk.StringVar(value="ファイルを選択してください")
        ttk.Label(file_frame, textvariable=self.status_var, style='Academic.TLabel').pack(padx=10, pady=(0, 5))
        
    def create_results_area(self, parent):
        """処理結果表示エリア"""
        # 左側フレーム（要約結果）
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 要約結果フレーム
        summary_frame = ttk.LabelFrame(left_frame, text="📄 論文要約結果")
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 要約表示
        summary_text_frame = ttk.Frame(summary_frame)
        summary_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.summary_text = scrolledtext.ScrolledText(summary_text_frame, wrap=tk.WORD, font=('Arial', 10))
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # 要約操作ボタン
        summary_button_frame = ttk.Frame(summary_frame)
        summary_button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(summary_button_frame, text="📋 コピー", command=self.copy_summary).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(summary_button_frame, text="💾 保存", command=self.save_summary).pack(side=tk.LEFT, padx=5)
        ttk.Button(summary_button_frame, text="🔄 再処理", command=self.reprocess).pack(side=tk.RIGHT)
        
    def create_analysis_area(self, parent):
        """詳細分析エリア"""
        # 下部タブエリア
        analysis_frame = ttk.LabelFrame(parent, text="🔍 詳細分析")
        analysis_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # タブウィジェット
        self.analysis_notebook = ttk.Notebook(analysis_frame)
        self.analysis_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 技術詳細タブ
        self.tech_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.tech_frame, text="🔧 技術詳細")
        
        self.tech_text = scrolledtext.ScrolledText(self.tech_frame, wrap=tk.WORD, height=8, font=('Arial', 9))
        self.tech_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 主要発見タブ
        self.findings_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.findings_frame, text="💡 主要発見")
        
        self.findings_text = scrolledtext.ScrolledText(self.findings_frame, wrap=tk.WORD, height=8, font=('Arial', 9))
        self.findings_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 応用・制限タブ
        self.applications_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.applications_frame, text="🎯 応用・制限")
        
        self.applications_text = scrolledtext.ScrolledText(self.applications_frame, wrap=tk.WORD, height=8, font=('Arial', 9))
        self.applications_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # メタデータタブ
        self.metadata_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(self.metadata_frame, text="📊 メタデータ")
        
        self.metadata_text = scrolledtext.ScrolledText(self.metadata_frame, wrap=tk.WORD, height=8, font=('Consolas', 9))
        self.metadata_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_structure_area(self, parent):
        """構造解析エリア"""
        # 右側フレーム（構造解析）
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        structure_frame = ttk.LabelFrame(right_frame, text="🏗️ 論文構造解析")
        structure_frame.pack(fill=tk.BOTH, expand=True)
        
        # 構造情報ツリー
        tree_frame = ttk.Frame(structure_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ツリービュー
        self.structure_tree = ttk.Treeview(tree_frame, show='tree headings', height=25)
        self.structure_tree['columns'] = ('value',)
        self.structure_tree.heading('#0', text='項目')
        self.structure_tree.heading('value', text='詳細')
        self.structure_tree.column('#0', width=150)
        self.structure_tree.column('value', width=200)
        
        # スクロールバー
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.structure_tree.yview)
        self.structure_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.structure_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def browse_file(self):
        """ファイル選択ダイアログ"""
        file_path = filedialog.askopenfilename(
            title="学術論文・技術文書を選択",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.current_file = Path(file_path)
            self.status_var.set(f"選択されたファイル: {self.current_file.name}")
            
    def start_processing(self):
        """論文処理開始"""
        if not self.current_file or not self.current_file.exists():
            messagebox.showerror("エラー", "有効なファイルを選択してください")
            return
            
        if self.processing_thread and self.processing_thread.is_alive():
            messagebox.showwarning("警告", "処理が実行中です")
            return
        
        # ボタン無効化
        self.process_button.config(state='disabled')
        
        # プログレスバー開始
        self.progress_var.set(0)
        self.status_var.set("論文解析中...")
        
        # 処理スレッド開始
        self.processing_thread = threading.Thread(target=self.process_document)
        self.processing_thread.start()
        
    def process_document(self):
        """文書処理（バックグラウンド）"""
        try:
            # プログレス更新
            self.root.after(0, lambda: self.progress_var.set(10))
            self.root.after(0, lambda: self.status_var.set("テキスト抽出中..."))
            
            # 詳細レベルに応じてmax_length調整
            level_mapping = {
                "brief": 100,
                "standard": 200,
                "detailed": 400,
                "comprehensive": 800
            }
            max_length = level_mapping.get(self.detail_level_var.get(), 200)
            
            # プログレス更新
            self.root.after(0, lambda: self.progress_var.set(30))
            self.root.after(0, lambda: self.status_var.set("論文構造解析中..."))
            
            # 論文処理実行
            result = self.processor.generate_academic_summary(
                self.current_file, 
                language="ja",
                max_length=max_length
            )
            
            # プログレス更新
            self.root.after(0, lambda: self.progress_var.set(80))
            self.root.after(0, lambda: self.status_var.set("結果表示中..."))
            
            # 結果表示
            self.root.after(0, lambda: self.display_results(result))
            
            # 完了
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_var.set("処理完了"))
            
        except Exception as e:
            error_msg = f"処理エラー: {str(e)}"
            self.root.after(0, lambda: self.status_var.set(error_msg))
            self.root.after(0, lambda: messagebox.showerror("エラー", error_msg))
        finally:
            # ボタン有効化
            self.root.after(0, lambda: self.process_button.config(state='normal'))
            
    def display_results(self, result: Dict[str, Any]):
        """結果表示"""
        # 要約表示
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, result.get("summary", "要約生成に失敗しました"))
        
        # 技術詳細表示
        self.tech_text.delete(1.0, tk.END)
        if result.get("technical_analysis"):
            tech_analysis = result["technical_analysis"]
            
            tech_content = []
            tech_content.append(f"【技術レベル】\n{tech_analysis.technical_level}")
            tech_content.append(f"【文書タイプ】\n{tech_analysis.document_type}")
            
            if tech_analysis.technical_details:
                details_str = "\n".join([f"• {detail}" for detail in tech_analysis.technical_details])
                tech_content.append(f"【技術詳細】\n{details_str}")
                
            if tech_analysis.mathematical_concepts:
                concepts_str = "、".join(tech_analysis.mathematical_concepts)
                tech_content.append(f"【数学的概念】\n{concepts_str}")
            
            self.tech_text.insert(tk.END, "\n\n".join(tech_content))
        
        # 主要発見表示
        self.findings_text.delete(1.0, tk.END)
        if result.get("technical_analysis"):
            findings_content = []
            
            if tech_analysis.key_findings:
                findings_str = "\n".join([f"• {finding}" for finding in tech_analysis.key_findings])
                findings_content.append(f"【主要発見】\n{findings_str}")
            
            if tech_analysis.main_contribution:
                findings_content.append(f"【主要貢献】\n{tech_analysis.main_contribution}")
                
            if tech_analysis.methodology_summary:
                findings_content.append(f"【手法要約】\n{tech_analysis.methodology_summary}")
            
            self.findings_text.insert(tk.END, "\n\n".join(findings_content))
        
        # 応用・制限表示  
        self.applications_text.delete(1.0, tk.END)
        if result.get("technical_analysis"):
            app_content = []
            
            if tech_analysis.practical_applications:
                apps_str = "\n".join([f"• {app}" for app in tech_analysis.practical_applications])
                app_content.append(f"【実用的応用】\n{apps_str}")
            
            if tech_analysis.limitations:
                limits_str = "\n".join([f"• {limit}" for limit in tech_analysis.limitations])
                app_content.append(f"【制限事項】\n{limits_str}")
                
            if tech_analysis.future_work:
                app_content.append(f"【今後の課題】\n{tech_analysis.future_work}")
            
            self.applications_text.insert(tk.END, "\n\n".join(app_content))
        
        # メタデータ表示
        self.metadata_text.delete(1.0, tk.END)
        if result.get("processing_metadata"):
            metadata_json = json.dumps(result["processing_metadata"], indent=2, ensure_ascii=False)
            self.metadata_text.insert(tk.END, metadata_json)
        
        # 構造ツリー表示
        self.display_structure_tree(result.get("structure"))
        
    def display_structure_tree(self, structure):
        """構造ツリー表示"""
        # ツリークリア
        for item in self.structure_tree.get_children():
            self.structure_tree.delete(item)
        
        if not structure:
            return
            
        # 基本情報
        basic_info = self.structure_tree.insert('', 'end', text='基本情報', values=('',))
        
        if structure.title:
            self.structure_tree.insert(basic_info, 'end', text='タイトル', values=(structure.title[:50] + "..." if len(structure.title) > 50 else structure.title,))
        
        if structure.authors:
            authors_str = "、".join(structure.authors[:3])
            if len(structure.authors) > 3:
                authors_str += f" 他{len(structure.authors)-3}名"
            self.structure_tree.insert(basic_info, 'end', text='著者', values=(authors_str,))
        
        # セクション情報
        sections = self.structure_tree.insert('', 'end', text='セクション', values=('',))
        
        section_counts = 0
        for section_name in ['abstract', 'introduction', 'methodology', 'results', 'discussion', 'conclusion']:
            section_content = getattr(structure, section_name, None)
            if section_content:
                section_counts += 1
                section_ja = {
                    'abstract': 'アブストラクト',
                    'introduction': 'はじめに', 
                    'methodology': '手法',
                    'results': '結果',
                    'discussion': '考察',
                    'conclusion': '結論'
                }
                self.structure_tree.insert(sections, 'end', text=section_ja.get(section_name, section_name), 
                                         values=(f"{len(section_content)}文字",))
        
        # 図表・数式
        figures_tables = self.structure_tree.insert('', 'end', text='図表・数式', values=('',))
        
        if structure.figures:
            self.structure_tree.insert(figures_tables, 'end', text='図', values=(f"{len(structure.figures)}個",))
        
        if structure.tables:
            self.structure_tree.insert(figures_tables, 'end', text='表', values=(f"{len(structure.tables)}個",))
            
        if structure.equations:
            self.structure_tree.insert(figures_tables, 'end', text='数式', values=(f"{len(structure.equations)}個",))
        
        if structure.references:
            self.structure_tree.insert('', 'end', text='参考文献', values=(f"{len(structure.references)}件",))
        
        # ツリー展開
        for item in self.structure_tree.get_children():
            self.structure_tree.item(item, open=True)
            
    def copy_summary(self):
        """要約をクリップボードにコピー"""
        summary_content = self.summary_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(summary_content)
        messagebox.showinfo("完了", "要約をクリップボードにコピーしました")
        
    def save_summary(self):
        """要約を保存"""
        if not self.current_file:
            messagebox.showerror("エラー", "処理されたファイルがありません")
            return
            
        save_path = filedialog.asksaveasfilename(
            title="要約を保存",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ],
            initialname=f"{self.current_file.stem}_academic_summary"
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(self.summary_text.get(1.0, tk.END))
                messagebox.showinfo("完了", f"要約を保存しました: {save_path}")
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {str(e)}")
                
    def reprocess(self):
        """再処理"""
        if self.current_file:
            self.start_processing()

def main():
    """メイン関数"""
    root = tk.Tk()
    app = AcademicGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
