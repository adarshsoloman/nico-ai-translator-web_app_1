import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 11

# Combined benchmark data
data = {
    'Model': ['CT2 FP16', 'CT2 INT8', 'BnB INT8', 'BnB INT4'] * 2,
    'Direction': ['EN→HI']*4 + ['HI→EN']*4,
    'Avg Time (ms)': [139.16, 154.45, 800.13, 441.67, 120.91, 131.11, 683.14, 375.75],
    'Throughput (s/s)': [7.19, 6.47, 1.25, 2.26, 8.27, 7.63, 1.46, 2.66],
    'BLEU': [27.59, 27.46, 27.50, 27.19, 35.97, 35.90, 35.91, 34.34],
    'COMET': [0.7816, 0.7818, 0.7821, 0.7770, 0.8770, 0.8771, 0.8771, 0.8737],
    'GPU Memory (MB)': [2090, 1204, 20973, 21559, 2090, 1204, 20973, 21559],
    'Load Time (s)': [3.69, 5.51, 21.53, 18.63, 3.69, 5.51, 21.53, 18.63]
}

df = pd.DataFrame(data)

# Create comprehensive visualization
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

colors = {'CT2 FP16': '#2ecc71', 'CT2 INT8': '#3498db', 'BnB INT8': '#e74c3c', 'BnB INT4': '#f39c12'}

# 1. Throughput Comparison
ax1 = fig.add_subplot(gs[0, :2])
df_en = df[df['Direction'] == 'EN→HI'].sort_values('Throughput (s/s)', ascending=False)
bars = ax1.barh(df_en['Model'], df_en['Throughput (s/s)'], 
                color=[colors[m] for m in df_en['Model']])
ax1.set_xlabel('Throughput (sentences/second)', fontweight='bold', fontsize=12)
ax1.set_title('Speed Comparison: EN→HI Translation', fontweight='bold', fontsize=14)
ax1.grid(axis='x', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, df_en['Throughput (s/s)'])):
    ax1.text(val + 0.2, bar.get_y() + bar.get_height()/2, 
             f'{val:.2f} s/s', va='center', fontweight='bold')

# 2. GPU Memory Comparison
ax2 = fig.add_subplot(gs[0, 2])
df_mem = df[df['Direction'] == 'EN→HI']
bars = ax2.bar(range(len(df_mem)), df_mem['GPU Memory (MB)'] / 1024,
               color=[colors[m] for m in df_mem['Model']])
ax2.set_ylabel('GPU Memory (GB)', fontweight='bold')
ax2.set_title('Memory Usage', fontweight='bold', fontsize=14)
ax2.set_xticks(range(len(df_mem)))
ax2.set_xticklabels(df_mem['Model'], rotation=45, ha='right')
ax2.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, df_mem['GPU Memory (MB)'] / 1024):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 0.5, 
             f'{val:.1f}GB', ha='center', fontweight='bold', fontsize=9)

# 3. BLEU Score Comparison
ax3 = fig.add_subplot(gs[1, 0])
for direction in ['EN→HI', 'HI→EN']:
    df_dir = df[df['Direction'] == direction]
    x = np.arange(len(df_dir))
    ax3.plot(x, df_dir['BLEU'], marker='o', linewidth=2.5, markersize=8, label=direction)
ax3.set_xticks(range(4))
ax3.set_xticklabels(['CT2\nFP16', 'CT2\nINT8', 'BnB\nINT8', 'BnB\nINT4'])
ax3.set_ylabel('BLEU Score', fontweight='bold')
ax3.set_title('Translation Quality: BLEU', fontweight='bold', fontsize=14)
ax3.legend()
ax3.grid(alpha=0.3)
ax3.set_ylim(26, 37)

# 4. COMET Score Comparison  
ax4 = fig.add_subplot(gs[1, 1])
for direction in ['EN→HI', 'HI→EN']:
    df_dir = df[df['Direction'] == direction]
    x = np.arange(len(df_dir))
    ax4.plot(x, df_dir['COMET'], marker='s', linewidth=2.5, markersize=8, label=direction)
ax4.set_xticks(range(4))
ax4.set_xticklabels(['CT2\nFP16', 'CT2\nINT8', 'BnB\nINT8', 'BnB\nINT4'])
ax4.set_ylabel('COMET Score', fontweight='bold')
ax4.set_title('Translation Quality: COMET', fontweight='bold', fontsize=14)
ax4.legend()
ax4.grid(alpha=0.3)
ax4.set_ylim(0.77, 0.88)

# 5. Load Time Comparison
ax5 = fig.add_subplot(gs[1, 2])
df_load = df[df['Direction'] == 'EN→HI']
bars = ax5.bar(range(len(df_load)), df_load['Load Time (s)'],
               color=[colors[m] for m in df_load['Model']])
ax5.set_ylabel('Load Time (seconds)', fontweight='bold')
ax5.set_title('Model Load Time', fontweight='bold', fontsize=14)
ax5.set_xticks(range(len(df_load)))
ax5.set_xticklabels(df_load['Model'], rotation=45, ha='right')
ax5.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, df_load['Load Time (s)']):
    ax5.text(bar.get_x() + bar.get_width()/2, val + 0.5, 
             f'{val:.1f}s', ha='center', fontweight='bold', fontsize=9)

# 6. Speed vs Quality Trade-off (EN→HI)
ax6 = fig.add_subplot(gs[2, :])
df_en = df[df['Direction'] == 'EN→HI']
scatter = ax6.scatter(df_en['Throughput (s/s)'], df_en['COMET'], 
                     s=[m/20 for m in df_en['GPU Memory (MB)']], 
                     c=[colors[m] for m in df_en['Model']], 
                     alpha=0.7, edgecolors='black', linewidth=2)
for i, row in df_en.iterrows():
    ax6.annotate(row['Model'], 
                (row['Throughput (s/s)'], row['COMET']),
                xytext=(10, 10), textcoords='offset points',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
ax6.set_xlabel('Throughput (sentences/second)', fontweight='bold', fontsize=12)
ax6.set_ylabel('COMET Score (Quality)', fontweight='bold', fontsize=12)
ax6.set_title('Speed vs Quality Trade-off (EN→HI)\nBubble size = GPU Memory', 
             fontweight='bold', fontsize=14)
ax6.grid(alpha=0.3)

# Add legend for bubble sizes
handles, labels = [], []
for model, mem in zip(df_en['Model'], df_en['GPU Memory (MB)']):
    handles.append(plt.scatter([], [], s=mem/20, c=colors[model], alpha=0.7, edgecolors='black'))
    labels.append(f'{model}: {mem/1024:.1f}GB')
ax6.legend(handles, labels, loc='lower right', title='Model: GPU Memory', framealpha=0.9)

# Overall title
fig.suptitle('NLLB Model Benchmark - Complete Comparison\nCTranslate2 vs BitsAndBytes Quantization', 
             fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout()
plt.savefig('nllb_complete_benchmark.png', dpi=300, bbox_inches='tight')
print("✅ Visualization saved: nllb_complete_benchmark.png")
plt.show()
