# 📦 RunPod Upload Checklist

## Files to Upload to RunPod

Upload these files/folders to your RunPod instance:

### 1. Scripts Folder
```
scripts/
├── benchmark_nllb_models.py  ✅ Main benchmark script
├── analyze_results.py         ✅ Analysis & visualization
├── requirements.txt           ✅ Python dependencies
└── README.md                  ✅ Documentation
```

### 2. Evaluation Datasets Folder
```
eval_dataset/
├── FLORES/
│   ├── flores_eng.txt        ✅ 1,013 English sentences
│   └── flores_hin.txt        ✅ 1,013 Hindi sentences
└── NTREX/
    ├── newstest2019-src.eng.txt  ✅ 1,998 English sentences
    └── newstest2019-ref.hin.txt  ✅ 1,998 Hindi sentences
```

## Upload Methods

### Option 1: Using RunPod Web Terminal (Recommended)

1. **Zip the files locally**:
   ```bash
   # In your project root
   zip -r benchmark_suite.zip scripts/ eval_dataset/
   ```

2. **Upload via RunPod File Browser**:
   - Open your RunPod pod
   - Click "Connect" → "Start Web Terminal"
   - Use the file upload button in the web terminal
   - Upload `benchmark_suite.zip`

3. **Extract on RunPod**:
   ```bash
   cd /workspace
   unzip benchmark_suite.zip
   ls -la scripts/ eval_dataset/
   ```

### Option 2: Using SCP (If you have SSH access)

```bash
scp -r scripts/ eval_dataset/ root@<runpod-ip>:/workspace/
```

### Option 3: Using Git (If you have a repo)

```bash
# On RunPod
cd /workspace
git clone <your-repo-url>
cd <repo-name>
```

## Verify Upload

Run this on RunPod to verify everything is uploaded correctly:

```bash
cd /workspace

# Check scripts
ls -lh scripts/
# Should show: benchmark_nllb_models.py, analyze_results.py, requirements.txt, README.md

# Check datasets
wc -l eval_dataset/FLORES/*.txt
# Should show: 1013 flores_eng.txt, 1013 flores_hin.txt

wc -l eval_dataset/NTREX/*.txt
# Should show: 1998 newstest2019-src.eng.txt, 1998 newstest2019-ref.hin.txt

# Total check
echo "Total EN→HI sentences: $((1013 + 1998))"
echo "Total HI→EN sentences: $((1013 + 1998))"
# Should both show: 3011
```

## Next Steps

Once uploaded and verified:

1. **Install dependencies**:
   ```bash
   cd /workspace/scripts
   pip install -r requirements.txt
   ```

2. **Start benchmark in tmux**:
   ```bash
   tmux new -s nllb_benchmark
   python benchmark_nllb_models.py
   ```

3. **Detach from tmux**: Press `Ctrl+B`, then `D`

4. **Check progress later**:
   ```bash
   tmux attach -t nllb_benchmark
   ```

## Storage Requirements

- **Scripts**: ~50 KB
- **Evaluation Datasets**: ~5-10 MB
- **Benchmark Results**: ~50-100 MB (JSON + CSV)
- **Total**: ~150 MB

✅ All files fit comfortably in RunPod's workspace!
