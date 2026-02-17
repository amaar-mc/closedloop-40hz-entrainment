"""
V8: Specialized EEG Architectures from Research

Based on recent literature (2024-2025):
1. EEGNet - Compact CNN for small EEG datasets
2. ATCNet - Attention Temporal Convolutional Network
3. TransformEEG-inspired - CNN-Transformer for PAC prediction

These architectures are specifically designed for EEG and proven in literature.

Sources:
- TransformEEG (Dec 2025): 4.2% improvement for Alzheimer's with PAC features
- EEGNet (2016, widely used): Designed for small BCI datasets
- ATCNet (2022): Combines attention + temporal convolutions
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
print("V8: SPECIALIZED EEG ARCHITECTURES FROM RESEARCH")
print("="*70)
print("Models:")
print("  1. EEGNet (compact, proven for small datasets)")
print("  2. ATCNet (attention + temporal convolutions)")
print("  3. TransformEEG-inspired (CNN-Transformer for PAC)")
print("="*70)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"\nDevice: {device}")

# 1. Load data
print("\n1. Loading data...")
train_data = np.load('data/processed/train_data.npz')
val_data = np.load('data/processed/val_data.npz')
test_data = np.load('data/processed/test_data.npz')

X_train = train_data['windows'].squeeze(1).astype(np.float32)
y_train = train_data['pac'].astype(np.float32)
X_val = val_data['windows'].squeeze(1).astype(np.float32)
y_val = val_data['pac'].astype(np.float32)
X_test = test_data['windows'].squeeze(1).astype(np.float32)
y_test = test_data['pac'].astype(np.float32)

print(f"✓ Data loaded: Train {X_train.shape}, Val {X_val.shape}, Test {X_test.shape}")

# 2. Normalize
print("\n2. Normalizing...")
mean_per_channel = X_train.mean(axis=(0, 2), keepdims=True)
std_per_channel = X_train.std(axis=(0, 2), keepdims=True)

X_train = (X_train - mean_per_channel) / (std_per_channel + 1e-8)
X_val = (X_val - mean_per_channel) / (std_per_channel + 1e-8)
X_test = (X_test - mean_per_channel) / (std_per_channel + 1e-8)

scaler_y = StandardScaler()
y_train = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_val = scaler_y.transform(y_val.reshape(-1, 1)).flatten()
y_test = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

# 3. Create datasets with augmentation
class PhaseSwapAugmentation:
    """Phase-swap augmentation from TransformEEG paper."""
    def __init__(self, p=0.5):
        self.p = p

    def __call__(self, x):
        if np.random.rand() < self.p:
            # Randomly swap phases between channels
            fft = np.fft.rfft(x, axis=-1)
            phase = np.angle(fft)
            magnitude = np.abs(fft)

            # Shuffle phases across channels
            shuffled_idx = np.random.permutation(x.shape[0])
            phase_shuffled = phase[shuffled_idx]

            # Reconstruct
            fft_shuffled = magnitude * np.exp(1j * phase_shuffled)
            x_aug = np.fft.irfft(fft_shuffled, n=x.shape[-1], axis=-1)
            return x_aug.astype(np.float32)
        return x

augment = PhaseSwapAugmentation(p=0.3)

class AugmentedDataset(torch.utils.data.Dataset):
    def __init__(self, X, y, augment=None):
        self.X = X
        self.y = y
        self.augment = augment

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        x = self.X[idx]
        if self.augment is not None:
            x = self.augment(x)
        return torch.from_numpy(x), torch.tensor(self.y[idx])

train_dataset = AugmentedDataset(X_train, y_train, augment=augment)
val_dataset = TensorDataset(torch.from_numpy(X_val), torch.from_numpy(y_val))
test_dataset = TensorDataset(torch.from_numpy(X_test), torch.from_numpy(y_test))

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=128, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

print("✓ Datasets created with phase-swap augmentation")

# 4. Define specialized architectures
print("\n3. Defining Models...")
print("="*70)

class EEGNet(nn.Module):
    """
    EEGNet: Compact CNN for EEG-based BCIs.

    Original paper: Lawhern et al. (2018)
    Designed for small datasets with limited training data.

    ~2,500 parameters (very compact!)
    """
    def __init__(self, n_channels=7, n_timepoints=500, F1=8, F2=16, D=2, dropout=0.5):
        super().__init__()

        # Block 1: Temporal convolution
        self.conv1 = nn.Conv2d(1, F1, (1, 64), padding=(0, 32), bias=False)
        self.bn1 = nn.BatchNorm2d(F1)

        # Block 2: Depthwise convolution (spatial filter)
        self.depthwise = nn.Conv2d(F1, F1 * D, (n_channels, 1), groups=F1, bias=False)
        self.bn2 = nn.BatchNorm2d(F1 * D)
        self.elu = nn.ELU()
        self.pool1 = nn.AvgPool2d((1, 4))
        self.dropout1 = nn.Dropout(dropout)

        # Block 3: Separable convolution
        self.separable1 = nn.Conv2d(F1 * D, F2, (1, 16), padding=(0, 8), bias=False)
        self.separable2 = nn.Conv2d(F2, F2, 1, bias=False)
        self.bn3 = nn.BatchNorm2d(F2)
        self.pool2 = nn.AvgPool2d((1, 8))
        self.dropout2 = nn.Dropout(dropout)

        # Classifier (regression)
        self.flatten = nn.Flatten()
        # Calculate flattened size
        with torch.no_grad():
            dummy = torch.zeros(1, 1, n_channels, n_timepoints)
            dummy = self.pool1(self.depthwise(self.conv1(dummy)))
            dummy = self.pool2(self.separable2(self.separable1(dummy)))
            n_features = dummy.numel()

        self.fc = nn.Linear(n_features, 1)

    def forward(self, x):
        # x: (batch, 7, 500)
        x = x.unsqueeze(1)  # (batch, 1, 7, 500)

        # Block 1
        x = self.bn1(self.conv1(x))

        # Block 2
        x = self.depthwise(x)
        x = self.bn2(x)
        x = self.elu(x)
        x = self.pool1(x)
        x = self.dropout1(x)

        # Block 3
        x = self.separable1(x)
        x = self.separable2(x)
        x = self.bn3(x)
        x = self.elu(x)
        x = self.pool2(x)
        x = self.dropout2(x)

        # Classifier
        x = self.flatten(x)
        x = self.fc(x).squeeze(-1)

        return x


class ATCNet(nn.Module):
    """
    ATCNet: Attention Temporal Convolutional Network.

    Combines multi-head self-attention with temporal convolutions.
    Based on: "Physics-informed attention temporal convolutional network" (2022)

    ~25k parameters
    """
    def __init__(self, n_channels=7, n_timepoints=500, n_windows=5, attention_heads=4):
        super().__init__()

        # Convolutional feature extractor
        self.conv1 = nn.Conv2d(1, 16, (1, 25), padding=(0, 12))
        self.bn1 = nn.BatchNorm2d(16)

        # Depthwise spatial convolution
        self.depthwise = nn.Conv2d(16, 32, (n_channels, 1), groups=16)
        self.bn2 = nn.BatchNorm2d(32)
        self.elu = nn.ELU()
        self.pool = nn.AvgPool2d((1, 4))
        self.dropout = nn.Dropout(0.5)

        # Multi-head attention
        # After pooling: 500/4 = 125 timepoints, 32 channels
        self.attention = nn.MultiheadAttention(32, attention_heads, dropout=0.3, batch_first=True)
        self.ln = nn.LayerNorm(32)

        # TCN blocks
        self.tcn1 = self._make_tcn_block(32, 64, kernel_size=3, dilation=1)
        self.tcn2 = self._make_tcn_block(64, 64, kernel_size=3, dilation=2)

        # Global pooling and classifier
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Sequential(
            nn.Linear(64, 32),
            nn.ELU(),
            nn.Dropout(0.5),
            nn.Linear(32, 1)
        )

    def _make_tcn_block(self, in_channels, out_channels, kernel_size, dilation):
        return nn.Sequential(
            nn.Conv1d(in_channels, out_channels, kernel_size, padding=dilation*(kernel_size-1)//2, dilation=dilation),
            nn.BatchNorm1d(out_channels),
            nn.ELU(),
            nn.Dropout(0.3)
        )

    def forward(self, x):
        # x: (batch, 7, 500)
        x = x.unsqueeze(1)  # (batch, 1, 7, 500)

        # CNN feature extraction
        x = self.elu(self.bn1(self.conv1(x)))
        x = self.elu(self.bn2(self.depthwise(x)))
        x = self.pool(x)
        x = self.dropout(x)

        # Reshape for attention: (batch, timepoints, channels)
        x = x.squeeze(2).transpose(1, 2)  # (batch, 125, 32)

        # Multi-head attention
        attn_out, _ = self.attention(x, x, x)
        x = self.ln(attn_out + x)  # Residual

        # Transpose back for TCN: (batch, channels, timepoints)
        x = x.transpose(1, 2)  # (batch, 32, 125)

        # TCN blocks
        x = self.tcn1(x)
        x = self.tcn2(x)

        # Global pooling and classification
        x = self.global_pool(x).squeeze(-1)  # (batch, 64)
        x = self.fc(x).squeeze(-1)

        return x


class TransformEEG(nn.Module):
    """
    TransformEEG-inspired: Convolutional-Transformer for PAC.

    Inspired by: "Self-Supervised Representation Learning for EEG-Based
    Detection of Neurodegenerative Diseases" (Dec 2025)

    Uses phase-swap augmentation and focuses on PAC features.

    ~40k parameters
    """
    def __init__(self, n_channels=7, n_timepoints=500, d_model=64, nhead=4, num_layers=2):
        super().__init__()

        # CNN encoder (local patterns)
        self.conv1 = nn.Conv1d(n_channels, 32, kernel_size=25, padding=12)
        self.bn1 = nn.BatchNorm1d(32)
        self.conv2 = nn.Conv1d(32, d_model, kernel_size=15, padding=7)
        self.bn2 = nn.BatchNorm1d(d_model)
        self.elu = nn.ELU()
        self.pool = nn.MaxPool1d(2)  # 500 -> 250
        self.dropout = nn.Dropout(0.3)

        # Positional encoding
        self.pos_encoder = nn.Parameter(torch.randn(1, 250, d_model) * 0.02)

        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 2,
            dropout=0.3,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Regression head
        self.fc = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ELU(),
            nn.Dropout(0.5),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        # x: (batch, 7, 500)

        # CNN encoding
        x = self.elu(self.bn1(self.conv1(x)))
        x = self.elu(self.bn2(self.conv2(x)))
        x = self.pool(x)
        x = self.dropout(x)

        # Transpose for transformer: (batch, timepoints, features)
        x = x.transpose(1, 2)  # (batch, 250, 64)

        # Add positional encoding
        x = x + self.pos_encoder

        # Transformer
        x = self.transformer(x)

        # Global average pooling
        x = x.mean(dim=1)  # (batch, 64)

        # Regression
        x = self.fc(x).squeeze(-1)

        return x


# 5. Training function
def train_model(model, train_loader, val_loader, n_epochs=150, patience=20):
    """Train with early stopping."""
    model = model.to(device)

    criterion = nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min',
                                                     factor=0.5, patience=7)

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
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
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
        scheduler.step(val_loss)

        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_model_state = model.state_dict()
        else:
            patience_counter += 1

        if (epoch + 1) % 15 == 0:
            print(f"  Epoch {epoch+1:3d}: Train = {train_loss:.6f}, Val = {val_loss:.6f}, "
                  f"LR = {optimizer.param_groups[0]['lr']:.6f}")

        if patience_counter >= patience:
            print(f"  Early stopping at epoch {epoch+1}")
            break

    model.load_state_dict(best_model_state)
    return model


def evaluate_model(model, loader, y_true, scaler_y):
    """Evaluate and return metrics."""
    model.eval()
    predictions = []

    with torch.no_grad():
        for X_batch, _ in loader:
            X_batch = X_batch.to(device)
            y_pred = model(X_batch)
            predictions.append(y_pred.cpu().numpy())

    predictions = np.concatenate(predictions)
    predictions = scaler_y.inverse_transform(predictions.reshape(-1, 1)).flatten()

    r2 = r2_score(y_true, predictions)
    mae = mean_absolute_error(y_true, predictions)
    corr = np.corrcoef(predictions, y_true)[0, 1]

    return r2, mae, corr, predictions


# 6. Train models
print("\n4. Training Specialized Models...")
print("="*70)

results = {}
y_val_orig = val_data['pac']
y_test_orig = test_data['pac']

# 6a. EEGNet
print("\n4a. Training EEGNet...")
model_eegnet = EEGNet()
n_params = sum(p.numel() for p in model_eegnet.parameters())
print(f"  Parameters: {n_params:,}")

t0 = time.time()
model_eegnet = train_model(model_eegnet, train_loader, val_loader)
t1 = time.time()

val_r2, val_mae, val_corr, _ = evaluate_model(model_eegnet, val_loader, y_val_orig, scaler_y)
test_r2, test_mae, test_corr, test_pred = evaluate_model(model_eegnet, test_loader, y_test_orig, scaler_y)

print(f"\n  Time: {t1-t0:.1f}s")
print(f"  Val:  R² = {val_r2:.4f}, MAE = {val_mae:.6f}, Corr = {val_corr:+.4f}")
print(f"  Test: R² = {test_r2:.4f}, MAE = {test_mae:.6f}, Corr = {test_corr:+.4f}")

results['EEGNet'] = {'val_r2': val_r2, 'test_r2': test_r2, 'test_mae': test_mae,
                     'test_corr': test_corr, 'n_params': n_params, 'predictions': test_pred}
torch.save(model_eegnet.state_dict(), 'models/eegnet_v8.pth')

# 6b. ATCNet
print("\n4b. Training ATCNet...")
model_atcnet = ATCNet()
n_params = sum(p.numel() for p in model_atcnet.parameters())
print(f"  Parameters: {n_params:,}")

t0 = time.time()
model_atcnet = train_model(model_atcnet, train_loader, val_loader)
t1 = time.time()

val_r2, val_mae, val_corr, _ = evaluate_model(model_atcnet, val_loader, y_val_orig, scaler_y)
test_r2, test_mae, test_corr, test_pred = evaluate_model(model_atcnet, test_loader, y_test_orig, scaler_y)

print(f"\n  Time: {t1-t0:.1f}s")
print(f"  Val:  R² = {val_r2:.4f}, MAE = {val_mae:.6f}, Corr = {val_corr:+.4f}")
print(f"  Test: R² = {test_r2:.4f}, MAE = {test_mae:.6f}, Corr = {test_corr:+.4f}")

results['ATCNet'] = {'val_r2': val_r2, 'test_r2': test_r2, 'test_mae': test_mae,
                     'test_corr': test_corr, 'n_params': n_params, 'predictions': test_pred}
torch.save(model_atcnet.state_dict(), 'models/atcnet_v8.pth')

# 6c. TransformEEG
print("\n4c. Training TransformEEG...")
model_transform = TransformEEG()
n_params = sum(p.numel() for p in model_transform.parameters())
print(f"  Parameters: {n_params:,}")

t0 = time.time()
model_transform = train_model(model_transform, train_loader, val_loader)
t1 = time.time()

val_r2, val_mae, val_corr, _ = evaluate_model(model_transform, val_loader, y_val_orig, scaler_y)
test_r2, test_mae, test_corr, test_pred = evaluate_model(model_transform, test_loader, y_test_orig, scaler_y)

print(f"\n  Time: {t1-t0:.1f}s")
print(f"  Val:  R² = {val_r2:.4f}, MAE = {val_mae:.6f}, Corr = {val_corr:+.4f}")
print(f"  Test: R² = {test_r2:.4f}, MAE = {test_mae:.6f}, Corr = {test_corr:+.4f}")

results['TransformEEG'] = {'val_r2': val_r2, 'test_r2': test_r2, 'test_mae': test_mae,
                           'test_corr': test_corr, 'n_params': n_params, 'predictions': test_pred}
torch.save(model_transform.state_dict(), 'models/transformeeg_v8.pth')

# 6d. Ensemble
print("\n4d. Creating Ensemble...")
ensemble_pred = np.mean([results['EEGNet']['predictions'],
                        results['ATCNet']['predictions'],
                        results['TransformEEG']['predictions']], axis=0)

ensemble_r2 = r2_score(y_test_orig, ensemble_pred)
ensemble_mae = mean_absolute_error(y_test_orig, ensemble_pred)
ensemble_corr = np.corrcoef(ensemble_pred, y_test_orig)[0, 1]

print(f"  Test: R² = {ensemble_r2:.4f}, MAE = {ensemble_mae:.6f}, Corr = {ensemble_corr:+.4f}")

results['Ensemble_V8'] = {'test_r2': ensemble_r2, 'test_mae': ensemble_mae,
                          'test_corr': ensemble_corr, 'predictions': ensemble_pred}

# 7. Results
print("\n" + "="*70)
print("RESULTS SUMMARY")
print("="*70)

print("\n📊 Performance Comparison:")
print("\nModel              | Params  | Test R² | vs Ridge | Status")
print("-------------------|---------|---------|----------|----------")

v5_ridge_r2 = 0.287

for name, res in results.items():
    r2 = res['test_r2']
    params = res.get('n_params', 0)
    vs_ridge = (r2 - v5_ridge_r2) / v5_ridge_r2 * 100

    marker = "🎯" if r2 > v5_ridge_r2 else "  "
    params_str = f"{params:,}" if params > 0 else "N/A"
    status = "BETTER!" if r2 > v5_ridge_r2 else "worse"

    print(f"{marker} {name:16s} | {params_str:>7s} | {r2:.4f} | {vs_ridge:+6.1f}% | {status}")

print(f"\n   V5 Ridge        |     N/A |  0.287 |   0.0%   | baseline")

# 8. Final verdict
print("\n" + "="*70)
print("FINAL VERDICT")
print("="*70)

best_dl = max(results.items(), key=lambda x: x[1]['test_r2'])
best_r2 = best_dl[1]['test_r2']

if best_r2 > v5_ridge_r2:
    improvement = best_r2 - v5_ridge_r2
    print(f"\n🎉 BREAKTHROUGH! {best_dl[0]} beats Ridge!")
    print(f"   Test R²: {best_r2:.4f} (+{improvement:.4f} improvement)")
    print(f"   Specialized EEG architectures work better!")
else:
    print(f"\n💡 VERDICT: Feature-based Ridge remains best (R² = {v5_ridge_r2:.4f})")
    print(f"   Best DL: {best_dl[0]} with R² = {best_r2:.4f}")
    print(f"\n   After trying {len(results)} specialized architectures:")
    print(f"   → EEGNet (designed for small datasets)")
    print(f"   → ATCNet (attention + TCN)")
    print(f"   → TransformEEG (PAC-specific)")
    print(f"\n   None beat simple Ridge with handcrafted features.")
    print(f"\n   CONCLUSION: R² ≈ 0.29 is likely the honest ceiling.")
    print(f"   This is limited by EEG noise and dataset size, not model architecture.")

print("\n" + "="*70)
