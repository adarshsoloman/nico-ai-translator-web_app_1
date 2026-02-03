#!/usr/bin/env python3
"""
Benchmark Results Analysis Script
==================================

Analyzes benchmark results and generates comparison charts and reports.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path
from datetime import datetime


class BenchmarkAnalyzer:
    """Analyze and visualize benchmark results"""
    
    def __init__(self, results_file: str):
        """
        Initialize analyzer with results file
        
        Args:
            results_file: Path to benchmark_results_*.json file
        """
        self.results_file = results_file
        self.results = self.load_results()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
    def load_results(self) -> list:
        """Load results from JSON file"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_summary_df(self) -> pd.DataFrame:
        """Create summary DataFrame from results"""
        summary_data = []
        for result in self.results:
            summary_data.append({
                "Model": result['model'],
                "Direction": result['direction'],
                "Avg Time (ms)": result['avg_time_ms'],
                "Throughput (s/s)": result['throughput_sps'],
                "GPU Memory (MB)": result['gpu_memory_mb'],
                "RAM (GB)": result['ram_gb'],
                "Load Time (s)": result['load_time_s'],
                "BLEU": result.get('bleu_score', 0),
                "COMET": result.get('comet_score', 0)
            })
        return pd.DataFrame(summary_data)
    
    def plot_speed_comparison(self):
        """Create speed comparison chart"""
        df = self.create_summary_df()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Average time comparison
        pivot_time = df.pivot(index='Direction', columns='Model', values='Avg Time (ms)')
        pivot_time.plot(kind='bar', ax=ax1, color=['#3498db', '#e74c3c', '#2ecc71'])
        ax1.set_title('Average Translation Time Comparison', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Translation Direction', fontsize=12)
        ax1.set_ylabel('Time (milliseconds)', fontsize=12)
        ax1.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(axis='y', alpha=0.3)
        
        # Throughput comparison
        pivot_throughput = df.pivot(index='Direction', columns='Model', values='Throughput (s/s)')
        pivot_throughput.plot(kind='bar', ax=ax2, color=['#3498db', '#e74c3c', '#2ecc71'])
        ax2.set_title('Throughput Comparison', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Translation Direction', fontsize=12)
        ax2.set_ylabel('Sentences per Second', fontsize=12)
        ax2.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        filename = f"speed_comparison_{self.timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {filename}")
        plt.close()
    
    def plot_memory_comparison(self):
        """Create memory usage comparison chart"""
        df = self.create_summary_df()
        
        # Get unique models and their memory usage
        model_memory = df.groupby('Model').first()[['GPU Memory (MB)', 'RAM (GB)']]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # GPU Memory
        model_memory['GPU Memory (MB)'].plot(
            kind='bar', 
            ax=ax1, 
            color=['#3498db', '#e74c3c', '#2ecc71']
        )
        ax1.set_title('GPU Memory Usage', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Model', fontsize=12)
        ax1.set_ylabel('VRAM (MB)', fontsize=12)
        ax1.grid(axis='y', alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for i, v in enumerate(model_memory['GPU Memory (MB)']):
            ax1.text(i, v + 50, f'{v:.0f} MB', ha='center', va='bottom', fontweight='bold')
        
        # RAM Usage
        model_memory['RAM (GB)'].plot(
            kind='bar', 
            ax=ax2, 
            color=['#3498db', '#e74c3c', '#2ecc71']
        )
        ax2.set_title('RAM Usage', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Model', fontsize=12)
        ax2.set_ylabel('RAM (GB)', fontsize=12)
        ax2.grid(axis='y', alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for i, v in enumerate(model_memory['RAM (GB)']):
            ax2.text(i, v + 0.1, f'{v:.2f} GB', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        filename = f"memory_comparison_{self.timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {filename}")
        plt.close()
    
    def plot_quality_comparison(self):
        """Create quality metrics comparison chart"""
        df = self.create_summary_df()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # BLEU Score comparison
        pivot_bleu = df.pivot(index='Direction', columns='Model', values='BLEU')
        pivot_bleu.plot(kind='bar', ax=ax1, color=['#3498db', '#e74c3c', '#2ecc71'])
        ax1.set_title('BLEU Score Comparison', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Translation Direction', fontsize=12)
        ax1.set_ylabel('BLEU Score (higher is better)', fontsize=12)
        ax1.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_ylim(0, 100)
        
        # Add value labels on bars
        for container in ax1.containers:
            ax1.bar_label(container, fmt='%.1f', padding=3)
        
        # COMET Score comparison
        pivot_comet = df.pivot(index='Direction', columns='Model', values='COMET')
        pivot_comet.plot(kind='bar', ax=ax2, color=['#3498db', '#e74c3c', '#2ecc71'])
        ax2.set_title('COMET Score Comparison', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Translation Direction', fontsize=12)
        ax2.set_ylabel('COMET Score (higher is better)', fontsize=12)
        ax2.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(axis='y', alpha=0.3)
        ax2.set_ylim(0, 1.0)
        
        # Add value labels on bars
        for container in ax2.containers:
            ax2.bar_label(container, fmt='%.3f', padding=3)
        
        plt.tight_layout()
        filename = f"quality_comparison_{self.timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {filename}")
        plt.close()
    
    def plot_overall_comparison(self):
        """Create comprehensive comparison chart"""
        df = self.create_summary_df()
        
        # Calculate average metrics across both directions
        avg_metrics = df.groupby('Model').agg({
            'Avg Time (ms)': 'mean',
            'Throughput (s/s)': 'mean',
            'GPU Memory (MB)': 'first',
            'Load Time (s)': 'first'
        }).reset_index()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        models = avg_metrics['Model']
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        
        # Average Time
        ax1.bar(models, avg_metrics['Avg Time (ms)'], color=colors)
        ax1.set_title('Average Translation Time', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Time (ms)', fontsize=10)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y', alpha=0.3)
        for i, v in enumerate(avg_metrics['Avg Time (ms)']):
            ax1.text(i, v + 5, f'{v:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Throughput
        ax2.bar(models, avg_metrics['Throughput (s/s)'], color=colors)
        ax2.set_title('Throughput', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Sentences/sec', fontsize=10)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(axis='y', alpha=0.3)
        for i, v in enumerate(avg_metrics['Throughput (s/s)']):
            ax2.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # GPU Memory
        ax3.bar(models, avg_metrics['GPU Memory (MB)'], color=colors)
        ax3.set_title('GPU Memory Usage', fontsize=12, fontweight='bold')
        ax3.set_ylabel('VRAM (MB)', fontsize=10)
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(axis='y', alpha=0.3)
        for i, v in enumerate(avg_metrics['GPU Memory (MB)']):
            ax3.text(i, v + 30, f'{v:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Load Time
        ax4.bar(models, avg_metrics['Load Time (s)'], color=colors)
        ax4.set_title('Model Load Time', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Time (seconds)', fontsize=10)
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(axis='y', alpha=0.3)
        for i, v in enumerate(avg_metrics['Load Time (s)']):
            ax4.text(i, v + 0.5, f'{v:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.suptitle('NLLB Model Benchmark - Overall Comparison', 
                     fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        filename = f"overall_comparison_{self.timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {filename}")
        plt.close()
    
    def generate_text_report(self):
        """Generate detailed text report"""
        df = self.create_summary_df()
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("NLLB MODEL BENCHMARK ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Source: {self.results_file}")
        report_lines.append("=" * 80)
        
        # Summary table
        report_lines.append("\n📊 SUMMARY TABLE")
        report_lines.append("-" * 80)
        report_lines.append(df.to_string(index=False))
        
        # Performance analysis
        report_lines.append("\n\n⚡ PERFORMANCE ANALYSIS")
        report_lines.append("-" * 80)
        
        avg_by_model = df.groupby('Model').agg({
            'Avg Time (ms)': 'mean',
            'Throughput (s/s)': 'mean'
        })
        
        fastest_model = avg_by_model['Avg Time (ms)'].idxmin()
        slowest_model = avg_by_model['Avg Time (ms)'].idxmax()
        
        report_lines.append(f"Fastest Model: {fastest_model}")
        report_lines.append(f"  → Avg Time: {avg_by_model.loc[fastest_model, 'Avg Time (ms)']:.2f} ms")
        report_lines.append(f"  → Throughput: {avg_by_model.loc[fastest_model, 'Throughput (s/s)']:.2f} s/s")
        report_lines.append(f"\nSlowest Model: {slowest_model}")
        report_lines.append(f"  → Avg Time: {avg_by_model.loc[slowest_model, 'Avg Time (ms)']:.2f} ms")
        report_lines.append(f"  → Throughput: {avg_by_model.loc[slowest_model, 'Throughput (s/s)']:.2f} s/s")
        
        # Memory analysis
        report_lines.append("\n\n💾 MEMORY ANALYSIS")
        report_lines.append("-" * 80)
        
        memory_by_model = df.groupby('Model').first()[['GPU Memory (MB)', 'RAM (GB)']]
        
        for model in memory_by_model.index:
            report_lines.append(f"{model}:")
            report_lines.append(f"  → GPU Memory: {memory_by_model.loc[model, 'GPU Memory (MB)']:.0f} MB")
            report_lines.append(f"  → RAM: {memory_by_model.loc[model, 'RAM (GB)']:.2f} GB")
        
        # Quality analysis
        report_lines.append("\n\n🎨 QUALITY ANALYSIS")
        report_lines.append("-" * 80)
        
        quality_by_model = df.groupby('Model').agg({
            'BLEU': 'mean',
            'COMET': 'mean'
        })
        
        best_bleu_model = quality_by_model['BLEU'].idxmax()
        best_comet_model = quality_by_model['COMET'].idxmax()
        
        for model in quality_by_model.index:
            report_lines.append(f"{model}:")
            report_lines.append(f"  → BLEU Score: {quality_by_model.loc[model, 'BLEU']:.2f}")
            report_lines.append(f"  → COMET Score: {quality_by_model.loc[model, 'COMET']:.4f}")
        
        report_lines.append(f"\nBest BLEU Score: {best_bleu_model} ({quality_by_model.loc[best_bleu_model, 'BLEU']:.2f})")
        report_lines.append(f"Best COMET Score: {best_comet_model} ({quality_by_model.loc[best_comet_model, 'COMET']:.4f})")
        
        # Recommendations
        report_lines.append("\n\n🎯 RECOMMENDATIONS")
        report_lines.append("-" * 80)
        report_lines.append("Based on the benchmark results:\n")
        report_lines.append("1. For BEST SPEED → Choose INT4 Quantized")
        report_lines.append("2. For BEST QUALITY → Choose model with highest COMET score")
        report_lines.append("3. For BALANCED (Speed + Quality) → Choose INT8 Quantized")
        report_lines.append("4. For LOWEST MEMORY → Choose INT4 Quantized")
        report_lines.append("\n💡 Quality Impact Analysis:")
        
        # Calculate quality degradation
        base_bleu = quality_by_model.loc['Base Model (Float16)', 'BLEU'] if 'Base Model (Float16)' in quality_by_model.index else 0
        for model in quality_by_model.index:
            if model != 'Base Model (Float16)' and base_bleu > 0:
                bleu_diff = quality_by_model.loc[model, 'BLEU'] - base_bleu
                report_lines.append(f"   {model}: {bleu_diff:+.2f} BLEU points vs Base")
        
        # Next steps
        report_lines.append("\n\n📋 NEXT STEPS")
        report_lines.append("-" * 80)
        report_lines.append("1. Review sample translations in the JSON file")
        report_lines.append("2. Assess quality vs. speed trade-offs")
        report_lines.append("3. Choose the optimal model for your use case")
        report_lines.append("4. Proceed with QLoRA training on the chosen model")
        report_lines.append("5. Integrate quantized model + LoRA adapters into web app")
        
        report_lines.append("\n" + "=" * 80)
        
        # Save report
        filename = f"analysis_report_{self.timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"✓ Saved: {filename}")
        
        # Also print to console
        print("\n" + '\n'.join(report_lines))
    
    def run_analysis(self):
        """Run complete analysis"""
        print("\n🔍 Analyzing benchmark results...\n")
        
        print("Generating visualizations...")
        self.plot_speed_comparison()
        self.plot_memory_comparison()
        self.plot_quality_comparison()
        self.plot_overall_comparison()
        
        print("\nGenerating text report...")
        self.generate_text_report()
        
        print("\n✅ Analysis complete!")
        print("\n📁 Generated files:")
        print(f"   - speed_comparison_{self.timestamp}.png")
        print(f"   - memory_comparison_{self.timestamp}.png")
        print(f"   - quality_comparison_{self.timestamp}.png")
        print(f"   - overall_comparison_{self.timestamp}.png")
        print(f"   - analysis_report_{self.timestamp}.txt")


def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_results.py <benchmark_results_file.json>")
        print("\nExample:")
        print("  python analyze_results.py benchmark_results_20260131_123456.json")
        sys.exit(1)
    
    results_file = sys.argv[1]
    
    if not Path(results_file).exists():
        print(f"Error: File not found: {results_file}")
        sys.exit(1)
    
    analyzer = BenchmarkAnalyzer(results_file)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
