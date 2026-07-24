# Signal Processing for Beyond-5G and 6G Communications
## Slide-by-Slide Outline — 90-minute invited talk

**Audience:** engineering faculty, PG students, research scholars (communications/DSP background)
**Budget:** 70 min slides · 15 min live MATLAB demos (**interleaved**: each demo runs right after its home section) · 5 min Q&A buffer
**Deck size:** 70 numbered slides + 5 appendix "Backup: pre-computed result" slides (one per demo)

**Demo placement (approved):** D1 after Sec. 3 (slide 20) · D2 after Sec. 4 (slide 29) · D3 after Sec. 5 (slide 35) · D4 after Sec. 6 (slide 42) · D5 after Sec. 7 (slide 50). The closing slide of each host section doubles as the demo transition slide.

Legend per slide: **[time]** estimated speaking time · **Eq:** equation(s) to typeset · **Fig:** figure/diagram needed.

---

## Section 1 — Opening & Motivation (Slides 1–5, 6 min)

### Slide 1 — Title slide [0.5 min]
- Talk title, speaker name/affiliation, venue, date
- One-line hook: "6G is a signal processing problem"
- QR code / short URL to slides + demo code (optional)
- **Fig:** clean title layout; subtle 6G-themed accent graphic

### Slide 2 — Six generations in forty years: 1G → 6G [1.5 min]
- 1G analog voice → 2G digital → 3G data → 4G mobile broadband (OFDM/MIMO) → 5G verticals (eMBB/URLLC/mMTC)
- Each generation ≈ 10 years, ≈ 10–100× peak-rate jump
- The pattern: every generation is *defined* by its physical-layer signal processing choices
- 6G research window is now: ITU framework 2023, 3GPP study from Rel-20, spec by ~2029
- **Fig:** horizontal timeline 1980→2030 with per-generation PHY highlights

### Slide 3 — The IMT-2030 vision [1.5 min]
- ITU-R M.2160 (Nov 2023): the official "what is 6G" document
- Three 5G scenarios extended: immersive comm., hyper-reliable low-latency comm., massive comm.
- Three genuinely new scenarios: **ISAC**, **AI and communication**, **ubiquitous connectivity**
- Overarching design values: sustainability, security/resilience, connecting the unconnected
- **Fig:** IMT-2030 usage-scenario wheel (redrawn, not the ITU original)

### Slide 4 — KPI targets: 5G vs 6G [1.5 min]
- Peak rate: 20 Gb/s → 200 Gb/s–1 Tb/s research target
- User-plane latency: 1 ms → 0.1–1 ms; connection density: 10⁶ → 10⁶–10⁸ devices/km²
- New KPI classes: sensing accuracy (cm-level ranging, ~m positioning), AI-related capabilities, energy efficiency
- Caution: IMT-2030 gives *ranges*, not single numbers — targets are scenario-dependent
- **Fig:** KPI comparison table (5G IMT-2020 vs 6G IMT-2030 columns)

### Slide 5 — Why signal processing is both bottleneck and enabler [1 min]
- Shannon gap at sub-6 GHz nearly closed → gains must come from *new dimensions*: bandwidth, aperture, environment, semantics
- Every 6G headline tech is a DSP problem: waveforms, arrays, surfaces, sensing, learning
- Hardware gets *worse* as frequency rises → DSP must compensate (impairment-aware design)
- Roadmap of this talk (the 10 sections + 5 live demos)
- **Fig:** talk roadmap graphic (sections as a signal-chain block diagram)

---

## Section 2 — New Spectrum Frontiers (Slides 6–11, 7 min)

### Slide 6 — The 6G spectrum landscape [1 min]
- Sub-6 GHz: coverage workhorse, congested
- FR3 / upper mid-band 7–24 GHz: the "golden bands" — capacity *and* reasonable coverage
- FR2 mmWave 24–71 GHz: deployed but niche; sub-THz 100–300 GHz: research frontier
- WRC-23 identified new IMT bands incl. parts of 4.4–4.8, 7.1–8.4, 14.8–15.35 GHz (region-dependent)
- **Fig:** log-frequency spectrum bar chart with band annotations

### Slide 7 — FR3 / upper mid-band: the pragmatic 6G band [1 min]
- Why 7–15 GHz first: ~2–4× bandwidth vs C-band with manageable path loss
- Massive MIMO scales naturally: same aperture → 4–9× more elements than 3.5 GHz
- Coexistence challenges: incumbent satellite/radar users → sharing & sensing
- Signal processing angle: wider bandwidth + more antennas = heavier beam squint, calibration burden
- **Fig:** none (keep light); optional coverage-vs-capacity conceptual plot

### Slide 8 — mmWave: what a decade taught us [1 min]
- FR2 works — but blockage, hand/body loss (10–25 dB), and beam-management overhead limited rollout
- Dense small cells economically hard; FWA became the killer app
- Lesson 1: link budget math wins arguments; Lesson 2: beam training overhead is a *rate* tax
- These lessons directly shape sub-THz system design
- **Fig:** simple blockage/coverage cartoon (TikZ)

### Slide 9 — Sub-THz channels: 100–300 GHz [1.5 min]
- Spreading loss + **molecular absorption** (H₂O, O₂ resonances) → distance-selective bands
- **Eq:** PL(f,d) = (4πfd/c)² · e^{κ_abs(f)·d}; absorption peaks near 60, 119, 183, 325 GHz
- Channel is sparse, specular, LoS-dominated; scattering ↑ as λ → surface roughness
- Consequences: short links, pencil beams mandatory, favorable transmission windows (e.g., W-/D-band)
- **Fig:** atmospheric attenuation (dB/km) vs frequency curve, windows shaded

### Slide 10 — Hardware impairments dominate at high bands [1.5 min]
- PA efficiency collapses with frequency; back-off needed → PAPR becomes a first-class metric
- **Eq:** Rapp AM/AM g(A) = G·A / (1+(GA/A_sat)^{2p})^{1/2p}; Wiener phase noise φ[n+1]=φ[n]+w[n], w~N(0, σ²=4π²f_c²·c·T_s)
- Phase noise ∝ f_c² → ICI/CPE; low-resolution ADCs to save power → quantization-aware processing
- "Dirty RF" mindset: design the waveform *for* the hardware, not despite it
- **Fig:** PA AM/AM curve with back-off region marked

### Slide 11 — Implications for waveform design [1 min]
- Requirements matrix: low PAPR (PA), phase-noise robustness (oscillator), Doppler robustness (mobility), spectral confinement
- No single waveform wins on all axes → scenario-dependent choices likely in 6G
- CP-OFDM's weaknesses are exactly the axes that get worse at high bands
- Sets up Section 3
- **Fig:** requirements spider/radar chart (waveform axes)

---

## Section 3 — Waveforms Beyond OFDM (Slides 12–20, 10 min)

### Slide 12 — CP-OFDM recap: why it won 4G & 5G [1 min]
- **Eq:** x[n] = (1/√N) Σ_k X_k e^{j2πkn/N}; CP turns linear conv. → circular → 1-tap FDE
- MIMO-friendly, flexible numerology, mature ecosystem
- Implicit assumption: channel ≈ constant over one symbol (quasi-static)
- That assumption is what breaks next
- **Fig:** OFDM TX/RX block diagram (compact TikZ)

### Slide 13 — Where OFDM breaks: high Doppler & high bands [1 min]
- Doppler spread → subcarrier orthogonality lost → ICI
- **Eq:** ICI power bound P_ICI ≲ (π f_d T_s)²/3 (small normalized Doppler)
- 500 km/h @ 30 GHz → f_d ≈ 14 kHz; phase noise adds CPE+ICI on top
- High PAPR (~10–12 dB) forces PA back-off — worst possible fit for THz PAs
- **Fig:** ICI power vs normalized Doppler plot (generated)

### Slide 14 — DFT-s-OFDM and the single-carrier comeback [1 min]
- **Eq:** DFT spreading: X = F_M s before subcarrier mapping → quasi single-carrier envelope
- 3–4 dB PAPR advantage; already the 5G uplink workhorse
- Sub-THz proposals: SC-FDE with flexible block structure — equalizer complexity moves to RX
- Candidate for 6G high bands in 3GPP discussions
- **Fig:** PAPR CCDF comparison (OFDM vs DFT-s-OFDM, generated)

### Slide 15 — Filtered multicarrier: the 5G bake-off lessons [1 min]
- FBMC, UFMC, GFDM, f-OFDM: better spectral confinement, asynchronous access
- Why they lost in 2016: MIMO integration pain, complexity, marginal gains after windowing
- Surviving legacy: spectral shaping is now a TX implementation choice, not a standard
- Lesson: ecosystem inertia is a design constraint — radical waveforms need radical gains
- **Fig:** PSD comparison sketch (OFDM vs filtered variants)

### Slide 16 — OTFS I: thinking in delay–Doppler [1.5 min]
- Doubly selective channel: compact & quasi-stationary in delay–Doppler (DD) domain
- **Eq:** r(t) = ∬ h(τ,ν) s(t−τ) e^{j2πν(t−τ)} dτ dν — a few (τᵢ, νᵢ) taps
- Each DD symbol experiences the *whole* TF channel → full diversity potential
- Physical picture: DD taps = moving reflectors with fixed range/velocity
- **Fig:** side-by-side TF-grid (fast fading) vs DD-grid (sparse, static) heatmaps (generated)

### Slide 17 — OTFS II: transceiver structure [1.5 min]
- **Eq:** ISFFT X_tf[n,m] = (1/√(NM)) Σ_k Σ_l x[k,l] e^{j2π(nk/N − ml/M)}; RX: SFFT back to DD
- Interpretation: OTFS = 2D precoding over an entire OFDM frame
- Implementation: reuse OFDM modulator + pre/post-processing → attractive migration path
- Pilot design: single DD pilot with guard region → clean channel sounding
- **Fig:** **TikZ block diagram** — ISFFT → Heisenberg TX → channel → Wigner RX → SFFT

### Slide 18 — OTFS III: input–output relation & detection [1 min]
- **Eq:** y[k,l] ≈ Σᵢ hᵢ · x[(k−kᵢ) mod N, (l−lᵢ) mod M] · phase term (twisted convolution)
- 2D circular structure → message-passing / MMSE detectors exploit sparsity
- Cost: detection complexity & latency (frame-level processing); fractional Doppler leakage
- Status: strong academic results; not yet in 3GPP normative work — honest framing
- **Fig:** DD input-output convolution illustration

### Slide 19 — AFDM: the chirp-based challenger [1 min]
- Affine Frequency Division Multiplexing: multiplex on discrete affine Fourier (chirp) basis
- **Eq:** DAFT kernel φ_m[n] = (1/√N) e^{j2π(c₁n² + mn/N + c₂m²)}; tune c₁ to Doppler range
- Achieves full diversity in doubly dispersive channels with *1D* (single-symbol) processing
- Backward-compatible complexity (FFT-based); rising fast in literature since 2023
- **Fig:** DAFT-domain channel representation sketch

### Slide 20 — Waveform scorecard + ➤ Demo 1 pointer [1 min]
- Comparison table: CP-OFDM / DFT-s-OFDM / SC-FDE / OTFS / AFDM
- Axes: PAPR, Doppler robustness, complexity, MIMO maturity, standards readiness
- Takeaway: OFDM stays for low mobility; DD-domain designs own the high-mobility/ISAC corner
- **➤ LIVE DEMO 1 runs here (3.5 min):** "OFDM vs OTFS at 500 km/h — watch the BER floor appear"
- **Fig:** the comparison table (styled)

---

## Section 4 — Ultra-Massive MIMO & Beamforming (Slides 21–29, 10 min)

### Slide 21 — From massive to ultra-massive [1 min]
- 5G: 64 TRX at 3.5 GHz → 6G: 512–4096 elements at FR3/mmWave/sub-THz
- Same physical aperture at higher f → more elements, narrower beams, more EIRP
- New regimes: near-field propagation, spatial non-stationarity across the array
- Cost axis: RF chains, ADCs, calibration, fronthaul — DSP must economize
- **Fig:** array size / frequency scaling graphic

### Slide 22 — Near-field vs far-field [1.5 min]
- **Eq:** Rayleigh distance d_R = 2D²/λ; e.g., D = 0.5 m @ 30 GHz → d_R = 50 m — users are *inside* it
- Far-field: planar waves, steering vector a(θ); Near-field: spherical waves a(θ, r)
- Beam **focusing** (range-selective) vs beam steering — new DoF, new interference behavior
- Impacts codebooks, channel models, localization accuracy (curvature carries range info)
- **Fig:** TikZ: plane-wave vs spherical-wave geometry with d_R marked

### Slide 23 — Hybrid analog–digital architectures [1.5 min]
- Fully digital at 1024 elements ≈ power/cost prohibitive at high bands
- **Eq:** y = W_BB^H W_RF^H (H F_RF F_BB s + n); F_RF phase-only, |F_RF(i,j)| = 1/√N_t
- Fully connected vs partially connected (subarray) trade: gain vs #phase shifters
- Beam squint across wide bandwidth: true-time-delay units re-entering the toolbox
- **Fig:** **TikZ block diagram** — fully digital vs hybrid (fully/partially connected) side by side

### Slide 24 — Designing the hybrid precoder [1 min]
- Key insight: mmWave channels sparse in angle → precoding ≈ sparse reconstruction
- **Eq:** minimize ‖F_opt − F_RF F_BB‖_F s.t. F_RF from array-response dictionary → OMP (El Ayach et al.)
- Spectral efficiency: R = log₂|I + (ρ/N_s) W† H F F† H† W (W†W)^{-1}|
- Hybrid with N_RF ≈ N_s + a few chains ≈ near-digital performance in sparse channels
- **Fig:** SE vs SNR curves — digital vs OMP-hybrid vs analog (generated; mirrors Demo 2)

### Slide 25 — Beam management: finding the needle [1 min]
- 5G NR baseline: SSB beam sweep → CSI-RS refinement → beam tracking/recovery
- Overhead scales with codebook size → hierarchical & ML-assisted search for 6G
- Sub-THz: pencil beams → mobility & micro-blockage stress the loop hard
- Research: side-information beam prediction (position, camera, radar), near-field codebooks
- **Fig:** hierarchical codebook tree sketch

### Slide 26 — Cell-free massive MIMO [1 min]
- Many distributed low-cost APs, joint coherent processing, no cell boundaries
- Uniform SNR instead of cell-edge misery; macro-diversity against blockage
- The catches: fronthaul capacity, synchronization, scalable (DCC) processing
- 6G angle: natural platform for distributed sensing + RIS integration
- **Fig:** cellular vs cell-free topology cartoon (TikZ)

### Slide 27 — Channel estimation by compressed sensing [1 min]
- Angular-domain sparsity: H ≈ A_R diag(g) A_T^H with few paths
- **Eq:** y = Φ h + n, ‖h‖₀ = L ≪ dim → OMP/AMP recovery from O(L log N) pilots
- Pilot savings are what make ultra-massive arrays trainable at all
- Caveats: grid mismatch (off-grid methods), near-field dictionary growth
- **Fig:** sparse angular spectrum illustration

### Slide 28 — Pilot contamination [1 min]
- Finite coherence block → pilot reuse across cells → correlated estimates
- **Eq:** as M→∞, SINR → β²_jj / Σ_{l≠j} β²_jl — interference that *doesn't* average out
- Modern view (Björnson et al.): with multi-cell MMSE processing, capacity grows without bound — contamination is a processing artifact, not a law
- Mitigation: pilot assignment, spatial correlation exploitation, cell-free operation
- **Fig:** pilot-reuse geometry sketch

### Slide 29 — Open challenges + ➤ Demo 2 pointer [1 min]
- Wideband beam squint at 10%+ fractional bandwidth; TTD hybrid architectures
- Near-field codebook & CSI dimensionality; spatial non-stationarity
- Energy per beamformed bit as the real figure of merit
- **➤ LIVE DEMO 2 runs here (3.5 min):** "64-element array live — steer the beam, watch digital vs hybrid SE"
- **Fig:** none (text + teaser thumbnail)

---

## Section 5 — Reconfigurable Intelligent Surfaces (Slides 30–35, 6 min)

### Slide 30 — RIS: programming the channel itself [1 min]
- Passive metasurface, N sub-wavelength elements, electronically tunable reflection phase
- Paradigm shift: channel becomes a *controllable* variable, not just estimated
- Nearly-passive: no PA, no ADC per element → low power, low cost, conformal
- Control plane: low-rate link from BS configures phases
- **Fig:** **TikZ geometry** — BS → RIS → UE with blocked direct path, element zoom-in

### Slide 31 — The cascaded channel model [1 min]
- **Eq:** y = (h_r^H Θ G + h_d^H) x + n, Θ = diag(β₁e^{jθ₁}, …, β_N e^{jθ_N})
- Product (dyadic) path loss: PL ∝ (d₁d₂)^{-α} — the fundamental cost of passivity
- Estimation burden: cascaded h_r ⊙ G has N·M coefficients; structure to the rescue
- Far-field vs near-field RIS operation differ meaningfully at large N
- **Fig:** labeled channel diagram (reuse Slide 30 TikZ with symbols)

### Slide 32 — Phase optimization & the N² law [1.5 min]
- **Eq:** max_θ |h_d + Σ_n β_n e^{jθ_n} [h_r]_n [G]_n|² → closed form: θ_n = arg(h_d) − arg([h_r]_n[G]_n)
- Coherent combining: received power ∝ N² (amplitude ∝ N); random phases: ∝ N
- N² is per-*power*; ~6 dB per doubling of N — but squared against dyadic path loss
- Multi-user / MIMO case: non-convex → SDR, manifold optimization, alternating optimization
- **Fig:** SNR gain vs N (log-log) showing N vs N² slopes (generated; mirrors Demo 3)

### Slide 33 — Active RIS & other variants [1 min]
- Passive RIS gain often eaten by dyadic loss in practice → active RIS adds amplification (and noise)
- **Eq:** active model y = (h_r^H Θ G)x + h_r^H Θ n_RIS + n — amplified noise term is the tax
- Variants: STAR-RIS (transmit+reflect), beyond-diagonal RIS, holographic surfaces
- Trade study: active RIS vs simply deploying a relay/small cell — must be honest here
- **Fig:** passive vs active element schematic

### Slide 34 — Deployment: where RIS actually helps [1 min]
- Sweet spots: mmWave/sub-THz blockage bypass, indoor dead zones, localized capacity boost
- Placement matters: near TX or RX (not mid-path) to minimize dyadic loss
- Channel estimation & control overhead scale with N — the practical bottleneck
- Field trials (e.g., metro/industrial pilots) show promise; standardization still pre-normative
- **Fig:** deployment scenarios cartoon (3 vignettes)

### Slide 35 — RIS open problems + ➤ Demo 3 pointer [0.5 min]
- CSI acquisition without RF chains; wideband (frequency-flat phase) limitation
- RIS-aided sensing/localization synergy; EM-consistent (mutual-coupling) models
- **➤ LIVE DEMO 3 runs here (2.5 min):** "watch the N² law emerge from 16 to 1024 elements"
- **Fig:** none

---

## Section 6 — Integrated Sensing & Communication (Slides 36–42, 8 min)

### Slide 36 — Why ISAC [1 min]
- One spectrum, one infrastructure, two functions: comms + radar-like sensing
- Drivers: spectrum scarcity, cellular densification = ready-made sensor network, perception for XR/V2X/drones
- IMT-2030 lists ISAC as a *defining* 6G scenario (not an add-on)
- Spectrum reuse economics: sensing "for free" on comm waveforms
- **Fig:** ISAC application collage (V2X, drone, gesture, weather)

### Slide 37 — Radar refresher in one slide [1.5 min]
- **Eq:** delay τ = 2R/c (monostatic); Doppler f_D = 2v f_c/c; ambiguity function A(τ,ν) trade-offs
- Range resolution ΔR = c/2B — bandwidth buys resolution; velocity res. ∝ 1/(coherent time)
- Matched filtering & coherent integration = the SNR workhorses
- Audience calibration: this is all classic DSP — 6G reuses it wholesale
- **Fig:** range/Doppler resolution cheat-diagram

### Slide 38 — OFDM as a radar waveform [1.5 min]
- Sturm–Wiesbeck processing: divide RX symbol grid by known TX symbols → channel grid
- **Eq:** D[n,m] = Y[n,m]/X[n,m]; range profile via IFFT over subcarriers, Doppler via FFT over symbols
- Sidelobe behavior ~ periodogram; windowing trades resolution vs leakage
- Beauty: the *data payload itself* is the radar illumination — no dedicated waveform
- **Fig:** **TikZ block diagram** — ISAC receiver: comm branch + sensing branch from same ADC

### Slide 39 — Joint waveform design [1 min]
- Design axes: subcarrier/power allocation, dedicated sensing symbols vs data reuse, beampattern shaping
- Comm wants randomness (capacity); radar wants determinism (clean ambiguity) — inherent friction
- Approaches: weighted optimization, sensing-assisted comm (beam prediction from radar tracks)
- Random-data radar: recent theory quantifies the "data randomness penalty" on sensing
- **Fig:** design-space triangle (rate / range res. / hardware)

### Slide 40 — Fundamental limits: CRB vs rate [1 min]
- **Eq:** delay CRB var(τ̂) ≥ 1/(8π² β_rms² · SNR·N_obs) — RMS bandwidth is king
- CRB–rate trade-off region: the ISAC "capacity–distortion" picture
- Power/subcarrier split moves you along the boundary — no free lunch, but cheap lunches exist
- Waterfilling for rate ≠ waterfilling for sensing → compromise allocations
- **Fig:** rate vs CRB^{-1} trade-off curve (conceptual)

### Slide 41 — Monostatic, bistatic, and network sensing [1 min]
- Monostatic: full waveform knowledge, but TX–RX isolation / self-interference is brutal
- Bistatic (BS→UE or BS→BS): no self-interference, but sync & clock offsets bite
- Network/multistatic: fusion across cells → coverage + geometry diversity
- Cellular reality: OFDM numerology, duplexing, and scheduling constrain sensing design
- **Fig:** mono/bi/multi-static geometry sketch (TikZ)

### Slide 42 — ISAC in 3GPP + ➤ Demo 4 pointer [1 min]
- Rel-19: channel model for ISAC study (SA1 use cases → RAN1 modeling)
- Rel-20: 6G study phase — sensing among candidate features; ETSI ISG ISAC parallel track
- Honest status: pre-normative; first commercial sensing features likely network-based positioning++
- **➤ LIVE DEMO 4 runs here (3 min):** "two moving targets on a range–Doppler map — from a data-carrying OFDM frame"
- **Fig:** 3GPP timeline strip for ISAC milestones

---

## Section 7 — AI-Native Physical Layer (Slides 43–50, 8 min)

### Slide 43 — What "AI-native" actually means [1 min]
- 5G: AI bolted on (SON, scheduling); 6G ambition: AI as a *design principle* in the air interface
- Model deficit (no good math model: e.g., hardware nonlinearity) vs algorithm deficit (model known, optimal algo intractable)
- Learning helps most where models fail or complexity kills — not everywhere
- Spectrum of integration: block replacement → block co-design → end-to-end learned PHY
- **Fig:** taxonomy diagram: where ML slots into the PHY chain

### Slide 44 — Deep learning for channel estimation [1 min]
- Treat the pilot-grid channel estimate as a noisy image → CNN denoising/super-resolution
- Learned estimators approach MMSE performance *without* knowing channel statistics
- Gains largest at low SNR and under model mismatch; cost: training data & generalization
- This is Demo 5's exact setting (LS vs MMSE vs small NN)
- **Fig:** pilot grid → CNN → refined channel illustration

### Slide 45 — Autoencoder end-to-end PHY [1 min]
- O'Shea & Hoydis: TX-channel-RX as one autoencoder; learn constellation + demapper jointly
- Learned constellations rediscover & sometimes beat hand-designed ones under impairments
- Differentiable channel needed → surrogate models / RL for real channels
- Realism check: block-based systems won't vanish; hybrid learned blocks are the near-term path
- **Fig:** autoencoder PHY diagram with learned constellation inset

### Slide 46 — Neural receivers [1 min]
- Replace equalization+demapping with a trained network over the full RX grid
- Demonstrated: multi-user MIMO neural receivers within 3GPP-compatible frames (e.g., Sionna-class results)
- Robustness via training over channel distributions; complexity via quantization/pruning
- Deployment question: retraining cadence vs channel drift
- **Fig:** classic RX chain vs neural RX chain comparison

### Slide 47 — Model-based deep learning: deep unfolding [1.5 min]
- Middle path: unroll an iterative algorithm, learn its parameters (step sizes, thresholds)
- **Eq:** ISTA step x^{(k+1)} = η_λ(x^{(k)} + A^H(y − A x^{(k)})) → LISTA: learn (W₁, W₂, λ) per layer
- Orders-of-magnitude fewer iterations at same accuracy; retains interpretability & guarantees flavor
- PHY hits: unfolded detection, beamforming, channel estimation — best of both worlds
- **Fig:** iterative loop "unrolled" into layered network diagram

### Slide 48 — Semantic communications [1 min]
- Shift from bit fidelity to *task* fidelity: transmit meaning, reconstruct what matters
- JSCC neural codecs: graceful degradation, no cliff effect — image/speech demos compelling
- Open theory: semantic information measure, separation-theorem status, standardization interface
- Positioning: promising for constrained links (XR, satellite IoT), not a 6G day-one feature
- **Fig:** classic chain vs semantic chain diagram

### Slide 49 — The hard problems: data, generalization, trust [1 min]
- Dataset gap: channel data is vendor-siloed; sim-to-real transfer is the quiet blocker
- Generalization across cells/hardware/mobility; distribution shift monitoring
- Complexity/energy budget at the PHY timescale (µs inference); testability & certification
- Research opening: standardized channel datasets & benchmarks (a service to the field)
- **Fig:** none (discussion slide)

### Slide 50 — AI/ML in 3GPP + ➤ Demo 5 pointer [1 min]
- Rel-18 study → Rel-19: three use cases — CSI feedback compression, beam prediction, positioning
- Two-sided models (UE encoder + NW decoder): the interoperability puzzle
- 6G (Rel-20 study): AI-native candidate discussions; life-cycle management is the real spec work
- **➤ LIVE DEMO 5 runs here (2.5 min):** "a 3-layer network vs MMSE — watch NMSE curves cross"
- **Fig:** 3GPP AI/ML timeline strip

---

## Section 8 — Multiple Access & Spectrum Sharing (Slides 51–55, 5 min)

### Slide 51 — Beyond orthogonal access [1 min]
- OMA is optimal only in corner cases; 6G stress: massive connectivity + heterogeneous QoS
- Landscape: power-domain NOMA, code-domain (SCMA), RSMA, grant-free
- 5G reality check: MUST/NOMA studied, not widely deployed — why? (SIC complexity, gains modest)
- Framing: multiple access = interference *management* philosophy
- **Fig:** OMA vs NOMA vs RSMA resource cartoon

### Slide 52 — Power-domain NOMA & SIC [1 min]
- Superpose users in power; strong user cancels weak user's signal first
- **Eq:** R_far = log₂(1 + P₂|h_f|²/(P₁|h_f|² + σ²)), R_near = log₂(1 + P₁|h_n|²/σ²) after SIC
- Gains hinge on channel disparity; error propagation & CSI sensitivity are the taxes
- Degenerates poorly with mobility → motivates rate-splitting
- **Fig:** power-domain superposition + SIC decoding chain

### Slide 53 — Rate-Splitting Multiple Access [1.5 min]
- Split each user's message: common part (decoded by all) + private parts (SIC of common only)
- **Eq:** R_k = C_k + R_{p,k}; common rate min-shared: Σ C_k ≤ min_k log₂(1 + SINR_c,k)
- One framework spanning SDMA ↔ NOMA ↔ multicast as special cases
- Killer property: robustness to *imperfect CSIT* — degrees-of-freedom optimal
- **Fig:** RSMA TX/RX structure diagram (TikZ)

### Slide 54 — Grant-free & unsourced random access [1 min]
- mMTC regime: short packets, sporadic activity, no time for handshakes
- Activity detection = compressed sensing (sparse user activity); covariance-based detection at scale
- Unsourced RA: common codebook, decoder returns message list — new info-theoretic framing
- Connects back to CS math from Slide 27 — same tools, new problem
- **Fig:** sporadic-activity matrix sketch

### Slide 55 — Why RSMA is gaining traction for 6G [0.5 min]
- Unifies existing schemes + graceful CSIT degradation + synergy with ISAC/RIS beamforming
- Standardization outlook: candidate for 6G MIMO enhancements; complexity is the entry fee
- Takeaway line: "split, superpose, and let SIC do bounded work"
- **Fig:** none (summary slide)

---

## Section 9 — Coverage from the Sky & New Media (Slides 56–60, 4 min)

### Slide 56 — Non-terrestrial networks: the 3D architecture [1 min]
- Layers: LEO mega-constellations (300–1200 km), HAPS (~20 km), UAV relays
- 6G goal: one 3GPP-native fabric — same waveform family, seamless handover sky↔ground
- Direct-to-device is already real (satellite NR NTN); scaling it is the 6G task
- **Fig:** layered NTN architecture graphic (TikZ)

### Slide 57 — The LEO signal processing problem: Doppler [1 min]
- **Eq:** f_D(t) = (f_c/c)·v_rel(t); v_sat ≈ 7.6 km/s → up to ±25 ppm → ±50 kHz @ 2 GHz, ×10 at 20 GHz
- Doppler *rate* up to ~kHz/s → tracking loops stressed; long RTT (2–25 ms) breaks HARQ timing
- Fix: ephemeris-based pre-compensation (satellite position known!) + residual tracking
- OTFS/DD-domain designs are natural fits here — callback to Section 3
- **Fig:** Doppler profile over a LEO pass (generated curve)

### Slide 58 — NTN in 3GPP [0.5 min]
- Rel-17: NR-NTN transparent payload baseline; Rel-18/19: coverage, mobility, regenerative payloads
- 6G: NTN native from day one (not retrofitted) — ISL routing, store-and-forward IoT
- **Fig:** small timeline strip

### Slide 59 — Optical wireless & VLC [1 min]
- IM/DD constraint: real, non-negative signals → DCO-/ACO-OFDM adaptations
- LiFi: dense indoor capacity, security by physics; FSO backhaul for terrestrial/NTN links
- Challenges: alignment, ambient light, uplink asymmetry
- Niche but real: industrial, aircraft cabins, RF-denied environments
- **Fig:** VLC downlink scenario sketch

### Slide 60 — Quantum-secured links (brief) [0.5 min]
- QKD: key distribution with physics-based security guarantees; terrestrial fiber + satellite demos
- Realism: point-to-point, low key rates → hybrid with PQC (post-quantum crypto) is the practical path
- For 6G: security architecture topic more than PHY DSP topic — one slide, honest scope
- **Fig:** none

---

## Section 10 — Energy, Standardization & Roadmap (Slides 61–65, 4 min)

### Slide 61 — Energy-efficient PHY design [1 min]
- Network energy is an OPEX + sustainability headline KPI for 6G (IMT-2030 design value)
- **Eq:** η_EE = R/P_total; PA efficiency + ADC power P_ADC ∝ 2^b·f_s dominate at high bands
- Levers: low-resolution ADCs, sleep-mode-aware waveforms (light sleep between bursts), lean pilots/always-on signal reduction
- Design shift: bits/Joule as a first-class metric next to bits/s/Hz
- **Fig:** energy breakdown bar chart (conceptual)

### Slide 62 — 3GPP release timeline to 6G [1 min]
- Rel-18 (5G-Advanced, frozen 2024): AI/ML study, NTN+, RedCap+
- Rel-19 (2025–26): ISAC channel model, AI/ML normative first steps
- Rel-20 (from ~2025): 6G *study* phase; Rel-21: 6G normative → first spec ~2028–29
- Reading guide: how to track TDocs/TRs without drowning (TR 38.xxx pointers)
- **Fig:** release timeline graphic (TikZ)

### Slide 63 — ITU IMT-2030 process [1 min]
- M.2160 framework (2023) → requirements & evaluation methodology (2024–26) → submissions → IMT-2030 specs ~2029–30
- History rhymes: same machinery that turned IMT-2020 into 5G
- Regional programs feeding in: Hexa-X-II (EU), Next G Alliance (US), IMT-2030 promotion group (CN), Bharat 6G (IN)
- **Fig:** ITU process funnel timeline

### Slide 64 — A research roadmap for the room [0.5 min]
- Near-term (papers now): DD-domain receivers, near-field CSI, ISAC waveform trade-offs, unfolded algorithms
- Medium: cell-free + RIS field studies, AI life-cycle management, sub-THz prototyping
- Choose problems where DSP insight beats brute-force learning — comparative advantage
- **Fig:** 2×3 roadmap grid (topic × horizon)

### Slide 65 — The 6G signal-processing map (section wrap) [0.5 min]
- One-slide synthesis: spectrum → waveform → arrays → surfaces → sensing → learning, one pipeline
- Recurring themes: sparsity, domain transforms, hardware-aware design, model+data hybrids
- **Fig:** the talk-roadmap graphic from Slide 5, now annotated with key equations

---

## Section 11 — Demo Recap, Takeaways & Q&A (Slides 66–70, 2 min)

*(Demos already ran interleaved after Sections 3–7; this section closes the loop.)*

### Slide 66 — Five demos, five lessons [0.5 min]
- One-line recap per demo: what we saw and the formula it demonstrated
- D1: DD-domain beats TF at high Doppler · D2: 4 RF chains ≈ 64 · D3: N² is real · D4: data frames can sense · D5: learned ≈ MMSE without statistics
- Fallback note: pre-computed versions live in appendix A1–A5
- **Fig:** 5 thumbnail strip (from `figures/demo_backups/`)

### Slide 67 — Key takeaways [1 min]
- 6G = new spectrum + new geometry (near-field) + new functions (sensing) + new tools (learning)
- OFDM is not dead; it has new roommates — scenario-adaptive PHY is the theme
- The N², the d_R = 2D²/λ, and the CRB: three formulas that organize half the field
- Signal processing remains the discipline that turns physics into throughput
- **Fig:** none (big-type slide)

### Slide 68 — Open problems worth a PhD [0.5 min]
- Curated list (6–8 items) mapped to sections: DD-ISAC unification, near-field estimation, EM-consistent RIS models, trustworthy neural PHY, energy-optimal waveforms
- Each tagged with "entry cost" (toolbox needed) — actionable for the scholars in the room
- **Fig:** none

### Slide 69 — References & resources [0.5 min]
- 12–15 IEEE-style key references (surveys: 6G vision, OTFS, RIS, ISAC, AI-PHY; ITU M.2160)
- Tooling pointers: MATLAB toolboxes used, Sionna, open channel datasets
- Split across 2 visual columns; full list also in the handout
- **Fig:** none (reference list)

### Slide 70 — Thank you / contact / Q&A [—]
- Contact details, slides+code link (QR), invitation to collaborate
- Q&A buffer begins (~5 min)
- **Fig:** closing visual

---

## Appendix (not counted in the 70)

- **A1–A5 — "Backup: pre-computed result" slides**, one per demo: the exact final figure(s) each demo produces, from `figures/demo_backups/`, with a one-line result summary — used only if MATLAB fails on stage.

---

## Figure & equation inventory (for build phase)

**TikZ (native) diagrams:** OTFS transceiver (S17), hybrid beamforming architectures (S23), RIS geometry (S30/31), ISAC receiver (S38), plus light cartoons (S8, S22, S26, S41, S53, S56, S62).
**Generated (matplotlib → PNG, shared with PPTX):** timeline (S2), KPI table styling (S4), absorption curve (S9), PA curve (S10), ICI-vs-Doppler (S13), PAPR CCDF (S14), TF-vs-DD grids (S16), SE curves (S24), N² law (S32), rate-CRB (S40), LEO Doppler (S57), plus all demo output figures.
**Key equations:** molecular-absorption path loss, Rapp AM/AM, Wiener phase noise, OFDM/ICI, ISFFT/SFFT + DD I/O, DAFT, Rayleigh distance, hybrid BF model + OMP objective, CS model, pilot-contamination SINR, RIS cascaded model + optimal phases, radar delay/Doppler, OFDM-radar periodogram, delay CRB, NOMA SIC rates, RSMA rates, LEO Doppler, energy efficiency.
