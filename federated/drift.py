"""Page-Hinkley concept-drift detector.

Fed the stream of per-sample prediction *residuals* (|pred - true|). Detecting on
residuals rather than raw inputs means we flag genuine target drift (the model
getting worse) rather than benign covariate shift. Detection is local to each
client, because degradation regimes shift asynchronously across the fleet.
"""


class PageHinkley:
    def __init__(self, delta=0.005, lam=50.0, alpha=0.9999):
        self.delta = delta      # tolerance / allowed magnitude of change
        self.lam = lam          # detection threshold
        self.alpha = alpha      # forgetting factor for the running mean
        self.reset()

    def reset(self):
        self.n = 0
        self.mean = 0.0
        self.cum = 0.0          # cumulative deviation
        self.min_cum = 0.0

    def update(self, value: float) -> bool:
        """Feed one residual; return True if drift is detected."""
        self.n += 1
        # running mean with forgetting
        self.mean = self.alpha * self.mean + (1 - self.alpha) * value if self.n > 1 else value
        self.cum = self.cum * self.alpha + (value - self.mean - self.delta)
        self.min_cum = min(self.min_cum, self.cum)
        drift = (self.cum - self.min_cum) > self.lam
        if drift:
            self.reset()
        return drift

    def update_stream(self, residuals) -> bool:
        """Feed a batch of residuals; return True if drift fired at least once."""
        flagged = False
        for r in residuals:
            if self.update(float(r)):
                flagged = True
        return flagged
