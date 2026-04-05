"""
╔══════════════════════════════════════════════════════════════════╗
║         PROJECT GENESIS — THE GREAT BENCHMARK ARENA             ║
║         "GENESIS Analog Cluster" vs "Digital AI (CPU)"          ║
╚══════════════════════════════════════════════════════════════════╝

Benchmark Tasks:
  1. MNIST Digit Classification (8x8 handwritten digits)
  2. Training Time vs Inference Time
  3. Accuracy vs Throughput tradeoff

Install dependencies:
  pip install scikit-learn matplotlib numpy pyserial
"""

import time
import json
import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────
USE_HARDWARE   = False   # Set True when GENESIS Blade is connected
PORT           = 'COM3'
BAUD           = 115200
GENESIS_CORES  = 16      # Cores per connected blade

# Load calibration if it exists
try:
    with open('calibration.json') as f:
        CAL = json.load(f)
    MULTIPLIERS = np.array(CAL['multipliers'])
    print("✅ Calibration data loaded.")
except FileNotFoundError:
    MULTIPLIERS = np.ones(GENESIS_CORES)
    print("⚠️  No calibration.json — using raw values.")

# ─────────────────────────────────────────────────────────────────
# HARDWARE LINK
# ─────────────────────────────────────────────────────────────────
ser = None
if USE_HARDWARE:
    try:
        import serial
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)
        print(f"✅ GENESIS Blade online at {PORT}")
    except Exception as e:
        print(f"⚠️  Hardware not found ({e}) — falling back to simulation.")
        USE_HARDWARE = False

# ── Fixed Reservoir Matrix (deterministic — correct ESN/RNC design) ─────────
NP_RNG        = np.random.RandomState(seed=42)
INPUT_DIM     = 64   # 8x8 MNIST pixels
W_RESERVOIR   = NP_RNG.randn(INPUT_DIM, GENESIS_CORES) * 0.5
BIAS_RESERVOIR= NP_RNG.randn(GENESIS_CORES) * 0.1


def genesis_embed(sample: np.ndarray) -> np.ndarray:
    """
    Pass a flattened image through the BCN lattice.
    Hardware mode  : sends V:X command, reads 16D analog response.
    Simulation mode: Random Projection (faithful RNC approximation).
    """
    if USE_HARDWARE and ser:
        stimulus = int(np.mean(sample) * 255)
        ser.reset_input_buffer()
        ser.write(f"V:{stimulus}\n".encode())
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith("DATA:"):
            raw = np.array([int(x) for x in line.split(":")[1].split(',')])
            return np.clip(raw * MULTIPLIERS, 0, 4095) / 4095.0
        return np.zeros(GENESIS_CORES)

    # ── Simulation: RNC via fixed random projection + tanh non-linearity ──
    # This represents the consistent physical response of the BCN lattice.
    return np.tanh(sample @ W_RESERVOIR + BIAS_RESERVOIR)

# ─────────────────────────────────────────────────────────────────
# DATA PREPARATION
# ─────────────────────────────────────────────────────────────────
print("\n📥 Loading MNIST-8x8 handwritten digits dataset...")
digits = load_digits()
X      = digits.data / 16.0   # Normalize to [0, 1]
y      = digits.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   Train: {len(X_train)} samples | Test: {len(X_test)} samples")

# ─────────────────────────────────────────────────────────────────
# CONTESTANT 1: DIGITAL MLP (The Challenger)
# ─────────────────────────────────────────────────────────────────
print("\n🔵 DIGITAL AI — Training MLP (100 hidden neurons)...")
mlp = MLPClassifier(hidden_layer_sizes=(100,), max_iter=500,
                    random_state=42, early_stopping=False)

t0 = time.perf_counter()
mlp.fit(X_train, y_train)
digital_train_time = time.perf_counter() - t0

t0 = time.perf_counter()
y_pred_digital = mlp.predict(X_test)
digital_infer_time = time.perf_counter() - t0

acc_digital = accuracy_score(y_test, y_pred_digital)
print(f"   Train time : {digital_train_time*1000:.1f} ms")
print(f"   Infer time : {digital_infer_time*1000:.1f} ms ({len(X_test)} samples)")
print(f"   Accuracy   : {acc_digital*100:.2f}%")

# ─────────────────────────────────────────────────────────────────
# CONTESTANT 2: GENESIS ANALOG CLUSTER (The Material Champion)
# ─────────────────────────────────────────────────────────────────
print("\n🔴 GENESIS ANALOG — Extracting reservoir states...")

t0 = time.perf_counter()
X_train_g = np.array([genesis_embed(s) for s in X_train])
X_test_g  = np.array([genesis_embed(s) for s in X_test])
hardware_extract_time = time.perf_counter() - t0

print(f"   Reservoir extraction: {hardware_extract_time*1000:.1f} ms")
print(f"   Feature dimension   : {X_train_g.shape[1]}D")

# Readout layer — single linear model (true Echo State / RNC paradigm)
print("   Training readout layer (Logistic Regression)...")
t0 = time.perf_counter()
scaler  = StandardScaler()
X_tr_sc = scaler.fit_transform(X_train_g)
X_te_sc = scaler.transform(X_test_g)

readout = LogisticRegression(max_iter=1000, random_state=42, C=10)
readout.fit(X_tr_sc, y_train)
genesis_train_time = time.perf_counter() - t0

t0 = time.perf_counter()
y_pred_genesis = readout.predict(X_te_sc)
genesis_infer_time = time.perf_counter() - t0

acc_genesis = accuracy_score(y_test, y_pred_genesis)
print(f"   Readout train time : {genesis_train_time*1000:.1f} ms")
print(f"   Infer time         : {genesis_infer_time*1000:.1f} ms")
print(f"   Accuracy           : {acc_genesis*100:.2f}%")

# ─────────────────────────────────────────────────────────────────
# SCOREBOARD
# ─────────────────────────────────────────────────────────────────
print("\n" + "═"*52)
print("           ⚔️  BENCHMARK SCOREBOARD ⚔️")
print("═"*52)
print(f"{'Metric':<28} {'Digital':>10} {'GENESIS':>10}")
print("─"*52)
print(f"{'Accuracy':<28} {acc_digital*100:>9.2f}% {acc_genesis*100:>9.2f}%")
print(f"{'Training Time (ms)':<28} {digital_train_time*1000:>10.1f} {genesis_train_time*1000:>10.1f}")
print(f"{'Inference Time (ms)':<28} {digital_infer_time*1000:>10.1f} {genesis_infer_time*1000:>10.1f}")
print(f"{'Feature Dimensions':<28} {'64':>10} {str(GENESIS_CORES):>10}")
print(f"{'Hardware Required':<28} {'CPU/GPU':>10} {'BCN Chip':>10}")
mode_label = "HARDWARE" if USE_HARDWARE else "SIMULATED"
print(f"{'GENESIS Mode':<28} {'—':>10} {mode_label:>10}")
print("═"*52)

winner_acc    = "DIGITAL" if acc_digital > acc_genesis else "GENESIS"
winner_speed  = "GENESIS" if genesis_train_time < digital_train_time else "DIGITAL"
print(f"  🏆 Accuracy Winner  : {winner_acc}")
print(f"  ⚡ Speed Winner     : {winner_speed}")
print("═"*52)

# ─────────────────────────────────────────────────────────────────
# VISUALIZATION
# ─────────────────────────────────────────────────────────────────
plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 9), facecolor='#0a0a0f')
gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

BLUE = '#00aaff'
RED  = '#ff4444'
GOLD = '#ffd700'

# ── Panel 1: Accuracy Bar ────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
bars = ax1.bar(['Digital\n(MLP)', 'GENESIS\n(Analog)'],
               [acc_digital*100, acc_genesis*100],
               color=[BLUE, RED], width=0.5, zorder=3)
for bar, val in zip(bars, [acc_digital*100, acc_genesis*100]):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f'{val:.1f}%', ha='center', va='bottom', color='white', fontweight='bold')
ax1.set_ylim(0, 110)
ax1.set_title('Accuracy (%)', color=GOLD, fontweight='bold')
ax1.set_facecolor('#12121a')
ax1.grid(axis='y', alpha=0.2)
ax1.tick_params(colors='white')
ax1.spines[:].set_color('#333')

# ── Panel 2: Training Speed ──────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
times = [digital_train_time*1000, genesis_train_time*1000]
bars2 = ax2.bar(['Digital\n(MLP)', 'GENESIS\n(Readout)'],
                times, color=[BLUE, RED], width=0.5, zorder=3)
for bar, val in zip(bars2, times):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{val:.0f}ms', ha='center', va='bottom', color='white', fontweight='bold')
ax2.set_title('Readout Training Time (ms)\n[Lower = Better]', color=GOLD, fontweight='bold')
ax2.set_facecolor('#12121a')
ax2.grid(axis='y', alpha=0.2)
ax2.tick_params(colors='white')
ax2.spines[:].set_color('#333')

# ── Panel 3: Confusion Matrix (GENESIS) ──────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
cm = confusion_matrix(y_test, y_pred_genesis)
im = ax3.imshow(cm, aspect='auto', cmap='plasma')
ax3.set_title(f'GENESIS Confusion Matrix\n(Acc: {acc_genesis*100:.1f}%)', color=GOLD, fontweight='bold')
ax3.set_xlabel('Predicted', color='white')
ax3.set_ylabel('Actual', color='white')
ax3.tick_params(colors='white')
plt.colorbar(im, ax=ax3)

# ── Panel 4: Training Loss (Digital MLP) ─────────────────────────
ax4 = fig.add_subplot(gs[1, 0])
ax4.plot(mlp.loss_curve_, color=BLUE, lw=2)
ax4.set_title('Digital MLP Loss Curve', color=GOLD, fontweight='bold')
ax4.set_xlabel('Epoch', color='white')
ax4.set_ylabel('Loss', color='white')
ax4.set_facecolor('#12121a')
ax4.grid(alpha=0.2)
ax4.tick_params(colors='white')
ax4.spines[:].set_color('#333')

# ── Panel 5: GENESIS Reservoir Feature Spread ────────────────────
ax5 = fig.add_subplot(gs[1, 1])
for label in range(10):
    mask = (y_train == label)
    ax5.scatter(X_train_g[mask, 0], X_train_g[mask, 1 % GENESIS_CORES],
                label=str(label), s=15, alpha=0.7)
ax5.set_title('GENESIS Reservoir State Space\n(First 2 Dims)', color=GOLD, fontweight='bold')
ax5.set_xlabel('Dim-0', color='white')
ax5.set_ylabel('Dim-1', color='white')
ax5.legend(loc='upper right', fontsize=6, ncol=2)
ax5.set_facecolor('#12121a')
ax5.grid(alpha=0.2)
ax5.tick_params(colors='white')
ax5.spines[:].set_color('#333')

# ── Panel 6: Summary Scorecard ────────────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis('off')
ax6.set_facecolor('#12121a')
summary_text = (
    f"  ⚔️  FINAL SCORECARD\n"
    f"{'─'*32}\n"
    f"  Accuracy\n"
    f"    Digital  : {acc_digital*100:.2f}%\n"
    f"    GENESIS  : {acc_genesis*100:.2f}%\n\n"
    f"  Training Speed\n"
    f"    Digital  : {digital_train_time*1000:.0f} ms\n"
    f"    GENESIS  : {genesis_train_time*1000:.0f} ms\n\n"
    f"  Inference Speed\n"
    f"    Digital  : {digital_infer_time*1000:.1f} ms\n"
    f"    GENESIS  : {genesis_infer_time*1000:.1f} ms\n\n"
    f"  Mode     : {mode_label}\n"
    f"  Cores    : {GENESIS_CORES}\n"
    f"{'─'*32}\n"
    f"  Winner (Accuracy) : {winner_acc}\n"
    f"  Winner (Speed)    : {winner_speed}"
)
ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
         family='monospace', color='white', fontsize=8.5,
         verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor=GOLD, alpha=0.9))

fig.suptitle('PROJECT GENESIS  vs.  DIGITAL AI   |   The Great Benchmark',
             color=GOLD, fontsize=14, fontweight='bold', y=0.98)

plt.savefig('genesis_benchmark_results.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0f')
plt.show()
print("\n📊 Chart saved to genesis_benchmark_results.png")

if ser:
    ser.close()
