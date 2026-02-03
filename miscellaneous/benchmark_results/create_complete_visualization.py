import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 12)
plt.rcParams['font.size'] = 10

# Combined benchmark data with all models
data = {
    'Model': ['CT2-FP16', 'CT2-INT8', 'BnB-INT8', 'BnB-INT4'] * 2,
    'Direction': ['EN→HI']*4 + ['HI→EN']*4,
    'Avg_Time_ms': [139.16, 154.45, 800.13, 441.67, 120.91, 131.11, 683.14, 375.75],
    'Throughput': [7.19, 6.47, 1.25, 2.26, 8.27, 7.63, 1.46, 2.66],
    'BLEU': [27.59, 27.46, 27.50, 27.19, 35.97, 35.90, 35.91, 34.34],
    'COMET': [0.7816, 0.7818, 0.7821, 0.7770, 0.8770, 0.8771, 0.8771, 0.8737],
    'GPU_Mem_MB': [2090, 1204, 20973, 21559, 2090, 1204, 20973, 21559],
    'Load_Time_s': [3.69, 5.51, 21.53, 18.63, 3.69, 5.51, 21.53, 18.63]
}

df = pd.DataFrame(data)

# Create figure with subplots
fig = plt.figure(figsize=(20, 12))
fig.suptitle('NLLB Model Benchmark Results - Complete Comparison\nCTranslate2 FP16 Recommended for Production', 
             fontsize=18, fontweight='bold', y=0.98)

# Define colors for each model
colors = {
    'CT2-FP16': '#2ecc71',    # Green
    'CT2-INT8': '#3498db',    # Blue  
    'BnB-INT8': '#e74c3c',    # Red
    'BnB-INT4': '#f39c12'     # Orange
}

# 1. BLEU Score Comparison (Top Left)
ax1 = plt.subplot(3, 3, 1)
df_pivot = df.pivot(index='Direction', columns='Model', values='BLEU')
df_pivot = df_pivot[['CT2-FP16', 'CT2-INT8', 'BnB-INT8', 'BnB-INT4']]
x = np.arange(len(df_pivot.index))
width = 0.2
for i, model in enumerate(df_pivot.columns):
    bars = ax1.bar(x + i*width, df_pivot[model], width, label=model, 
                   color=colors[model], edgecolor='black', linewidth=1.5)
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
ax1.set_ylabel('BLEU Score', fontweight='bold', fontsize=11)
ax1.set_title('BLEU Score Comparison - All Models Excellent', fontweight='bold', fontsize=12)
ax1.set_xticks(x + width * 1.5)
ax1.set_xticklabels(df_pivot.index)
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(axis='y', alpha=0.3)

# 2. COMET Score Comparison (Top Right)
ax2 = plt.subplot(3, 3, 3)
df_pivot = df.pivot(index='Direction', columns='Model', values='COMET')
df_pivot = df_pivot[['CT2-FP16', 'CT2-INT8', 'BnB-INT8', 'BnB-INT4']]
x = np.arange(len(df_pivot.index))
for i, model in enumerate(df_pivot.columns):
    bars = ax2.bar(x + i*width, df_pivot[model], width, label=model,
                   color=colors[model], edgecolor='black', linewidth=1.5)
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
ax2.set_ylabel('COMET Score', fontweight='bold', fontsize=11)
ax2.set_title('COMET Score Comparison', fontweight='bold', fontsize=12)
ax2.set_xticks(x + width * 1.5)
ax2.set_xticklabels(df_pivot.index)
ax2.legend(loc='lower left', fontsize=9)
ax2.grid(axis='y', alpha=0.3)

# 3. Speed (Throughput) Comparison (Middle Left)
ax3 = plt.subplot(3, 3, 4)
df_pivot = df.pivot(index='Direction', columns='Model', values='Throughput')
df_pivot = df_pivot[['CT2-FP16', 'CT2-INT8', 'BnB-INT8', 'BnB-INT4']]
x = np.arange(len(df_pivot.index))
for i, model in enumerate(df_pivot.columns):
    bars = ax3.bar(x + i*width, df_pivot[model], width, label=model,
                   color=colors[model], edgecolor='black', linewidth=1.5)
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
ax3.set_ylabel('Throughput (sentences/sec)', fontweight='bold', fontsize=11)
ax3.set_title('Speed: CT2-FP16 is 5.7x Faster!', fontweight='bold', fontsize=12)
ax3.set_xticks(x + width * 1.5)
ax3.set_xticklabels(df_pivot.index)
ax3.legend(loc='upper left', fontsize=9)
ax3.grid(axis='y', alpha=0.3)

# 4. Translation Time Comparison (Middle Center)
ax4 = plt.subplot(3, 3, 5)
df_en = df[df['Direction'] == 'EN→HI']
bars = ax4.barh(df_en['Model'], df_en['Avg_Time_ms'], 
               color=[colors[m] for m in df_en['Model']], 
               edgecolor='black', linewidth=1.5)
for bar, val in zip(bars, df_en['Avg_Time_ms']):
    ax4.text(val + 20, bar.get_y() + bar.get_height()/2, 
             f'{val:.0f}ms', va='center', fontweight='bold', fontsize=10)
ax4.set_xlabel('Avg Translation Time (ms)', fontweight='bold', fontsize=11)
ax4.set_title('Translation Time: EN→HI - Lower is Better', fontweight='bold', fontsize=12)
ax4.grid(axis='x', alpha=0.3)
ax4.invert_yaxis()

# 5. GPU Memory Usage (Middle Right)
ax5 = plt.subplot(3, 3, 6)
df_en = df[df['Direction'] == 'EN→HI']
bars = ax5.bar(range(len(df_en)), df_en['GPU_Mem_MB']/1024, 
              color=[colors[m] for m in df_en['Model']],
              edgecolor='black', linewidth=1.5)
for bar, val in zip(bars, df_en['GPU_Mem_MB']/1024):
    ax5.text(bar.get_x() + bar.get_width()/2, val + 0.5,
             f'{val:.1f}GB', ha='center', fontweight='bold', fontsize=9)
ax5.set_ylabel('GPU Memory (GB)', fontweight='bold', fontsize=11)
ax5.set_title('Memory Usage - CT2 Models Win', fontweight='bold', fontsize=12)
ax5.set_xticks(range(len(df_en)))
ax5.set_xticklabels(df_en['Model'], rotation=0)
ax5.grid(axis='y', alpha=0.3)

# 6. Quality vs Speed Trade-off (Bottom Left, spans 2 columns)
ax6 = plt.subplot(3, 3, (7, 8))
for direction in ['EN→HI', 'HI→EN']:
    df_dir = df[df['Direction'] == direction]
    for _, row in df_dir.iterrows():
        ax6.scatter(row['Throughput'], row['COMET'], 
                   s=300, c=colors[row['Model']], 
                   marker='o' if direction == 'EN→HI' else 's',
                   edgecolors='black', linewidth=2, alpha=0.8,
                   label=f"{row['Model']} ({direction})" if direction == 'EN→HI' else "")
        # Annotate only EN→HI for clarity
        if direction == 'EN→HI':
            ax6.annotate(row['Model'].replace('CT2-', '').replace('BnB-', ''),
                        (row['Throughput'], row['COMET']),
                        xytext=(8, 8), textcoords='offset points',
                        fontsize=9, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.4', 
                                facecolor='white', alpha=0.7, edgecolor='black'))
ax6.set_xlabel('Speed (sentences/second)', fontweight='bold', fontsize=11)
ax6.set_ylabel('Quality (COMET Score)', fontweight='bold', fontsize=11)
ax6.set_title('Quality vs Speed Trade-off\n● = EN→HI  ■ = HI→EN', fontweight='bold', fontsize=12)
ax6.legend(loc='lower right', fontsize=8, ncol=2)
ax6.grid(alpha=0.3)

# 7. Speed Improvement Comparison (Bottom Right)
ax7 = plt.subplot(3, 3, 9)
# Calculate improvements vs BnB-INT8 (slowest baseline)
df_en = df[df['Direction'] == 'EN→HI'].copy()
baseline_throughput = df_en[df_en['Model'] == 'BnB-INT8']['Throughput'].values[0]
df_en['Improvement'] = ((df_en['Throughput'] / baseline_throughput) - 1) * 100
df_en = df_en.sort_values('Improvement', ascending=True)

bars = ax7.barh(df_en['Model'], df_en['Improvement'],
               color=[colors[m] for m in df_en['Model']],
               edgecolor='black', linewidth=1.5)
for bar, val in zip(bars, df_en['Improvement']):
    ax7.text(val + 10 if val > 0 else val - 10, 
             bar.get_y() + bar.get_height()/2,
             f'+{val:.0f}%' if val > 0 else f'{val:.0f}%',
             va='center', ha='left' if val > 0 else 'right',
             fontweight='bold', fontsize=10)
ax7.set_xlabel('Speed Improvement over BnB-INT8 (%)', fontweight='bold', fontsize=11)
ax7.set_title('Speed Improvement (EN→HI)\nCT2-FP16 is 475% Faster!', fontweight='bold', fontsize=12)
ax7.axvline(x=0, color='black', linestyle='--', linewidth=1.5)
ax7.grid(axis='x', alpha=0.3)

# 8. Key Findings Text Box (Top Middle)
ax8 = plt.subplot(3, 3, 2)
ax8.axis('off')
findings_text = """
KEY FINDINGS

✓ CT2-FP16: FASTEST (7-8 s/s)
   • 5.7x faster than BnB-INT8
   • 3.2x faster than BnB-INT4
   • Identical quality (COMET 0.88)

✓ CT2-INT8: BEST MEMORY
   • Only 1.2GB VRAM (42% savings)
   • Quality loss < 0.1%
   • Still 5x faster than BnB

⚠ BnB Models: NOT RECOMMENDED
   • 5-8x slower than CT2
   • 10x more GPU memory
   • No quality advantage

RECOMMENDATION:
Deploy CT2-FP16 for Production
"""
ax8.text(0.1, 0.95, findings_text, transform=ax8.transAxes,
        fontsize=11, verticalalignment='top', family='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8, 
                 edgecolor='black', linewidth=2))

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('nllb_benchmark_complete.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Complete benchmark visualization saved: nllb_benchmark_complete.png")
