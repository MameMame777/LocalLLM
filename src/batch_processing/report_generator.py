#!/usr/bin/env python3
"""
Batch Processing System for LocalLLM
Step 5: Report Generator - Comprehensive processing reports
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import csv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from batch_processing.file_scanner import FileInfo
from batch_processing.task_manager import TaskResult
from batch_processing.error_handler import ProcessingError


@dataclass
class BatchReport:
    """Comprehensive batch processing report."""
    # Session info
    session_id: str
    start_time: datetime
    end_time: datetime
    total_duration: str
    
    # File statistics
    total_files: int
    processed_files: int
    failed_files_count: int
    skipped_files: int
    success_rate: float
    
    # Size statistics
    total_size_mb: float
    processed_size_mb: float
    avg_file_size_mb: float
    
    # Performance metrics
    avg_processing_time: float
    processing_speed_files_per_min: float
    processing_speed_mb_per_min: float
    parallelization_efficiency: float
    
    # File details
    successful_files: List[Dict[str, Any]]
    failed_files: List[Dict[str, Any]]
    
    # Error summary
    error_summary: Dict[str, Any]


class ReportGenerator:
    """
    Advanced report generator for batch processing results.
    Generates comprehensive reports in multiple formats.
    """
    
    def __init__(self, output_directory: Path = Path("output/reports")):
        """
        Initialize report generator.
        
        Args:
            output_directory: Directory to save reports
        """
        self.output_directory = output_directory
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Report templates
        self.html_template = self._get_html_template()
    
    def generate_report(
        self,
        session_id: str,
        start_time: datetime,
        end_time: datetime,
        task_results: List[TaskResult],
        error_handler: Optional[Any] = None,
        file_infos: Optional[List[FileInfo]] = None
    ) -> BatchReport:
        """
        Generate comprehensive batch processing report.
        
        Args:
            session_id: Unique session identifier
            start_time: Processing start time
            end_time: Processing end time
            task_results: List of task results
            error_handler: Error handler with error details
            file_infos: Original file information
            
        Returns:
            Comprehensive batch report
        """
        # Calculate basic statistics
        total_files = len(task_results)
        successful_results = [r for r in task_results if r.success]
        failed_results = [r for r in task_results if not r.success]
        
        processed_files = len(successful_results)
        failed_files = len(failed_results)
        success_rate = (processed_files / total_files * 100) if total_files > 0 else 0
        
        # Size statistics
        total_size_mb = sum(r.file_size_mb for r in task_results)
        processed_size_mb = sum(r.file_size_mb for r in successful_results)
        avg_file_size_mb = total_size_mb / total_files if total_files > 0 else 0
        
        # Performance metrics
        total_duration = end_time - start_time
        total_processing_time = sum(r.processing_time for r in task_results)
        avg_processing_time = total_processing_time / total_files if total_files > 0 else 0
        
        files_per_min = processed_files / (total_duration.total_seconds() / 60) if total_duration.total_seconds() > 0 else 0
        mb_per_min = processed_size_mb / (total_duration.total_seconds() / 60) if total_duration.total_seconds() > 0 else 0
        
        # Parallelization efficiency (theoretical vs actual)
        parallelization_efficiency = 0
        if total_processing_time > 0:
            parallelization_efficiency = (total_duration.total_seconds() / total_processing_time) * 100
        
        # File details
        successful_files = [
            {
                "filename": r.file_path.name,
                "size_mb": r.file_size_mb,
                "processing_time": r.processing_time,
                "result_summary": str(r.result_data)[:100] + "..." if r.result_data else ""
            }
            for r in successful_results
        ]
        
        failed_files_list = [
            {
                "filename": r.file_path.name,
                "size_mb": r.file_size_mb,
                "error_message": r.error_message,
                "processing_time": r.processing_time
            }
            for r in failed_results
        ]
        
        # Error summary
        error_summary = {"total_errors": 0, "error_types": {}}
        if error_handler:
            error_summary = error_handler.get_error_summary()
        
        # Create comprehensive report
        report = BatchReport(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            total_duration=str(total_duration),
            total_files=total_files,
            processed_files=processed_files,
            failed_files_count=failed_files,
            skipped_files=0,  # TODO: Add skipped file tracking
            success_rate=success_rate,
            total_size_mb=total_size_mb,
            processed_size_mb=processed_size_mb,
            avg_file_size_mb=avg_file_size_mb,
            avg_processing_time=avg_processing_time,
            processing_speed_files_per_min=files_per_min,
            processing_speed_mb_per_min=mb_per_min,
            parallelization_efficiency=parallelization_efficiency,
            successful_files=successful_files,
            failed_files=failed_files_list,
            error_summary=error_summary
        )
        
        return report
    
    def save_report_json(self, report: BatchReport, filename: Optional[str] = None) -> Path:
        """Save report as JSON file."""
        if not filename:
            timestamp = report.start_time.strftime("%Y%m%d_%H%M%S")
            filename = f"batch_report_{timestamp}.json"
        
        filepath = self.output_directory / filename
        
        # Convert datetime objects to strings for JSON serialization
        report_dict = asdict(report)
        report_dict['start_time'] = report.start_time.isoformat()
        report_dict['end_time'] = report.end_time.isoformat()
        
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def save_report_csv(self, report: BatchReport, filename: Optional[str] = None) -> Path:
        """Save detailed file results as CSV."""
        if not filename:
            timestamp = report.start_time.strftime("%Y%m%d_%H%M%S")
            filename = f"batch_results_{timestamp}.csv"
        
        filepath = self.output_directory / filename
        
        # Combine successful and failed files
        all_files = []
        
        # Add successful files
        for file_data in report.successful_files:
            all_files.append({
                "filename": file_data["filename"],
                "status": "SUCCESS",
                "size_mb": file_data["size_mb"],
                "processing_time": file_data["processing_time"],
                "error_message": "",
                "result_summary": file_data.get("result_summary", "")
            })
        
        # Add failed files
        for file_data in report.failed_files:
            all_files.append({
                "filename": file_data["filename"],
                "status": "FAILED",
                "size_mb": file_data["size_mb"],
                "processing_time": file_data["processing_time"],
                "error_message": file_data["error_message"],
                "result_summary": ""
            })
        
        # Write CSV
        if all_files:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_files[0].keys())
                writer.writeheader()
                writer.writerows(all_files)
        
        return filepath
    
    def save_report_html(self, report: BatchReport, filename: Optional[str] = None) -> Path:
        """Save report as HTML file."""
        if not filename:
            timestamp = report.start_time.strftime("%Y%m%d_%H%M%S")
            filename = f"batch_report_{timestamp}.html"
        
        filepath = self.output_directory / filename
        
        # Generate HTML content
        html_content = self._generate_html_report(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def save_report_markdown(self, report: BatchReport, filename: Optional[str] = None) -> Path:
        """Save report as Markdown file."""
        if not filename:
            timestamp = report.start_time.strftime("%Y%m%d_%H%M%S")
            filename = f"batch_report_{timestamp}.md"
        
        filepath = self.output_directory / filename
        
        # Generate Markdown content
        md_content = self._generate_markdown_report(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filepath
    
    def print_summary_report(self, report: BatchReport) -> None:
        """Print a concise summary report to console."""
        print("\n" + "="*80)
        print("📊 BATCH PROCESSING SUMMARY REPORT")
        print("="*80)
        
        print(f"🆔 Session: {report.session_id}")
        print(f"⏰ Duration: {report.total_duration}")
        print(f"📅 Completed: {report.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📈 PROCESSING STATISTICS")
        print(f"   📁 Total Files: {report.total_files}")
        print(f"   ✅ Successful: {report.processed_files}")
        print(f"   ❌ Failed: {report.failed_files_count}")
        print(f"   📊 Success Rate: {report.success_rate:.1f}%")
        
        print(f"\n💾 SIZE STATISTICS")
        print(f"   📂 Total Size: {report.total_size_mb:.2f} MB")
        print(f"   ✅ Processed: {report.processed_size_mb:.2f} MB")
        print(f"   📄 Avg File Size: {report.avg_file_size_mb:.2f} MB")
        
        print(f"\n⚡ PERFORMANCE METRICS")
        print(f"   ⏱️ Avg Time/File: {report.avg_processing_time:.2f}s")
        print(f"   🚀 Speed: {report.processing_speed_files_per_min:.1f} files/min")
        print(f"   💨 Throughput: {report.processing_speed_mb_per_min:.1f} MB/min")
        print(f"   🔧 Parallel Efficiency: {report.parallelization_efficiency:.1f}%")
        
        if report.error_summary.get("total_errors", 0) > 0:
            print(f"\n⚠️ ERROR SUMMARY")
            print(f"   Total Errors: {report.error_summary['total_errors']}")
            for error_type, count in report.error_summary.get("errors_by_type", {}).items():
                print(f"   • {error_type}: {count}")
        
        print("="*80)
    
    def _generate_html_report(self, report: BatchReport) -> str:
        """Generate HTML report content."""
        # This is a simplified HTML template
        # In a real implementation, you might use a template engine like Jinja2
        
        successful_files_html = ""
        for file_data in report.successful_files:
            successful_files_html += f"""
            <tr>
                <td>{file_data['filename']}</td>
                <td>{file_data['size_mb']:.2f} MB</td>
                <td>{file_data['processing_time']:.2f}s</td>
                <td>✅ Success</td>
            </tr>
            """
        
        failed_files_html = ""
        for file_data in report.failed_files:
            failed_files_html += f"""
            <tr>
                <td>{file_data['filename']}</td>
                <td>{file_data['size_mb']:.2f} MB</td>
                <td>{file_data['processing_time']:.2f}s</td>
                <td>❌ {file_data['error_message']}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Batch Processing Report - {report.session_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat-box {{ background: #e8f4f8; padding: 15px; border-radius: 5px; flex: 1; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Batch Processing Report</h1>
                <p><strong>Session:</strong> {report.session_id}</p>
                <p><strong>Duration:</strong> {report.total_duration}</p>
                <p><strong>Completed:</strong> {report.end_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <h3>📁 Files</h3>
                    <p>Total: {report.total_files}</p>
                    <p>Success: {report.processed_files}</p>
                    <p>Failed: {report.failed_files_count}</p>
                    <p>Rate: {report.success_rate:.1f}%</p>
                </div>
                <div class="stat-box">
                    <h3>💾 Size</h3>
                    <p>Total: {report.total_size_mb:.2f} MB</p>
                    <p>Processed: {report.processed_size_mb:.2f} MB</p>
                    <p>Avg: {report.avg_file_size_mb:.2f} MB</p>
                </div>
                <div class="stat-box">
                    <h3>⚡ Performance</h3>
                    <p>Avg Time: {report.avg_processing_time:.2f}s</p>
                    <p>Speed: {report.processing_speed_files_per_min:.1f} files/min</p>
                    <p>Efficiency: {report.parallelization_efficiency:.1f}%</p>
                </div>
            </div>
            
            <h2>📋 File Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Filename</th>
                        <th>Size</th>
                        <th>Processing Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {successful_files_html}
                    {failed_files_html}
                </tbody>
            </table>
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_report(self, report: BatchReport) -> str:
        """Generate Markdown report content."""
        md = f"""# 📊 Batch Processing Report

## Session Information
- **Session ID**: {report.session_id}
- **Duration**: {report.total_duration}
- **Completed**: {report.end_time.strftime('%Y-%m-%d %H:%M:%S')}

## 📈 Processing Statistics
| Metric | Value |
|--------|--------|
| Total Files | {report.total_files} |
| Successful | {report.processed_files} |
| Failed | {report.failed_files_count} |
| Success Rate | {report.success_rate:.1f}% |

## 💾 Size Statistics
| Metric | Value |
|--------|--------|
| Total Size | {report.total_size_mb:.2f} MB |
| Processed Size | {report.processed_size_mb:.2f} MB |
| Average File Size | {report.avg_file_size_mb:.2f} MB |

## ⚡ Performance Metrics
| Metric | Value |
|--------|--------|
| Avg Processing Time | {report.avg_processing_time:.2f}s |
| Processing Speed | {report.processing_speed_files_per_min:.1f} files/min |
| Throughput | {report.processing_speed_mb_per_min:.1f} MB/min |
| Parallelization Efficiency | {report.parallelization_efficiency:.1f}% |

## 📋 File Results

### ✅ Successful Files ({len(report.successful_files)})
| Filename | Size (MB) | Time (s) |
|----------|-----------|----------|
"""
        
        for file_data in report.successful_files:
            md += f"| {file_data['filename']} | {file_data['size_mb']:.2f} | {file_data['processing_time']:.2f} |\n"
        
        if report.failed_files:
            md += f"""
### ❌ Failed Files ({len(report.failed_files)})
| Filename | Size (MB) | Time (s) | Error |
|----------|-----------|----------|-------|
"""
            for file_data in report.failed_files:
                md += f"| {file_data['filename']} | {file_data['size_mb']:.2f} | {file_data['processing_time']:.2f} | {file_data['error_message']} |\n"
        
        if report.error_summary.get("total_errors", 0) > 0:
            md += f"""
## ⚠️ Error Summary
- **Total Errors**: {report.error_summary['total_errors']}

### Error Types
"""
            for error_type, count in report.error_summary.get("errors_by_type", {}).items():
                md += f"- **{error_type}**: {count}\n"
        
        return md
    
    def _get_html_template(self) -> str:
        """Get HTML template for reports."""
        # This would normally be loaded from a template file
        return ""


def test_report_generator():
    """Test the report generator functionality."""
    print("🧪 Testing Report Generator")
    print("=" * 60)
    
    # Create mock data
    from batch_processing.task_manager import TaskResult
    
    start_time = datetime.now()
    
    # Create mock task results
    task_results = [
        TaskResult(1, Path("file1.pdf"), True, "Summary of file1", processing_time=1.5, file_size_mb=2.1),
        TaskResult(2, Path("file2.txt"), True, "Summary of file2", processing_time=0.8, file_size_mb=0.5),
        TaskResult(3, Path("file3.pdf"), False, error_message="Parsing error", processing_time=2.0, file_size_mb=3.2),
        TaskResult(4, Path("file4.html"), True, "Summary of file4", processing_time=1.2, file_size_mb=1.1),
    ]
    
    end_time = datetime.now()
    
    # Initialize report generator
    generator = ReportGenerator()
    
    # Generate report
    session_id = f"test_session_{int(start_time.timestamp())}"
    report = generator.generate_report(
        session_id=session_id,
        start_time=start_time,
        end_time=end_time,
        task_results=task_results
    )
    
    # Print summary
    generator.print_summary_report(report)
    
    # Save in different formats
    try:
        json_path = generator.save_report_json(report)
        print(f"📄 JSON report saved: {json_path}")
        
        csv_path = generator.save_report_csv(report)
        print(f"📊 CSV report saved: {csv_path}")
        
        html_path = generator.save_report_html(report)
        print(f"🌐 HTML report saved: {html_path}")
        
        md_path = generator.save_report_markdown(report)
        print(f"📝 Markdown report saved: {md_path}")
        
        print("\n✅ Report Generator Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_report_generator()
