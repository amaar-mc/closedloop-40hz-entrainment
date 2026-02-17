"""
V7: Lightweight Deep Learning on Raw EEG

Different approach: Learn features directly from raw EEG instead of handcrafted features.

Models tested:
1. 1D CNN (~20k params) - learns spectro-temporal patterns
2. Multi-head Attention (~15k params) - focuses on important time points
3. CNN-Attention Hybrid (~30k params) - combines both

All models kept small (<50k params) to avoid overfitting with 11k samples.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import time

print("="*70)
print("V7: LIGHTWEIGHT DEEP LEARNING ON RAW EEG")
print("="*70)
print("Approach: Learn features from raw EEG (not handcrafted features)")
print("Models: 1D CNN, Attention, CNN-Attention Hybrid")
print("All models < 50k params to prevent overfitting")
print("="*70)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"\nDevice: {device}")

# 1. Load raw EEG data
print("\n1. Loading raw EEG data...")
train_data = np.load('data/processed/train_data.npz')
val_data = np.load('data/processed/val_data.npz')
test_data = np.load('data/processed/test_data.npz')

X_train = train_data['windows'].squeeze(1).astype(np.float32)  # (11736, 7, 500)
y_train = train_data['pac'].astype(np.float32)
X_val = val_data['windows'].squeeze(1).astype(np.float32)
y_val = val_data['pac'].astype(np.float32)
X_test = test_data['windows'].squeeze(1).astype(np.float32)
y_test = test_data['pac'].astype(np.float32)

print(f"✓ Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
print(f"  Input: (n_samples, 7 channels, 500 timepoints)")

# 2. Normalize per channel
print("\n2. Normalizing EEG per channel...")
# Compute mean and std per channel across all samples
mean_per_channel = X_train.mean(axis=(0, 2), keepdims=True)  # (1, 7, 1)
std_per_channel = X_train.std(axis=(0, 2), keepdims=True)

X_train = (X_train - mean_per_channel) / (std_per_channel + 1e-8)
X_val = (X_val - mean_per_channel) / (std_per_channel + 1e-8)
X_test = (X_test - mean_per_channel) / (std_per_channel + 1e-8)

# Normalize targets
scaler_y = StandardScaler()
y_train = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_val = scaler_y.transform(y_val.reshape(-1, 1)).flatten()
y_test = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

print("✓ Normalization complete")

# 3. Create PyTorch datasets
train_dataset = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
val_dataset = TensorDataset(torch.from_numpy(X_val), torch.from_numpy(y_val))
test_dataset = TensorDataset(torch.from_numpy(X_test), torch.from_numpy(y_test))

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=128, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

print("✓ DataLoaders created")

# 4. Define models
print("\n3. Defining Models...")
print("="*70)

class CNN1D(nn.Module):
    """
    1D CNN for EEG time series.

    Learns spectro-temporal filters from raw EEG.
    ~20k parameters.
    """
    def __init__(self, n_channels=7, n_timepoints=500):
        super().__init__()

        # Convolutional layers (learn temporal filters)
        self.conv1 = nn.Conv1d(n_channels, 32, kernel_size=25, stride=2, padding=12)
        self.bn1 = nn.BatchNorm1d(32)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=15, stride=2, padding=7)
        self.bn2 = nn.BatchNorm1d(64)
        self.conv3 = nn.Conv1d(64, 64, kernel_size=7, stride=2, padding=3)
        self.bn3 = nn.BatchNorm1d(64)

        self.pool = nn.AdaptiveAvgPool1d(1)
        self.dropout = nn.Dropout(0.5)

        # Regression head
        self.fc = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        # x: (batch, 7, 500)
        x = torch.relu(self.bn1(self.conv1(x)))
        x = torch.relu(self.bn2(self.conv2(x)))
        x = torch.relu(self.bn3(self.conv3(x)))

        x = self.pool(x).squeeze(-1)  # (batch, 64)
        x = self.dropout(x)
        x = self.fc(x).squeeze(-1)  # (batch,)

        return x


class AttentionModel(nn.Module):
    """
    Multi-head attention over time points.

    Learns which time points are important for PAC prediction.
    ~15k parameters.
    """
    def __init__(self, n_channels=7, n_timepoints=500, d_model=64, n_heads=4):
        super().__init__()

        # Project channels to d_model
        self.channel_proj = nn.Linear(n_channels, d_model)

        # Multi-head attention
        self.attention = nn.MultiheadAttention(d_model, n_heads, dropout=0.3, batch_first=True)

        # Layer norm
        self.ln = nn.LayerNorm(d_model)

        # Regression head
        self.fc = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        # x: (batch, 7, 500)
        x = x.transpose(1, 2)  # (batch, 500, 7)

        # Project
        x = self.channel_proj(x)  # (batch, 500, d_model)

        # Self-attention
        attn_out, _ = self.attention(x, x, x)
        x = self.ln(attn_out + x)  # Residual + norm

        # Global average pooling
        x = x.mean(dim=1)  # (batch, d_model)

        # Regression
        x = self.fc(x).squeeze(-1)  # (batch,)

        return x


class CNNAttentionHybrid(nn.Module):
    """
    Hybrid: CNN extracts features, Attention pools them.

    Combines local pattern detection (CNN) with global context (Attention).
    ~30k parameters.
    """
    def __init__(self, n_channels=7, n_timepoints=500):
        super().__init__()

        # CNN feature extractor
        self.conv1 = nn.Conv1d(n_channels, 32, kernel_size=25, stride=2, padding=12)
        self.bn1 = nn.BatchNorm1d(32)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=15, stride=2, padding=7)
        self.bn2 = nn.BatchNorm1d(64)

        # After 2 stride-2 convs: 500 -> 250 -> 125 timepoints
        reduced_timepoints = n_timepoints // 4

        # Attention over CNN features
        self.attention = nn.MultiheadAttention(64, 4, dropout=0.3, batch_first=True)
        self.ln = nn.LayerNorm(64)

        # Regression head
        self.fc = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        # x: (batch, 7, 500)

        # CNN feature extraction
        x = torch.relu(self.bn1(self.conv1(x)))
        x = torch.relu(self.bn2(self.conv2(x)))
        # x: (batch, 64, 125)

        x = x.transpose(1, 2)  # (batch, 125, 64)

        # Attention
        attn_out, _ = self.attention(x, x, x)
        x = self.ln(attn_out + x)

        # Global pooling
        x = x.mean(dim=1)  # (batch, 64)

        # Regression
        x = self.fc(x).squeeze(-1)  # (batch,)

        return x


# 5. Training function
def train_model(model, train_loader, val_loader, n_epochs=100, patience=15):
    """Train model with early stopping."""
    model = model.to(device)

    criterion = nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min',
                                                     factor=0.5, patience=5)

    best_val_loss = float('inf')
    patience_counter = 0
    best_model_state = None

    for epoch in range(n_epochs):
        # Training
        model.train()
        train_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)

            optimizer.zero_grad()
            y_pred = model(X_batch)
            loss = criterion(y_pred, y_batch)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * len(X_batch)

        train_loss /= len(train_loader.dataset)

        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                y_pred = model(X_batch)
                loss = criterion(y_pred, y_batch)
                val_loss += loss.item() * len(X_batch)

        val_loss /= len(val_loader.dataset)

        # Learning rate scheduling
        scheduler.step(val_loss)

        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_model_state = model.state_dict()
        else:
            patience_counter += 1

        if (epoch + 1) % 10 == 0:
            print(f"  Epoch {epoch+1:3d}: Train Loss = {train_loss:.6f}, "
                  f"Val Loss = {val_loss:.6f}, LR = {optimizer.param_groups[0]['lr']:.6f}")

        if patience_counter >= patience:
            print(f"  Early stopping at epoch {epoch+1}")
            break

    # Load best model
    model.load_state_dict(best_model_state)
    return model


def evaluate_model(model, loader, y_true, scaler_y):
    """Evaluate model and return predictions."""
    model.eval()
    predictions = []

    with torch.no_grad():
        for X_batch, _ in loader:
            X_batch = X_batch.to(device)
            y_pred = model(X_batch)
            predictions.append(y_pred.cpu().numpy())

    predictions = np.concatenate(predictions)

    # Denormalize
    predictions = scaler_y.inverse_transform(predictions.reshape(-1, 1)).flatten()

    # Compute metrics
    r2 = r2_score(y_true, predictions)
    mae = mean_absolute_error(y_true, predictions)
    corr = np.corrcoef(predictions, y_true)[0, 1]

    return r2, mae, corr, predictions


# 6. Train models
print("\n4. Training Models...")
print("="*70)

results = {}

# Original targets (denormalized for evaluation)
y_val_orig = val_data['pac']
y_test_orig = test_data['pac']

# 6a. 1D CNN
print("\n4a. Training 1D CNN...")
print("  Parameters: ~20k")
model_cnn = CNN1D()
n_params_cnn = sum(p.numel() for p in model_cnn.parameters())
print(f"  Actual parameters: {n_params_cnn:,}")

t0 = time.time()
model_cnn = train_model(model_cnn, train_loader, val_loader)
t1 = time.time()

val_r2, val_mae, val_corr, _ = evaluate_model(model_cnn, val_loader, y_val_orig, scaler_y)
test_r2, test_mae, test_corr, test_pred = evaluate_model(model_cnn, test_loader, y_test_orig, scaler_y)

print(f"\n  Training time: {t1-t0:.1f}s")
print(f"  Val:  R² = {val_r2:.4f}, MAE = {val_mae:.6f}, Corr = {val_corr:+.4f}")
print(f"  Test: R² = {test_r2:.4f}, MAE = {test_mae:.6f}, Corr = {test_corr:+.4f}")

results['CNN1D'] = {
    'val_r2': val_r2,
    'test_r2': test_r2,
    'test_mae': test_mae,
    'test_corr': test_corr,
    'n_params': n_params_cnn,
    'predictions': test_pred
}

# Save model
torch.save(model_cnn.state_dict(), 'models/cnn1d_v7.pth')

# 6b. Attention Model
print("\n4b. Training Attention Model...")
print("  Parameters: ~15k")
model_attn = AttentionModel()
n_params_attn = sum(p.numel() for p in model_attn.parameters())
print(f"  Actual parameters: {n_params_attn:,}")

t0 = time.time()
model_attn = train_model(model_attn, train_loader, val_loader)
t1 = time.time()

val_r2, val_mae, val_corr, _ = evaluate_model(model_attn, val_loader, y_val_orig, scaler_y)
test_r2, test_mae, test_corr, test_pred = evaluate_model(model_attn, test_loader, y_test_orig, scaler_y)

print(f"\n  Training time: {t1-t0:.1f}s")
print(f"  Val:  R² = {val_r2:.4f}, MAE = {val_mae:.6f}, Corr = {val_corr:+.4f}")
print(f"  Test: R² = {test_r2:.4f}, MAE = {test_mae:.6f}, Corr = {test_corr:+.4f}")

results['Attention'] = {
    'val_r2': val_r2,
    'test_r2': test_r2,
    'test_mae': test_mae,
    'test_corr': test_corr,
    'n_params': n_params_attn,
    'predictions': test_pred
}

torch.save(model_attn.state_dict(), 'models/attention_v7.pth')

# 6c. CNN-Attention Hybrid
print("\n4c. Training CNN-Attention Hybrid...")
print("  Parameters: ~30k")
model_hybrid = CNNAttentionHybrid()
n_params_hybrid = sum(p.numel() for p in model_hybrid.parameters())
print(f"  Actual parameters: {n_params_hybrid:,}")

t0 = time.time()
model_hybrid = train_model(model_hybrid, train_loader, val_loader)
t1 = time.time()

val_r2, val_mae, val_corr, _ = evaluate_model(model_hybrid, val_loader, y_val_orig, scaler_y)
test_r2, test_mae, test_corr, test_pred = evaluate_model(model_hybrid, test_loader, y_test_orig, scaler_y)

print(f"\n  Training time: {t1-t0:.1f}s")
print(f"  Val:  R² = {val_r2:.4f}, MAE = {val_mae:.6f}, Corr = {val_corr:+.4f}")
print(f"  Test: R² = {test_r2:.4f}, MAE = {test_mae:.6f}, Corr = {test_corr:+.4f}")

results['CNN_Attention'] = {
    'val_r2': val_r2,
    'test_r2': test_r2,
    'test_mae': test_mae,
    'test_corr': test_corr,
    'n_params': n_params_hybrid,
    'predictions': test_pred
}

torch.save(model_hybrid.state_dict(), 'models/cnn_attention_v7.pth')

# 7. Ensemble of all three
print("\n4d. Creating Ensemble (average of 3 models)...")
ensemble_pred = np.mean([results['CNN1D']['predictions'],
                        results['Attention']['predictions'],
                        results['CNN_Attention']['predictions']], axis=0)

ensemble_r2 = r2_score(y_test_orig, ensemble_pred)
ensemble_mae = mean_absolute_error(y_test_orig, ensemble_pred)
ensemble_corr = np.corrcoef(ensemble_pred, y_test_orig)[0, 1]

print(f"  Test: R² = {ensemble_r2:.4f}, MAE = {ensemble_mae:.6f}, Corr = {ensemble_corr:+.4f}")

results['Ensemble_DL'] = {
    'test_r2': ensemble_r2,
    'test_mae': ensemble_mae,
    'test_corr': ensemble_corr,
    'predictions': ensemble_pred
}

# 8. Results summary
print("\n" + "="*70)
print("RESULTS SUMMARY")
print("="*70)

print("\n📊 Performance Comparison:")
print("\nModel                | Params | Test R² | vs Ridge | vs Baseline")
print("---------------------|--------|---------|----------|-------------")

v5_ridge_r2 = 0.287
v6_best_r2 = 0.287
baseline_r2 = 0.236

for model_name, result in results.items():
    test_r2 = result['test_r2']
    params = result.get('n_params', 0)
    vs_ridge = (test_r2 - v5_ridge_r2) / v5_ridge_r2 * 100
    vs_baseline = (test_r2 - baseline_r2) / baseline_r2 * 100

    marker = "⭐" if test_r2 > v6_best_r2 else "  "
    params_str = f"{params:,}" if params > 0 else "N/A"
    print(f"{marker} {model_name:18s} | {params_str:>6s} | {test_r2:.4f} | {vs_ridge:+6.1f}% | {vs_baseline:+6.1f}%")

print(f"\n   V6 Best (GBoost)  | N/A    | {v6_best_r2:.4f} |   0.0%   |  +21.5%")
print(f"   V5 Ridge          | N/A    | {v5_ridge_r2:.4f} |   0.0%   |  +21.6%")
print(f"   V3-Clean          | N/A    | {baseline_r2:.4f} | -17.8%   |   0.0%")

# 9. Final assessment
print("\n" + "="*70)
print("FINAL ASSESSMENT")
print("="*70)

best_dl_model = max(results.items(), key=lambda x: x[1]['test_r2'])[0]
best_dl_r2 = results[best_dl_model]['test_r2']

print(f"\n🏆 Best Deep Learning Model: {best_dl_model}")
print(f"   Test R²: {best_dl_r2:.4f}")

if best_dl_r2 > v6_best_r2 + 0.01:
    print("\n🎉 BREAKTHROUGH! Deep learning on raw EEG works better!")
    print(f"   → Improvement: +{(best_dl_r2 - v6_best_r2):.4f} over V6")
    print(f"   → Raw EEG contains patterns missed by handcrafted features")
elif best_dl_r2 > v6_best_r2 - 0.01:
    print("\n~ SIMILAR PERFORMANCE")
    print(f"   → Deep learning ≈ feature-based approaches")
    print(f"   → Both capture similar information")
else:
    print("\n❌ DEEP LEARNING UNDERPERFORMED")
    print(f"   → Feature-based methods still better")
    print(f"   → Raw EEG approach needs more data or different architecture")

target_r2 = 0.46
gap = target_r2 - best_dl_r2
print(f"\n📈 Progress Toward Target:")
print(f"   Current (V7 best): R² = {best_dl_r2:.4f}")
print(f"   Target:            R² = {target_r2:.4f}")
print(f"   Gap:               {gap:.4f}")

if best_dl_r2 >= 0.35:
    print("\n✅ Significant progress! Near target range.")
else:
    print("\n⚠️  Still far from target. May need:")
    print("     1. More training data")
    print("     2. Different architecture")
    print("     3. Better preprocessing")
    print("     4. Accept R² ≈ 0.29 as ceiling")

print("\n" + "="*70)
print("✓ Models saved to models/ directory")
print("="*70)
