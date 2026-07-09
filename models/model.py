"""Representation–head split network for RUL estimation.

Body  (federated, shared):  1D-CNN over the sensor window -> LSTM -> latent vector.
Head  (client-local):       MLP mapping latent -> scalar RUL.

Only body parameters are exchanged with the server. The head stays on the
client, which is what makes the model personalized under non-IID data while
still sharing a common feature extractor.
"""
import torch
import torch.nn as nn


class Body(nn.Module):
    """Shared feature extractor. Input: (B, window, F)."""

    def __init__(self, n_features, n_filters, lstm_hidden, latent_dim, dropout):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(n_features, n_filters, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(n_filters, n_filters, kernel_size=3, padding=1),
            nn.ReLU(),
        )
        self.lstm = nn.LSTM(n_filters, lstm_hidden, batch_first=True)
        self.proj = nn.Sequential(
            nn.Linear(lstm_hidden, latent_dim), nn.ReLU(), nn.Dropout(dropout)
        )

    def forward(self, x):
        # x: (B, window, F) -> conv wants (B, F, window)
        h = self.conv(x.transpose(1, 2)).transpose(1, 2)   # (B, window, filters)
        out, _ = self.lstm(h)                              # (B, window, hidden)
        return self.proj(out[:, -1, :])                    # (B, latent)


class Head(nn.Module):
    """Client-local RUL regressor."""

    def __init__(self, latent_dim, hidden, dropout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1),
        )

    def forward(self, z):
        return self.net(z).squeeze(-1)


class RULNet(nn.Module):
    def __init__(self, cfg, n_features):
        super().__init__()
        self.body = Body(
            n_features, cfg.n_body_filters, cfg.lstm_hidden, cfg.latent_dim, cfg.dropout
        )
        self.head = Head(cfg.latent_dim, cfg.head_hidden, cfg.dropout)

    def forward(self, x):
        return self.head(self.body(x))

    # ---- parameter views used by the federation ----
    # head_local=True  -> only the body is shared (rep-head split, DGFed)
    # head_local=False -> the full model is shared (faithful FedAvg / FedProx)
    def shared_state(self, head_local: bool = True):
        src = self.body if head_local else self
        return {k: v.detach().cpu().clone() for k, v in src.state_dict().items()}

    def load_shared_state(self, state, head_local: bool = True):
        target = self.body if head_local else self
        target.load_state_dict(state)
