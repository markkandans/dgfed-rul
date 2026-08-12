"""Slide content for the 6G PowerPoint deck — mirrors the Beamer deck 1:1.

Each slide is a dict. `kind`: title | section | content | standout | backup.
`layout` (content only): bullets | bullets_img | img_bullets | eq_bullets |
eq_bullets_img | img | table.
`eq`: list of (name, latex) rendered to PNG by latex_render.eq.
`tikz`: a beamer/tikz/*.tex filename rendered by latex_render.tikz.
`img`: filename in ../figures/ (or figures/demo_backups/).
`demo`: banner text for a "live demo runs here" accent box.
`notes`: speaker notes (mirror of the Beamer \\note{}).
"""

TITLE = "Signal Processing for Beyond-5G and 6G Communications"
SUBTITLE = "Waveforms  •  ultra-massive MIMO  •  RIS  •  ISAC  •  AI-native PHY"
AUTHOR = "Dr. Markkandan S  ·  Associate Professor"
INSTITUTE = ("School of Electronics Engineering, "
             "Vellore Institute of Technology, Chennai  ·  markkandan.s@vit.ac.in")
DATE = "Invited talk  •  90 minutes  •  2026"

SLIDES = [
    # ============================ TITLE ============================
    dict(kind="title", title=TITLE, subtitle=SUBTITLE, author=AUTHOR,
         institute=INSTITUTE, date=DATE,
         notes="Welcome; hook: 6G is, at its core, a signal processing problem. "
               "Five live MATLAB experiments are woven through the talk. Slides "
               "and code available at the end."),

    # ===================== 1. OPENING & MOTIVATION =====================
    dict(kind="section", title="1 · Opening & Motivation"),
    dict(kind="content", layout="img", title="Six generations in forty years",
         img="fig_evolution_timeline.png",
         bullets=["Each decade: a new generation, a 10–100× peak-rate jump",
                  "The differentiator each time was the physical-layer signal "
                  "processing choice: FDMA → TDMA → CDMA → OFDM/MIMO → mMIMO"],
         notes="Walk the timeline left to right; generations are remembered by "
               "their PHY (3G=CDMA, 4G=OFDM+MIMO). The 6G research window is open "
               "now: ITU framework 2023, 3GPP study underway, spec by ~2029."),
    dict(kind="content", layout="bullets",
         title="The IMT-2030 vision (ITU-R M.2160, Nov. 2023)",
         bullets=["Extended from 5G: immersive comm.; hyper-reliable low-latency; "
                  "massive communication",
                  "Genuinely new for 6G: Integrated Sensing & Communication; "
                  "AI and communication; ubiquitous connectivity",
                  "Design values: sustainability, security & resilience, "
                  "connecting the unconnected, interoperability"],
         notes="M.2160 is the official 'what is 6G' document. Three scenarios are "
               "upgrades of the 5G triangle; three are new. Two of the new ones "
               "(ISAC, AI) are Sections 6 and 7 — both signal processing problems."),
    dict(kind="content", layout="table", title="KPI targets: IMT-2020 vs IMT-2030",
         table=dict(headers=["KPI", "5G (IMT-2020)", "6G (IMT-2030, research)"],
                    rows=[["Peak data rate", "20 Gb/s", "200 Gb/s – 1 Tb/s"],
                          ["User-plane latency", "1 ms", "0.1 – 1 ms"],
                          ["Connection density", "10⁶ /km²", "10⁶ – 10⁸ /km²"],
                          ["Positioning", "m-level", "cm-level (+ velocity)"],
                          ["Sensing", "—", "native KPI class"],
                          ["Energy", "qualitative", "first-class design value"]]),
         bullets=["IMT-2030 gives ranges, not single numbers — targets are "
                  "scenario-dependent"],
         notes="Highlight three rows: 10× peak rate needs new spectrum (Sec 2); "
               "sensing appears as a KPI class for the first time (Sec 6); energy "
               "moves from marketing to KPI (Sec 10). Don't quote single-number 6G KPIs."),
    dict(kind="content", layout="img",
         title="Why signal processing is the bottleneck and the enabler",
         img="fig_roadmap.png",
         bullets=["Near Shannon at sub-6 GHz → gains must come from new dimensions",
                  "New dimensions: bandwidth (THz), aperture (arrays), environment "
                  "(RIS), function (sensing), semantics (AI)",
                  "Hardware gets worse as frequency rises — DSP must compensate"],
         notes="The thesis slide. Every box on this roadmap is a DSP problem in a "
               "systems costume. The D1–D5 dots: five live MATLAB experiments, one "
               "after each core section."),

    # ===================== 2. SPECTRUM FRONTIERS =====================
    dict(kind="section", title="2 · New Spectrum Frontiers"),
    dict(kind="content", layout="img", title="The 6G spectrum landscape",
         img="fig_spectrum_landscape.png",
         bullets=["Sub-6: coverage workhorse, congested • FR2 mmWave: deployed, niche",
                  "FR3 (7–24 GHz): the pragmatic 6G capacity band; WRC-23 identified "
                  "new IMT bands (region-dependent)",
                  "Sub-THz 100–300 GHz: the research frontier"],
         notes="Orient on the log axis. 6G is NOT just THz — first commercial 6G "
               "capacity most likely comes from FR3. Keep sub-THz honest: research "
               "frontier, short links."),
    dict(kind="content", layout="bullets",
         title="FR3 / upper mid-band: the pragmatic 6G band",
         bullets=["7–15 GHz: 2–4× more bandwidth than C-band with manageable path loss",
                  "Same aperture → 4–9× more elements than at 3.5 GHz: massive MIMO "
                  "scales naturally",
                  "Coexistence with satellite/radar incumbents → sharing and sensing",
                  "DSP price: beam squint, calibration, channel-estimation burden"],
         notes="Operators love FR3: reuse the macro grid. Element count scales with "
               "wavelength, so the same panel holds an order of magnitude more "
               "elements. Foreshadows Section 4."),
    dict(kind="content", layout="bullets", title="mmWave: what a decade taught us",
         bullets=["FR2 works — but blockage (hand/body 10–25 dB), dense small "
                  "cells, beam-management overhead limited rollout",
                  "Killer app became fixed wireless access, not mobility",
                  "Lesson 1: link-budget math wins arguments",
                  "Lesson 2: beam training overhead is a rate tax"],
         notes="mmWave is not a failure, a recalibration. The two lessons are design "
               "constraints for everything that follows; sub-THz inherits both, "
               "amplified. A hand on the phone can erase 20 dB."),
    dict(kind="content", layout="eq_bullets_img", title="Sub-THz channels: 100–300 GHz",
         eq=[("eq_thz_pl",
              r"\mathrm{PL}(f,d)=\underbrace{\left(\tfrac{4\pi f d}{c}\right)^{2}}_{\text{spreading}}"
              r"\cdot\underbrace{e^{\kappa_{\mathrm{abs}}(f)\,d}}_{\text{molecular abs.}}")],
         img="fig_thz_absorption.png",
         bullets=["O₂/H₂O resonances at 60, 119, 183, 325 GHz carve transmission windows",
                  "Channel: sparse, specular, LoS-dominated",
                  "Consequences: short links, pencil beams mandatory"],
         notes="One equation to remember: spreading grows with f² at fixed aperture, "
               "and the exponential absorption term is frequency-selective. W/D/G "
               "windows are where sub-THz will live. Sparsity is good news for "
               "compressed sensing later."),
    dict(kind="content", layout="eq_bullets_img",
         title="Hardware impairments dominate at high bands",
         eq=[("eq_rapp",
              r"g(A)=\frac{G\,A}{\left[1+\left(\frac{GA}{A_{\mathrm{sat}}}\right)^{2p}\right]^{1/2p}}"),
             ("eq_wiener",
              r"\varphi[n{+}1]=\varphi[n]+w[n],\;\; w\sim\mathcal N\!\left(0,\,4\pi^{2}f_c^{2}c\,T_s\right)")],
         img="fig_pa_rapp.png",
         bullets=["PA efficiency falls with f; back-off → PAPR is a first-class metric",
                  "Phase noise power ∝ f_c²; low-resolution ADCs to save power"],
         notes="'Dirty RF' mindset: at 140 GHz the waveform must be designed FOR the "
               "hardware. Two knobs: PAPR (PA back-off, coverage) and phase-noise "
               "robustness (subcarrier spacing / single-carrier). Bridge to waveforms."),
    dict(kind="content", layout="table", title="Implications for waveform design",
         table=dict(headers=["Requirement", "sub-6", "FR3", "mmWave", "sub-THz"],
                    rows=[["Low PAPR", "nice", "nice", "want", "NEED"],
                          ["Phase-noise robustness", "—", "—", "want", "NEED"],
                          ["Doppler robustness", "HST", "HST", "want", "want"],
                          ["Spectral confinement", "want", "want", "nice", "nice"],
                          ["MIMO compatibility", "NEED", "NEED", "NEED", "want"]]),
         bullets=["No single waveform wins every column → expect scenario-dependent "
                  "waveform choices",
                  "CP-OFDM's weak spots are exactly the columns that harden at high bands"],
         notes="Read column-wise: the further right, the more requirements shift "
               "toward PAPR and phase noise, where OFDM is weakest. Transition to "
               "Section 3."),

    # ===================== 3. WAVEFORMS =====================
    dict(kind="section", title="3 · Waveforms Beyond OFDM"),
    dict(kind="content", layout="eq_bullets",
         title="CP-OFDM recap: why it won 4G and 5G",
         eq=[("eq_ofdm",
              r"x[n]=\frac{1}{\sqrt N}\sum_{k=0}^{N-1}X_k\,e^{j2\pi kn/N},\quad"
              r"\text{CP: linear}\to\text{circular conv.}\to\text{1-tap FDE}")],
         bullets=["One FFT turns a frequency-selective channel into N flat channels",
                  "MIMO-friendly, flexible numerology, gigantic ecosystem",
                  "Hidden assumption: channel constant over one symbol (quasi-static)",
                  "That assumption is what high mobility and high carriers break"],
         notes="Refresher framed as 'what did we sign up for?' The CP-makes-it-"
               "circular trick is the whole magic; it costs 7–25% overhead. The "
               "one-tap equalizer only exists if the channel sits still for a symbol."),
    dict(kind="content", layout="eq_bullets_img",
         title="Where OFDM breaks: high Doppler, high bands",
         eq=[("eq_ici", r"P_{\mathrm{ICI}}\;\lesssim\;\frac{(\pi f_d T_s)^{2}}{3}")],
         img="fig_ici_doppler.png",
         bullets=["Doppler spread destroys orthogonality → ICI",
                  "500 km/h at 28 GHz: f_d ≈ 13 kHz (ε ≈ 0.11)",
                  "PAPR ~10–12 dB → PA back-off, worst fit for THz PAs",
                  "Phase noise adds CPE + ICI on top"],
         notes="ICI grows with the square of normalized Doppler; the pink marker is "
               "the 500 km/h working point — an SINR ceiling near 17 dB no matter the "
               "power. That ceiling becomes the BER floor in Demo 1."),
    dict(kind="content", layout="eq_bullets_img",
         title="DFT-s-OFDM and the single-carrier comeback",
         eq=[("eq_dfts", r"\mathbf X = F_M\,\mathbf s \quad\text{(DFT spread)}")],
         img="fig_papr_ccdf.png",
         bullets=["Quasi single-carrier envelope: ~3 dB PAPR advantage",
                  "Already the 5G uplink workhorse — proven at scale",
                  "Sub-THz proposals: SC-FDE; equalizer complexity moves to RX",
                  "Leading candidate for 6G high bands"],
         notes="CCDF plot is simulated (QPSK, 1200 tones). ~3 dB less back-off "
               "translates almost 1:1 into transmit power and link range at THz. "
               "The single-carrier vs multicarrier war is back."),
    dict(kind="content", layout="bullets",
         title="Filtered multicarrier: lessons of the 5G bake-off",
         bullets=["Candidates c.2016: FBMC, UFMC, GFDM, f-OFDM — better spectral "
                  "confinement, relaxed synchronicity",
                  "Why they lost: MIMO integration pain, complexity, marginal gains "
                  "after windowing",
                  "What survived: spectral shaping as a TX implementation choice",
                  "Meta-lesson: ecosystem inertia is a design constraint — radical "
                  "waveforms need radical gains"],
         notes="Flex slide — compress to 20 s if behind (say only the meta-lesson). "
               "OTFS/AFDM must enable something OFDM fundamentally cannot: the "
               "high-Doppler regime, not just a prettier PSD."),
    dict(kind="content", layout="eq_bullets_img",
         title="OTFS I: thinking in delay–Doppler",
         eq=[("eq_otfs_rt",
              r"r(t)=\iint h(\tau,\nu)\,s(t-\tau)\,e^{j2\pi\nu(t-\tau)}\,d\tau\,d\nu")],
         img="fig_tf_vs_dd.png",
         bullets=["In delay–Doppler the channel is sparse and quasi-static: a few "
                  "(τ,ν) taps = physical reflectors with range & velocity",
                  "Each DD symbol rides the entire TF channel → full-diversity potential"],
         notes="Domain-change story with our own simulation: left, TF response "
               "(fading everywhere); right, the SAME channel in DD (a few still "
               "taps). TF is the weather; DD is the map of what causes it."),
    dict(kind="content", layout="eq_bullets", tikz="otfs_chain.tex",
         title="OTFS II: transceiver structure",
         eq=[("eq_isfft",
              r"X_{\mathrm{tf}}[n,m]=\tfrac{1}{\sqrt{NM}}\sum_{k=0}^{N-1}\sum_{l=0}^{M-1}"
              r"x[k,l]\,e^{\,j2\pi\left(\frac{nk}{N}-\frac{ml}{M}\right)}\quad(\text{ISFFT})")],
         bullets=["OTFS = 2D pre/post-processing around an OFDM modem → attractive "
                  "migration path"],
         notes="Walk the chain: ISFFT spreads every DD symbol over the whole TF "
               "frame; Heisenberg transform is the OFDM modulator in disguise; RX "
               "undoes both. No exotic hardware, an extra 2D FFT pair. Pilots: a "
               "single DD impulse with a guard box sounds the whole channel."),
    dict(kind="content", layout="eq_bullets",
         title="OTFS III: input–output relation and detection",
         eq=[("eq_otfs_io",
              r"y[k,l]\;\approx\;\sum_{i}h_i\;x\!\left[(k-k_i)_N,\,(l-l_i)_M\right]"
              r"e^{j2\pi\phi_i}\;+\;w[k,l]")],
         bullets=["A 2D twisted circular convolution: each tap shifts data in delay "
                  "and Doppler and adds a phase",
                  "Sparsity → message-passing / low-complexity MMSE detectors",
                  "Costs: frame-level latency, detection complexity, fractional-"
                  "Doppler leakage",
                  "Honest status: rich literature, strong results — not yet in 3GPP "
                  "normative work"],
         notes="OFDM's one-tap story upgraded to 2D: a small set of shifts of the "
               "whole grid. Detection is where OTFS pays its bill. Keep the standards "
               "status honest; it pays off in Q&A."),
    dict(kind="content", layout="eq_bullets",
         title="AFDM: the chirp-based challenger",
         eq=[("eq_afdm",
              r"\phi_m[n]=\tfrac{1}{\sqrt N}\,e^{\,j2\pi\left(c_1 n^{2}+\frac{mn}{N}+c_2 m^{2}\right)}"
              r"\quad(\text{discrete affine Fourier basis})")],
         bullets=["Multiplex on chirps; tune c₁ to the Doppler span → all paths "
                  "separate in the DAFT domain",
                  "Full diversity with 1D single-symbol processing (vs OTFS frame-level)",
                  "FFT-based implementation; rising fast since 2023",
                  "Open: MIMO integration, pilot design, robustness at scale"],
         notes="AFDM gets OTFS-like diversity with lower latency because it works "
               "symbol-by-symbol. The chirp parameter is matched to max Doppler — "
               "channel-aware basis design. Keep-sentence: same benefit, smaller "
               "transceiver reorganization."),
    dict(kind="content", layout="img", title="Waveform scorecard",
         img="fig_waveform_scorecard.png",
         demo="▶  Live Demo 1 (3.5 min): OFDM vs OTFS at 500 km/h — watch the BER "
              "floor appear.  [matlab/demo1_ofdm_vs_otfs]",
         notes="OFDM keeps the low-mobility mainstream; DD-domain waveforms own high "
               "mobility and pair with sensing. THEN SWITCH TO MATLAB. Recall the ICI "
               "ceiling, predict the floor, let the plot confirm. Expected: OFDM "
               "floors ~3e-2, OTFS falls past 1e-4. Fail → backup A1. Done by 0:26:30."),

    # ===================== 4. ULTRA-MASSIVE MIMO =====================
    dict(kind="section", title="4 · Ultra-Massive MIMO & Beamforming"),
    dict(kind="content", layout="bullets", title="From massive to ultra-massive",
         bullets=["5G: 64 TRX at 3.5 GHz → 6G: 512–4096 elements at FR3/mmWave/sub-THz",
                  "Same aperture at higher f → more elements, narrower beams, more EIRP",
                  "New physics: near-field propagation, spatial non-stationarity",
                  "The bill: RF chains, ADCs, calibration, fronthaul — DSP must economize"],
         notes="Re-entry after Demo 1: from time-frequency games to space. Scaling is "
               "driven by aperture reuse. Every gain has a hardware price; the DSP "
               "refuses to pay full retail."),
    dict(kind="content", layout="eq_bullets", title="Near-field vs far-field",
         eq=[("eq_rayleigh",
              r"d_R=\frac{2D^{2}}{\lambda}\qquad\begin{cases} d>d_R: & \text{planar, }\mathbf a(\theta)\\[2pt]"
              r" d<d_R: & \text{spherical, }\mathbf a(\theta,r)\end{cases}")],
         bullets=["D = 0.5 m at 30 GHz: d_R = 50 m — users are inside the near field",
                  "Near field → beam focusing (range-selective!), not just steering",
                  "Wavefront curvature carries range info — a gift for localization"],
         notes="Everyone learned d_R once and forgot it because it used to be "
               "centimeters. Recompute live: half-meter array, 30 GHz, 50 m — the "
               "cell IS the near field. Beam focusing separates two users on the same "
               "bearing at different ranges: a new spatial DoF."),
    dict(kind="content", layout="eq_bullets", tikz="hybrid_bf.tex",
         title="Hybrid analog–digital architectures",
         eq=[("eq_hybrid",
              r"y = W_{\mathrm{BB}}^{H}W_{\mathrm{RF}}^{H}\left(H F_{\mathrm{RF}}F_{\mathrm{BB}}\,s + n\right),"
              r"\quad |[F_{\mathrm{RF}}]_{ij}|=1/\sqrt{N_t}")],
         bullets=["Phase-only RF network; wideband arrays add true-time-delay units "
                  "against beam squint"],
         notes="Left: the fully digital ideal (an ADC/DAC pair per element, "
               "unaffordable at 1024). Right: the hybrid compromise — thin digital "
               "layer + cheap analog phases. The interesting constraint: RF entries "
               "are unit-modulus. Subarray variant trades gain for phase-shifter count."),
    dict(kind="content", layout="eq_bullets_img",
         title="Designing the hybrid precoder: sparsity to the rescue",
         eq=[("eq_omp",
              r"\min_{F_{\mathrm{RF}},F_{\mathrm{BB}}}\left\|F_{\mathrm{opt}}-F_{\mathrm{RF}}F_{\mathrm{BB}}\right\|_F"
              r"\;\;\text{s.t.}\;\;F_{\mathrm{RF}}\in\{\text{array responses}\}")],
         img="fig_hybrid_se.png",
         bullets=["mmWave channels sparse in angle → precoding ≈ sparse reconstruction "
                  "→ OMP (El Ayach et al. 2014)",
                  "N_RF ≈ N_s chains already ≈ near-digital performance"],
         notes="Curves are our own simulation (Demo 2 code): 64×16, 6 paths, 4 "
               "streams — 4-RF-chain OMP hybrid within a fraction of a bit of fully "
               "digital. The channel only has ~6 directions worth talking to."),
    dict(kind="content", layout="bullets", title="Beam management: finding the needle",
         bullets=["5G NR baseline: SSB sweep → CSI-RS refinement → tracking & recovery",
                  "Overhead grows with codebook size → hierarchical search, ML prediction",
                  "Sub-THz pencil beams: mobility and micro-blockage stress the loop",
                  "Research: side-information beams (position, vision, radar), "
                  "near-field codebooks (angle × range)"],
         notes="Beam management is where array theory meets protocol reality: every "
               "training symbol is a symbol not carrying data (mmWave Lesson 2). The "
               "6G twist: near-field codebooks sample angle AND range."),
    dict(kind="content", layout="bullets", title="Cell-free massive MIMO",
         bullets=["Many distributed low-cost APs, coherent joint processing, no cells",
                  "Uniform SNR replaces cell-edge misery; macro-diversity beats blockage",
                  "Catches: fronthaul, synchronization, scalable processing (DCC)",
                  "6G angle: natural platform for distributed sensing and RIS integration"],
         notes="Pitch: instead of a few big towers owning users, many small APs serve "
               "everyone. The 90-percentile user wins. Research lives in the "
               "'catches': scalable combining and phase sync over fronthaul."),
    dict(kind="content", layout="eq_bullets",
         title="Channel estimation by compressed sensing",
         eq=[("eq_cs",
              r"\mathbf y=\Phi\,\mathbf h+\mathbf n,\quad \|\mathbf h\|_0=L\ll\dim(\mathbf h),"
              r"\quad H\approx A_R\,\mathrm{diag}(\mathbf g)\,A_T^{H}")],
         bullets=["Angular sparsity (L paths) → recovery from O(L log N) pilots via OMP/AMP",
                  "Pilot savings make 1024-element arrays trainable at all",
                  "Caveats: grid mismatch (off-grid), near-field dictionaries grow",
                  "Same math returns in Section 8 for activity detection"],
         notes="Connect to S9: physics gave sparsity, CS cashes it in. 64 paths of "
               "unknowns in a 1024-vector need a few hundred, not a few thousand, "
               "measurements. Off-grid is a good student-project generator."),
    dict(kind="content", layout="eq_bullets", title="Pilot contamination",
         eq=[("eq_pilot",
              r"\mathrm{SINR}_j\;\xrightarrow{\;M\to\infty\;}\;\frac{\beta_{jj}^{2}}{\sum_{l\neq j}\beta_{jl}^{2}}"
              r"\qquad(\text{same-pilot cells }l)")],
         bullets=["Pilot reuse → correlated estimates → coherent interference that "
                  "does NOT average out with more antennas",
                  "Modern view (Björnson et al.): with multi-cell MMSE + spatial "
                  "correlation, capacity grows without bound — a processing artifact",
                  "Mitigations: pilot assignment, correlation-aware estimation, cell-free"],
         notes="Two-act story: 2010 the asymptotic ceiling (most-cited limit); 2018 "
               "the ceiling dissolves under MMSE with unequal spatial correlations. "
               "'Fundamental limits' sometimes encode assumptions; better DSP removes them."),
    dict(kind="content", layout="bullets", title="Array frontier: open challenges",
         bullets=["Wideband beam squint at 10%+ fractional bandwidth: TTD-augmented hybrids",
                  "Near-field CSI: dimensionality, codebooks, tracking",
                  "Spatial non-stationarity: subarrays see different channels",
                  "The honest metric: energy per beamformed bit, not array gain"],
         demo="▶  Live Demo 2 (3.5 min): 64-element array — steer the beam with a "
              "slider; digital vs OMP-hybrid SE.  [matlab/demo2_hybrid_beamforming]",
         notes="Quick pass, then SWITCH TO MATLAB. Move the slider, the beam follows; "
               "grating-lobe moment beyond 60°. Then the SE bars: 4 chains vs 64. "
               "Fail → backup A2. Done by 0:40."),

    # ===================== 5. RIS =====================
    dict(kind="section", title="5 · Reconfigurable Intelligent Surfaces"),
    dict(kind="content", layout="img", tikz="ris_geometry.tex",
         title="RIS: programming the channel itself",
         bullets=["Passive metasurface, N tunable elements adding a controllable "
                  "reflection phase; steered by a low-rate control link",
                  "Paradigm shift: the channel becomes a design variable"],
         notes="For a century the channel was fate — estimate and adapt. A RIS makes "
               "part of the environment a design variable: hundreds of passive "
               "elements, each adding a controllable phase. No PAs, no ADCs on the panel."),
    dict(kind="content", layout="eq_bullets", title="The cascaded channel model",
         eq=[("eq_ris_casc",
              r"y=\left(\bm h_r^{H}\,\Theta\,\bm G+h_d^{H}\right)x+n,\quad"
              r"\Theta=\mathrm{diag}\!\left(\beta_1 e^{j\theta_1},\dots,\beta_N e^{j\theta_N}\right)")],
         bullets=["Product path loss ∝ (d₁ d₂)^(−α): the fundamental tax of passivity",
                  "Estimation burden: cascaded coefficients scale as N×M; structure helps",
                  "Large N at short range → the RIS itself operates in the near field"],
         notes="Deceptively simple; two hard truths under it: dyadic path loss (why "
               "placement matters) and the estimation burden (the panel has no "
               "receivers). Both are active research veins."),
    dict(kind="content", layout="eq_bullets_img",
         title="Phase optimization and the N² law",
         eq=[("eq_ris_phase",
              r"\theta_n^{\star}=\arg(h_d)-\arg\!\left([\bm h_r]_n^{*}[\bm G]_n\right)"
              r"\;\Rightarrow\; P_{\mathrm{rx}}\propto\Big(\textstyle\sum_n |[\bm h_r]_n||[\bm G]_n|\Big)^{2}\sim N^{2}")],
         img="fig_demo3_ris_scaling.png",
         bullets=["Co-phasing: amplitude ∝ N → power ∝ N² (+6 dB per doubling)",
                  "Random phases: 2D random walk → power ∝ N",
                  "Multi-user/MIMO: non-convex → SDR, manifold, alternating optimization"],
         notes="Derive in one breath: single-user SNR max separates per element; each "
               "element cancels its cascade phase. Plot has the analytic overlays: "
               "slopes 2.0 and 1.0. The N² rides on top of the dyadic loss — Demo 3."),
    dict(kind="content", layout="eq_bullets", title="Active RIS and other variants",
         eq=[("eq_ris_active",
              r"y=\left(\bm h_r^{H}\Theta\,\bm G\right)x+\underbrace{\bm h_r^{H}\Theta\,\bm n_{\mathrm{RIS}}}_{\text{amplified noise}}+n")],
         bullets=["Passive gain often eaten by dyadic loss → active RIS: amplification "
                  "+ an amplified-noise tax",
                  "Variants: STAR-RIS (transmit + reflect), beyond-diagonal RIS, "
                  "holographic surfaces",
                  "The uncomfortable benchmark: does it beat a relay/small cell at "
                  "equal cost/power?"],
         notes="Keep it honest: add amplifiers and you must compare against a relay. "
               "Passive RIS shines where relays are impractical (facades, indoor "
               "panels). STAR-RIS: serve both sides of the surface."),
    dict(kind="content", layout="bullets", title="Deployment: where RIS actually helps",
         bullets=["Sweet spots: mmWave/sub-THz blockage bypass, indoor dead zones, "
                  "localized capacity boosts",
                  "Placement rule: near TX or near RX — mid-path maximizes dyadic loss",
                  "Overheads that gate practicality: channel estimation and control "
                  "link, both scaling with N",
                  "Field trials encouraging; standardization pre-normative"],
         notes="Dyadic intuition: (d₁ d₂) is minimized at the ends — put the mirror "
               "next to the lamp or the book, not halfway. Estimation with almost no "
               "observations is a beautiful problem."),
    dict(kind="content", layout="bullets", title="RIS: open problems",
         bullets=["CSI acquisition with no RF chains on the panel",
                  "Wideband behavior: one phase per element, many subcarriers",
                  "EM-consistent models: mutual coupling, non-ideal reflection",
                  "RIS-aided sensing and localization: surfaces as programmable landmarks"],
         demo="▶  Live Demo 3 (2.5 min): the N² law — SNR gain from 16 to 1024 "
              "elements, random vs optimized phases.  [matlab/demo3_ris_gain]",
         notes="Rapid-fire, then MATLAB. Demo 3 is the shortest: the two scaling "
               "lines draw themselves; ask the audience to call the slope difference "
               "(2 vs 1). Fail → backup A3. Done by ~0:48:30."),

    # ===================== 6. ISAC =====================
    dict(kind="section", title="6 · Integrated Sensing & Communication"),
    dict(kind="content", layout="bullets", title="Why ISAC",
         bullets=["One spectrum, one infrastructure, two functions: comm + radar-style "
                  "sensing",
                  "Drivers: spectrum scarcity; a dense grid is a ready-made sensor "
                  "network; XR/V2X/drones need perception",
                  "IMT-2030 lists ISAC as a defining scenario — not an add-on",
                  "Economic pitch: sensing for free on waveforms you already transmit"],
         notes="From programming the channel to reading it. The cellular network "
               "grows a sense of sight: every BS already illuminates the scene. The "
               "regulatory angle (spectrum reuse) is what makes operators care."),
    dict(kind="content", layout="eq_bullets", title="Radar refresher in one slide",
         eq=[("eq_radar",
              r"\tau=\frac{2R}{c},\quad f_D=\frac{2v f_c}{c},\quad \Delta R=\frac{c}{2B},"
              r"\quad \Delta v=\frac{c}{2 f_c\,T_{\mathrm{obs}}}")],
         bullets=["Bandwidth buys range resolution; coherent time buys velocity resolution",
                  "Matched filtering + coherent integration = the SNR workhorses",
                  "All classic DSP — 6G reuses it wholesale, on comm hardware"],
         notes="Calibration slide: four formulas, no magic. For our demo: 30 MHz → "
               "5 m range resolution; ~9 ms of symbols at 28 GHz → ~5 m/s velocity "
               "resolution. Demo 4 will print exactly these."),
    dict(kind="content", layout="eq_bullets", tikz="isac_rx.tex",
         title="OFDM as a radar waveform",
         eq=[("eq_ofdm_radar",
              r"D[n,m]=\frac{Y[n,m]}{X[n,m]}\;\xrightarrow[\text{FFT over }m]{\text{IFFT over }n}\;"
              r"\text{range--Doppler map}")],
         bullets=[],
         notes="The Sturm–Wiesbeck trick: the RX knows the transmitted grid X (it "
               "is the payload!), so element-wise division leaves pure channel; IFFT "
               "over subcarriers gives delay, FFT over symbols gives Doppler. One "
               "frame, two products."),
    dict(kind="content", layout="bullets", title="Joint waveform design",
         bullets=["Design axes: power/subcarrier allocation, dedicated sensing symbols "
                  "vs data reuse, beampattern shaping",
                  "Inherent friction: comm wants randomness (capacity), radar wants "
                  "determinism (clean ambiguity function)",
                  "Recent theory: the 'random-data radar' penalty is quantifiable — "
                  "often acceptably small",
                  "Sensing-assisted comm: radar tracks feed beam prediction"],
         notes="The philosophical core: cleanest radar waveforms are deterministic "
               "chirps; best comm signals are maximum-entropy noise. Joint design "
               "negotiates between them. The reverse (sensing helps comm) may ship first."),
    dict(kind="content", layout="eq_bullets_img", title="Fundamental limits: CRB vs rate",
         eq=[("eq_crb",
              r"\mathrm{var}(\hat\tau)\;\ge\;\frac{1}{8\pi^{2}\,\beta_{\mathrm{rms}}^{2}\,\mathrm{SNR}\cdot N_{\mathrm{obs}}}"
              r"\quad(\beta_{\mathrm{rms}}:\text{RMS bandwidth})")],
         img="fig_rate_crb.png",
         bullets=["Delay CRB: RMS bandwidth is king — edge subcarriers are gold for ranging",
                  "Rate–CRB region: the capacity–distortion picture of ISAC",
                  "Waterfilling for rate ≠ for sensing → principled compromises"],
         notes="Ranging accuracy improves with RMS bandwidth, so band-edge power "
               "helps sensing but not capacity under flat channels — hence the "
               "trade-off. 5% of resources already buys cm-class CRB at these SNRs; "
               "the curve is steep at first — cheap lunches exist."),
    dict(kind="content", layout="bullets",
         title="Monostatic, bistatic, and network sensing",
         bullets=["Monostatic: full waveform knowledge; but TX–RX self-interference "
                  "is brutal (full duplex / quasi-CW)",
                  "Bistatic (BS→UE, BS→BS): no self-interference; sync and clock "
                  "offsets bite instead",
                  "Network/multistatic: fusion across cells — geometry diversity, "
                  "coverage; cellular timing helps"],
         notes="Monostatic is clean (Demo 4 assumes it) but hides the hardest RF "
               "problem: your own TX is 120 dB above the echo. Bistatic swaps that "
               "for a sync problem. Network sensing is where cellular can beat radar."),
    dict(kind="content", layout="bullets", title="ISAC in 3GPP",
         bullets=["Rel-19: dedicated channel-model study for ISAC (targets with RCS "
                  "enter the stochastic model); SA1 use cases feed RAN",
                  "Rel-20 (6G study): sensing among candidate native features; ETSI "
                  "ISG ISAC in parallel",
                  "Honest status: pre-normative — first commercial 'sensing' likely "
                  "positioning-class, then micro-Doppler apps"],
         demo="▶  Live Demo 4 (3 min): two moving targets on a range–Doppler map — "
              "from a frame carrying QPSK data.  [matlab/demo4_isac_range_doppler]",
         notes="Standards in 30 s, then MATLAB. The frame carries random QPSK — point "
               "at the console line confirming data demod, then the map: two blobs at "
               "40 m/+15 m/s and 75 m/-25 m/s, within one bin of truth. Second peak a "
               "few dB lower (scalloping). Fail → backup A4. Done by ~0:59:30."),

    # ===================== 7. AI-NATIVE PHY =====================
    dict(kind="section", title="7 · AI-Native Physical Layer"),
    dict(kind="content", layout="bullets", title="What 'AI-native' actually means",
         bullets=["5G: AI bolted on (SON, scheduling). 6G: AI as a design principle "
                  "inside the air interface",
                  "Model deficit: no faithful math model (hardware nonlinearity) → "
                  "learn the model",
                  "Algorithm deficit: model known, optimal algorithm intractable → "
                  "learn the algorithm",
                  "Integration spectrum: replace a block → co-design blocks → "
                  "end-to-end learned PHY"],
         notes="The deficit taxonomy (Shlezinger/Eldar) is the best sorting hat: it "
               "predicts where learning helps. Channel coding: no deficit, learning "
               "adds little. PA distortion: model deficit, learning shines."),
    dict(kind="content", layout="bullets", title="Deep learning for channel estimation",
         bullets=["Treat the pilot-grid estimate as a noisy image → CNN denoising / "
                  "super-resolution across time–frequency",
                  "Learned estimators approach MMSE without knowing channel statistics",
                  "Gains largest at low SNR and under model mismatch",
                  "Costs: training data, generalization, µs-latency inference"],
         notes="Exactly Demo 5's setting — hold the thought. The image analogy is not "
               "decoration: the TF channel grid has local correlation like natural "
               "images, so vision architectures transfer."),
    dict(kind="content", layout="bullets", title="Autoencoder end-to-end PHY",
         bullets=["O'Shea & Hoydis 2017: TX–channel–RX as one autoencoder; learn "
                  "constellation and demapper jointly",
                  "Learned constellations rediscover — and under impairments beat — "
                  "hand-designed ones",
                  "Needs a differentiable channel → surrogate models or RL for the real world"],
         notes="The paper that launched the field: the whole link as one "
               "differentiable function. Realism check: block-based systems won't "
               "vanish — certification, interoperability, debugging favor structure. "
               "Hybrids win in practice."),
    dict(kind="content", layout="bullets", title="Neural receivers",
         bullets=["Replace equalization + demapping with one trained network over the "
                  "received grid (channel estimate optional)",
                  "Demonstrated at 3GPP-compatible scale (multi-user MIMO neural "
                  "receivers, Sionna-class toolchains)",
                  "Robustness from training over channel distributions; complexity "
                  "tamed by pruning/quantization",
                  "Open: retraining cadence vs channel drift"],
         notes="The pragmatic middle ground vendors prototype: keep the OFDM frame, "
               "swap the inner receiver. Good neural receivers can skip explicit "
               "channel estimation — pilots become input features."),
    dict(kind="content", layout="eq_bullets",
         title="Model-based deep learning: deep unfolding",
         eq=[("eq_lista",
              r"\text{ISTA: } \mathbf x^{(k+1)}=\eta_{\lambda}\!\left(\mathbf x^{(k)}+A^{H}(\mathbf y-A\mathbf x^{(k)})\right)"
              r"\;\Rightarrow\; \text{LISTA: } \eta_{\lambda_k}\!\left(W_1^{(k)}\mathbf y+W_2^{(k)}\mathbf x^{(k)}\right)")],
         bullets=["Unroll K iterations into a K-layer network; learn the knobs "
                  "(steps, thresholds, matrices)",
                  "Order-of-magnitude fewer iterations at equal accuracy; keeps "
                  "interpretability",
                  "PHY wins: unfolded detection, beamforming, sparse channel estimation"],
         notes="Best of both worlds: your favorite iterative algorithm, after weight "
               "training — same skeleton, data-tuned parameters, priors survive. For "
               "faculty: unfolding is a paper machine. This is the cheat-sheet's centerfold."),
    dict(kind="content", layout="bullets", title="Semantic communications",
         bullets=["Shift from bit fidelity to task fidelity: transmit what the "
                  "receiver needs to act",
                  "Neural joint source–channel coding: graceful degradation, no cliff effect",
                  "Open theory: a semantic information measure; separation theorem; "
                  "standardizable interfaces",
                  "Fair positioning: promising for constrained links (XR, satellite "
                  "IoT); not a day-one feature"],
         notes="Flex slide — can merge into the next. Example: transmitting a face "
               "for a video call needs the expression, not the pixels. Cliff-effect "
               "contrast: digital dies at threshold; learned JSCC degrades like "
               "analog TV."),
    dict(kind="content", layout="bullets",
         title="The hard problems: data, generalization, trust",
         bullets=["Data: channel measurements are vendor-siloed; sim-to-real is the "
                  "quiet blocker",
                  "Generalization: across cells, hardware, mobility; distribution-shift "
                  "monitoring",
                  "Budget: µs inference, joules per inference, PHY real-time constraints",
                  "Trust: testability, certification, explainability",
                  "Opening: standardized channel datasets & benchmarks would be a real "
                  "service"],
         notes="The referee-hat slide. A well-curated public dataset + benchmark for "
               "one PHY task can out-impact another architecture paper."),
    dict(kind="content", layout="bullets", title="AI/ML in 3GPP",
         bullets=["Rel-18 study → Rel-19 normative first steps; three use cases: CSI "
                  "feedback compression, beam prediction, positioning",
                  "Two-sided models (UE encoder / network decoder): the interoperability "
                  "puzzle",
                  "6G study (Rel-20): AI-native candidates; the real spec work is "
                  "life-cycle management"],
         demo="▶  Live Demo 5 (2.5 min): LS vs MMSE vs a small neural network for OFDM "
              "channel estimation.  [matlab/demo5_dl_channel_estimation]",
         notes="Standards in three bullets, then the last MATLAB switch. LS is the "
               "statistics-free baseline; MMSE knows the true covariance (unfair); the "
               "small NN learns from data and lands within a fraction of a dB of MMSE. "
               "First to skip if late → backup A5. Done by ~1:10."),

    # ===================== 8. MULTIPLE ACCESS =====================
    dict(kind="section", title="8 · Multiple Access & Spectrum Sharing"),
    dict(kind="content", layout="bullets", title="Beyond orthogonal access",
         bullets=["OMA is capacity-optimal only in corner cases; 6G stress: massive "
                  "connectivity + heterogeneous QoS",
                  "Landscape: power-domain NOMA, code-domain (SCMA), RSMA, grant-free",
                  "5G reality: NOMA studied (MUST), not widely deployed — SIC "
                  "complexity vs modest gains",
                  "Reframe: multiple access = an interference-management philosophy"],
         notes="Last stretch of theory — keep energy up. The philosophy: OMA avoids "
               "interference, NOMA decodes it fully at one side, RSMA decodes exactly "
               "the part worth decoding."),
    dict(kind="content", layout="eq_bullets", title="Power-domain NOMA and SIC",
         eq=[("eq_noma",
              r"R_{\mathrm{far}}=\log_2\!\left(1+\frac{P_2|h_f|^2}{P_1|h_f|^2+\sigma^2}\right),"
              r"\quad R_{\mathrm{near}}=\log_2\!\left(1+\frac{P_1|h_n|^2}{\sigma^2}\right)")],
         bullets=["Superpose users in power; near user decodes far user's signal, "
                  "cancels, then decodes its own",
                  "Gains hinge on channel disparity (|h_n| ≫ |h_f|)",
                  "Taxes: SIC error propagation, CSI sensitivity — degrades with mobility"],
         notes="Two-user intuition: the far user treats the near user as noise; the "
               "near user decodes the strong far-user signal first and subtracts it. "
               "Everything good about NOMA lives in that asymmetry — and everything "
               "fragile too."),
    dict(kind="content", layout="eq_bullets", title="Rate-splitting multiple access (RSMA)",
         eq=[("eq_rsma",
              r"R_k = C_k + R_{p,k},\qquad \sum_k C_k \;\le\; \min_k\,\log_2\!\left(1+\mathrm{SINR}_{c,k}\right)")],
         bullets=["Split each message: common part (decoded by all) + private part (own)",
                  "One SIC step: decode common, subtract, decode private",
                  "Spans SDMA ↔ NOMA ↔ multicast as special cases of one framework"],
         notes="Killer property: robustness to imperfect CSIT — the common stream "
               "soaks up interference you failed to precode away, and RSMA is DoF-"
               "optimal under imperfect CSIT where SDMA collapses. That safety net "
               "is why it keeps gaining momentum."),
    dict(kind="content", layout="bullets", title="Grant-free and unsourced random access",
         bullets=["mMTC: short packets, sporadic activity, handshakes cost more than "
                  "the payload",
                  "Activity detection = compressed sensing again: sparse recovery / "
                  "covariance methods",
                  "Unsourced RA: all users share one codebook; decoder returns an "
                  "unordered message list",
                  "Same sparsity toolbox as Section 4 — third billing for the same math"],
         notes="Connect to S27: different matrix, identical math. Unsourced RA: nobody "
               "says who they are; the decoder outputs WHAT was said. Elegant, and "
               "increasingly practical."),
    dict(kind="content", layout="bullets", title="Why RSMA keeps gaining traction for 6G",
         bullets=["One framework unifying the access zoo — fewer special cases to standardize",
                  "Graceful degradation under imperfect CSIT (the regime real networks live in)",
                  "Documented synergies with multi-antenna ISAC and RIS beamforming",
                  "Entry fee: encoder/scheduler complexity, common-rate control signaling",
                  "“Split, superpose — and let SIC do bounded work.”"],
         notes="30-second summary + the quotable line. Transition: so far everything "
               "sat on towers; 6G coverage does not stop at the horizon."),

    # ===================== 9. NTN & NEW MEDIA =====================
    dict(kind="section", title="9 · Coverage from the Sky & New Media"),
    dict(kind="content", layout="bullets", title="Non-terrestrial networks: the 3D architecture",
         bullets=["Layers: LEO mega-constellations (300–1200 km), HAPS (~20 km), UAV relays",
                  "6G goal: one 3GPP-native fabric — common waveform family, seamless "
                  "sky↔ground mobility",
                  "Direct-to-device NTN is already commercially real; scaling it is the "
                  "6G task"],
         notes="Coverage becomes 3D: three altitude layers with different delay/"
               "Doppler/link-budget personalities. 5G retrofitted NTN in Rel-17; 6G "
               "designs for it from day one. Phones already talk to satellites."),
    dict(kind="content", layout="eq_bullets_img",
         title="The LEO signal processing problem: Doppler",
         eq=[("eq_leo",
              r"f_D(t)=\frac{f_c}{c}\,v_{\mathrm{rel}}(t),\quad v_{\mathrm{sat}}\approx 7.6\,\text{km/s}"
              r"\;\Rightarrow\; \pm 25\,\text{ppm}\;(\pm 50\,\text{kHz at 2 GHz})")],
         img="fig_leo_doppler.png",
         bullets=["Doppler rate up to ~kHz/s near zenith; RTT 2–25 ms breaks HARQ timing",
                  "The gift: ephemeris is known → pre-compensate, track only the residual",
                  "DD-domain waveforms (Section 3) are natural fits here"],
         notes="The S-curve is computed from real orbital geometry (600 km). Half the "
               "swing happens in the two minutes around zenith — the tracking stress "
               "test. Unlike a car, a satellite tells you its velocity in advance; "
               "open-loop pre-compensation removes ~95%."),
    dict(kind="content", layout="bullets", title="NTN in 3GPP: status in one minute",
         bullets=["Rel-17: NR-NTN baseline (transparent payloads, timing/Doppler handling)",
                  "Rel-18/19: coverage & mobility enhancements, IoT-NTN, regenerative "
                  "payloads on the way",
                  "6G: NTN native from the start — inter-satellite routing, "
                  "store-and-forward IoT, unified mobility"],
         notes="Flex slide — one breath per bullet, or skip. Transparent vs "
               "regenerative in one line: bent pipe versus a base station in orbit."),
    dict(kind="content", layout="bullets", title="Optical wireless and VLC",
         bullets=["IM/DD constraint: real, non-negative signals → DCO-/ACO-OFDM adaptations",
                  "LiFi: dense indoor capacity, security by physics; FSO: fiber-class "
                  "backhaul incl. ground–satellite",
                  "Challenges: alignment, ambient light, uplink asymmetry",
                  "Honest niche: industrial floors, cabins, RF-denied environments"],
         notes="Optical is a complement, not a competitor: where RF is denied or "
               "congested, photons commute. IM/DD kills negative amplitudes, so OFDM "
               "needs DC bias or asymmetric clipping — same toolbox, new constraint."),
    dict(kind="content", layout="bullets", title="Quantum-secured links (brief)",
         bullets=["QKD: key distribution whose security rests on physics; fiber and "
                  "satellite demos exist",
                  "Realism: point-to-point, modest key rates → practical path is "
                  "hybrid QKD + post-quantum crypto",
                  "For 6G: primarily a security-architecture topic, not a PHY-DSP one "
                  "— one slide on purpose"],
         notes="Deliberately brief — acknowledge the buzzword, place it correctly, "
               "move on. In Q&A: the DSP-adjacent part is CV-QKD receivers (coherent "
               "detection, error reconciliation)."),

    # ===================== 10. ENERGY, STANDARDS, ROADMAP =====================
    dict(kind="section", title="10 · Energy, Standardization & Roadmap"),
    dict(kind="content", layout="eq_bullets_img", title="Energy-efficient PHY design",
         eq=[("eq_ee",
              r"\eta_{EE}=\frac{R}{P_{\mathrm{tot}}}\;\;[\text{bit/J}],\qquad P_{\mathrm{ADC}}\propto 2^{b} f_s")],
         img="fig_energy_breakdown.png",
         bullets=["Network energy: OPEX + sustainability KPI (an IMT-2030 design value)",
                  "Levers: PA operating point (waveform!), low-resolution ADCs, "
                  "sleep-aware design, lean always-on signals",
                  "Design shift: bit/J next to bit/s/Hz"],
         notes="Tie the loop closed: the PAPR discussion IS an energy topic — back-off "
               "is wasted watts. The ADC/DAC share grows with bandwidth (illustrative "
               "bars): the converter wall is why low-resolution and hybrid keep winning."),
    dict(kind="content", layout="img", title="The 3GPP road to 6G",
         img="fig_release_timeline.png",
         bullets=["Rel-19 carries the studies that matter (ISAC model, AI/ML); Rel-20 "
                  "opens the 6G study; Rel-21 goes normative → first spec ≈ 2028–29"],
         notes="Practical advice: watch study-item technical reports (TR 38.8xx/9xx) — "
               "they tell you what industry will ask of academia two years ahead. "
               "WRC-27 settles new spectrum; influence windows are open now."),
    dict(kind="content", layout="bullets", title="The ITU IMT-2030 process",
         bullets=["M.2160 framework (2023) → requirements & evaluation (2024–26) → "
                  "submissions → IMT-2030 specs ≈ 2029–30",
                  "Same machinery that turned IMT-2020 into '5G' — history rhymes",
                  "Feeding programs: Hexa-X-II (EU), Next G Alliance (US), IMT-2030 "
                  "Promotion Group (CN), Bharat 6G (IN)"],
         notes="De-mystify the acronym soup: ITU defines what counts as 6G and "
               "evaluates candidates; 3GPP writes the technology submitted. Aligning "
               "grant objectives with the IMT-2030 capability list is free reviewer "
               "goodwill."),
    dict(kind="content", layout="bullets", title="A research roadmap for this room",
         bullets=["Start now (paper-sized): DD-domain receivers & AFDM; near-field CSI "
                  "& codebooks; ISAC CRB–rate trade-offs; deep-unfolded PHY",
                  "Build toward (project-sized): cell-free + RIS testbeds; AI life-cycle "
                  "management; sub-THz prototyping; public channel datasets",
                  "Choose problems where DSP insight beats brute force — our "
                  "comparative advantage"],
         notes="Match problems to resources: the first group needs MATLAB and "
               "stubbornness; the second needs infrastructure and consortia. The "
               "closing line is career advice."),
    dict(kind="content", layout="img", title="The 6G signal-processing map",
         img="fig_roadmap.png",
         bullets=["Recurring themes: sparsity • domain transforms • hardware-aware "
                  "design • model + data hybrids"],
         notes="Same roadmap as slide 5, now earned. Name the four themes slowly — "
               "they are the intellectual through-line; every section used at least two."),

    # ===================== 11. CLOSING =====================
    dict(kind="section", title="11 · Takeaways & Q&A"),
    dict(kind="content", layout="bullets", title="Five demos, five lessons",
         bullets=["D1 OFDM vs OTFS: at high Doppler, change the domain, not the SNR",
                  "D2 Hybrid beamforming: in sparse channels, 4 RF chains ≈ 64",
                  "D3 RIS: co-phasing turns a random walk into N² combining",
                  "D4 ISAC: a data-carrying frame can image two moving targets",
                  "D5 Learned estimation: ≈ MMSE without knowing the statistics"],
         notes="Each demo compressed to its aphorism — read all five with rhythm. "
               "This is the recap that makes the demos stick. All code goes home."),
    dict(kind="content", layout="bullets", title="Key takeaways",
         bullets=["6G = new spectrum + new geometry (near-field) + new functions "
                  "(sensing) + new tools (learning)",
                  "OFDM is not dead — it has new roommates; expect scenario-adaptive PHY",
                  "Three formulas organize half the field: P ∝ N²  •  d_R = 2D²/λ  "
                  "•  var(τ̂) ≥ 1/(8π²β²·SNR)",
                  "Signal processing turns physics into throughput"],
         notes="THE LANDING SLIDE — if the schedule collapsed, jump straight here. "
               "Deliver the four lines slowly. The three-formulas bullet earns the "
               "photo of the talk; pause on it."),
    dict(kind="content", layout="bullets", title="Open problems worth a PhD",
         bullets=["Unified DD-domain ISAC: one waveform, provably optimal for both jobs",
                  "Near-field channel estimation & codebooks at N > 10³",
                  "EM-consistent RIS models (coupling, wideband) that stay tractable",
                  "Trustworthy neural PHY: certification, monitoring, graceful fallback",
                  "Energy-optimal waveform + PA co-design for sub-THz",
                  "Grant-free access at 10⁸ devices/km²: CS at societal scale"],
         notes="Aimed at the research scholars: each line is a defensible thesis "
               "statement with its entry toolbox. Offer to discuss any in Q&A or by email."),
    dict(kind="content", layout="refs", title="References & resources",
         notes="Don't read — point: fifteen well-chosen surveys and landmark papers; "
               "the handout has the same list. Every item is genuine and widely-cited; "
               "volume/number details were compiled from memory — spot-check before "
               "printing."),
    dict(kind="standout", title="Thank you!",
         lines=["Dr. Markkandan S  ·  Associate Professor, SENSE, VIT Chennai",
                "markkandan.s@vit.ac.in",
                "Slides, MATLAB demos & Python verification code ship together."],
         notes="Land warmly; invite collaboration explicitly — faculty for joint "
               "proposals, scholars for co-supervision. Keep MATLAB open: the best "
               "Q&A reuses a demo with a parameter changed live."),

    # ===================== APPENDIX: BACKUPS =====================
    dict(kind="backup", title="Backup A1: pre-computed result — Demo 1 (OFDM vs OTFS)",
         img="demo_backups/backup_demo1.png",
         notes="Only if Demo 1 fails live. OFDM floors near 3e-2 from ICI; OTFS falls "
               "past 1e-4 by 20 dB. Right: the delay-Doppler channel the frame saw."),
    dict(kind="backup", title="Backup A2: pre-computed result — Demo 2 (hybrid beamforming)",
         img="demo_backups/backup_demo2.png",
         notes="Only if Demo 2 fails live. Left: 64-element ULA patterns, 18 dB peak "
               "gain. Right: OMP hybrid with 4 RF chains tracks fully digital."),
    dict(kind="backup", title="Backup A3: pre-computed result — Demo 3 (RIS N² law)",
         img="demo_backups/backup_demo3.png",
         notes="Only if Demo 3 fails live. Log-log slopes: optimized 2.0 (the N² law), "
               "random 1.0. Analytic overlays sit on the simulation."),
    dict(kind="backup", title="Backup A4: pre-computed result — Demo 4 (ISAC range–Doppler)",
         img="demo_backups/backup_demo4.png",
         notes="Only if Demo 4 fails live. Two targets recovered within one bin each "
               "(40 m/+15 m/s and 75 m/-25 m/s) from a QPSK-carrying frame."),
    dict(kind="backup", title="Backup A5: pre-computed result — Demo 5 (learned estimation)",
         img="demo_backups/backup_demo5.png",
         notes="Only if Demo 5 fails live. LS tracks σ²; ideal MMSE gains ~9–10 dB "
               "using true statistics; the learned estimator matches MMSE within a "
               "fraction of a dB from data alone."),
]

# 15 IEEE-style references (mirror beamer/sections/sec11_closing.tex)
REFERENCES = [
    "ITU-R Rec. M.2160-0, “Framework and overall objectives of the future "
    "development of IMT for 2030 and beyond,” Nov. 2023.",
    "W. Saad, M. Bennis, M. Chen, “A vision of 6G wireless systems,” IEEE "
    "Network, vol. 34, no. 3, 2020.",
    "H. Tataria et al., “6G wireless systems: Vision, requirements, challenges, "
    "insights, and opportunities,” Proc. IEEE, vol. 109, no. 7, 2021.",
    "R. Hadani et al., “Orthogonal time frequency space modulation,” Proc. IEEE "
    "WCNC, 2017.",
    "Z. Wei et al., “Orthogonal time-frequency space modulation: A promising "
    "next-generation waveform,” IEEE Wireless Commun., vol. 28, no. 4, 2021.",
    "A. Bemani, N. Ksairi, M. Kountouris, “AFDM: Affine frequency division "
    "multiplexing for next generation wireless,” IEEE Trans. Wireless Commun., 2023.",
    "O. El Ayach et al., “Spatially sparse precoding in millimeter wave MIMO "
    "systems,” IEEE Trans. Wireless Commun., vol. 13, no. 3, 2014.",
    "E. Björnson, J. Hoydis, L. Sanguinetti, “Massive MIMO has unlimited "
    "capacity,” IEEE Trans. Wireless Commun., vol. 17, no. 1, 2018.",
    "Q. Wu, R. Zhang, “Intelligent reflecting surface enhanced wireless network "
    "via joint active and passive beamforming,” IEEE Trans. Wireless Commun., "
    "vol. 18, no. 11, 2019.",
    "M. Di Renzo et al., “Smart radio environments empowered by reconfigurable "
    "intelligent surfaces,” IEEE JSAC, vol. 38, no. 11, 2020.",
    "F. Liu et al., “Integrated sensing and communications: Toward dual-functional "
    "wireless networks for 6G and beyond,” IEEE JSAC, vol. 40, no. 6, 2022.",
    "C. Sturm, W. Wiesbeck, “Waveform design and signal processing aspects for "
    "fusion of wireless communications and radar sensing,” Proc. IEEE, vol. 99, "
    "no. 7, 2011.",
    "T. O'Shea, J. Hoydis, “An introduction to deep learning for the physical "
    "layer,” IEEE Trans. Cogn. Commun. Netw., vol. 3, no. 4, 2017.",
    "N. Shlezinger, J. Whang, Y. C. Eldar, A. J. Goldsmith, “Model-based deep "
    "learning,” Proc. IEEE, vol. 111, no. 5, 2023.",
    "Y. Mao, O. Dizdar, B. Clerckx, R. Schober, P. Popovski, H. V. Poor, "
    "“Rate-splitting multiple access: Fundamentals, survey, and future research "
    "trends,” IEEE Commun. Surveys Tuts., vol. 24, no. 4, 2022.",
]
