%% ========================================================================
%  DEMO 2 — Massive-array beamforming: pencil beams, a LIVE steering slider,
%           and why 4 RF chains can (almost) match 64.
%
%  THREE ACTS
%  ----------
%  (a) ARRAY FACTOR BY HAND.  A uniform linear array (ULA) of Nel = 64
%      elements at half-wavelength spacing. Each element sees an incoming
%      plane wave from angle theta with a progressive phase pi*n*sin(theta)
%      (because d = lambda/2  =>  2*pi*d/lambda = pi). We steer by applying
%      a conjugate taper w_n = exp(+j*pi*n*sin(theta0))/Nel; the array
%      response ("array factor") is  AF(theta) = w^H a(theta), where a() is
%      the steering vector. On a dB scale AF peaks at 20*log10(Nel) ~ 36 dB
%      and forms an increasingly narrow "pencil beam" as Nel grows. All of
%      this is a couple of exp()/sum() lines — NO Phased Array System Toolbox.
%
%  (b) LIVE BEAM STEERING (the on-stage centrepiece).  A uicontrol slider
%      sweeps the steering angle theta0 from -90 to +90 deg; its callback
%      recomputes AF(theta) and redraws a polar beam pattern in real time,
%      so the audience watches the main lobe swing across the room while the
%      sidelobes stay pinned ~13 dB down. This window is INTERACTIVE and is
%      guarded so the script still runs headless (see the display check).
%
%  (c) HYBRID vs FULLY-DIGITAL PRECODING.  At mmWave you cannot afford one
%      RF chain per antenna. Hybrid beamforming uses a few RF chains (Nrf)
%      feeding a network of analog phase shifters. We compare, over SNR:
%        * fully digital  : optimal unconstrained precoder Fopt = first Ns
%                            right singular vectors of the channel (SVD);
%        * hybrid OMP     : El-Ayach spatially-sparse precoding — greedily
%                            pick Nrf array-response beams (Orthogonal
%                            Matching Pursuit over a DFT-like dictionary) and
%                            least-squares fit the digital baseband Fbb;
%        * analog only    : a single beam steered at the strongest path.
%      Punchline: in a SPARSE mmWave channel (few paths), Nrf = 4 RF chains
%      track the fully-digital spectral efficiency to within a fraction of a
%      bit/s/Hz, at a fraction of the hardware cost.
%
%  This is a faithful MATLAB translation of the verified NumPy reference
%      matlab/verification/gen_demo2_backup.py
%  (helpers _sv_channel / _omp_hybrid from figures/make_figures.py) — same
%  parameters, same model, same math. MATLAB's RNG differs from NumPy's, so
%  the absolute Monte-Carlo values wobble at the ~1% level, but the ORDERING
%  and the tiny digital-vs-hybrid gap — the whole point — reproduce either way.
%
%  TOOLBOXES
%  ---------
%  REQUIRES: base MATLAB only. (No Signal Processing / Communications /
%  Phased Array / Deep Learning toolboxes. Steering vectors, the array
%  factor, the SVD-based digital precoder, the OMP dictionary/greedy loop and
%  the log-det spectral efficiency are all base linear algebra done by hand.)
%
%  EXPECTED RUNTIME: ~3 seconds for the computation + saved figures (well
%  under the 60 s budget). The interactive slider window then stays open.
%
%  FIGURES SAVED (300 dpi PNG, into ../../figures/):
%      fig_hybrid_se.png          — spectral efficiency: fully digital vs
%                                    OMP hybrid vs analog-only, vs SNR (slide).
%      fig_demo2_arrayfactor.png  — static 3-beam array-factor snapshot.
% =========================================================================

function run_demo()

% ---- Reproducibility -----------------------------------------------------
% Fixed seed so the on-stage numbers are identical every run. (The NumPy
% reference uses default_rng(2); MATLAB's Mersenne-Twister is a different
% stream, so absolute SE values differ slightly but the curves line up.)
rng(2);

% ---- Palette (matches the shared talk_style.py deck colours) ------------
C_BLUE   = hex2rgb('#2a78d6');   % fully digital
C_ORANGE = hex2rgb('#eb6834');   % hybrid OMP
C_AQUA   = hex2rgb('#1baf7a');   % analog only
INK2     = hex2rgb('#52514e');   % secondary ink for annotations

% ---- Global array geometry ----------------------------------------------
Nel      = 64;                       % ULA elements for the beam-pattern acts
thetaDeg = linspace(-90, 90, 2001);  % fine angle grid for a smooth pattern

% =========================================================================
%  ACT (c) FIRST — compute the spectral-efficiency curves and SAVE the slide.
%  We do the (headless-safe) number crunching and figure saving BEFORE the
%  interactive window, so the slide PNG is guaranteed on disk even if the
%  live slider is skipped or errors on a projector-less machine.
% =========================================================================

% ---- mmWave MIMO / precoding parameters (mirror the Python reference) ----
Nt     = 64;    % transmit antennas (BS ULA)
Nr     = 16;    % receive antennas (UE ULA)
L      = 6;     % channel paths (sparse mmWave scattering)
Ns     = 4;     % data streams
Nrf    = 4;     % RF chains (== number of analog beams OMP may pick)
trials = 40;    % Monte-Carlo channel realisations (~40 per reference)
snr_db = -10:5:20;                   % SNR sweep: -10 -5 0 5 10 15 20 dB

se_dig = zeros(1, numel(snr_db));    % accumulated mean SE, fully digital
se_hyb = zeros(1, numel(snr_db));    % accumulated mean SE, hybrid OMP
se_ana = zeros(1, numel(snr_db));    % accumulated mean SE, analog only

for t = 1:trials
    % --- Narrowband Saleh-Valenzuela mmWave channel (Nr x Nt) ------------
    [H, aod] = sv_channel(Nt, Nr, L);

    % --- Fully-digital optimum precoder: first Ns right singular vectors.
    % SVD gives H = U*S*V'. The unconstrained precoder that maximises mutual
    % information pours power into the strongest Ns spatial modes, i.e. the
    % leading columns of V. (matches Vh.conj().T[:, :Ns] in NumPy.)
    [~, ~, V] = svd(H);
    Fopt = V(:, 1:Ns);               % Nt x Ns

    % --- Hybrid OMP precoder: Frf (analog, unit-modulus beams) * Fbb -----
    [Frf, Fbb] = omp_hybrid(Fopt, Nrf, Nt);
    Fhyb = Frf * Fbb;                % Nt x Ns realised hybrid precoder

    % --- Analog-only baseline: one beam at the strongest path's AoD ------
    fana = exp(1i*pi*(0:Nt-1).' * sin(aod(1))) / sqrt(Nt);   % Nt x 1

    % --- Spectral efficiency vs SNR: SE = log2 det( I + (rho/ns) H F F^H H^H )
    for i = 1:numel(snr_db)
        rho = 10^(snr_db(i)/10);     % linear SNR

        se_dig(i) = se_dig(i) + se_logdet(H, Fopt, rho, Ns) / trials;
        se_hyb(i) = se_hyb(i) + se_logdet(H, Fhyb, rho, Ns) / trials;
        se_ana(i) = se_ana(i) + se_logdet(H, fana, rho, 1 ) / trials;
    end
end

% ---- Console read-out: confirm 4 RF chains ~ fully digital ---------------
gap_hi = se_dig(end) - se_hyb(end);   % at the top SNR
fprintf('\n SNR(dB)   digital   hybridOMP   analog\n');
for i = 1:numel(snr_db)
    fprintf('%6d   %8.3f  %9.3f  %8.3f\n', ...
            snr_db(i), se_dig(i), se_hyb(i), se_ana(i));
end
fprintf(['hybrid OMP trails fully digital by %.3f bit/s/Hz at %d dB ' ...
         '(4 RF chains ~ 64).\n'], gap_hi, snr_db(end));

% ---- Figure: spectral efficiency vs SNR (the saved slide) ---------------
figSE = figure('Color', 'w', 'Position', [80 80 950 600]);
axSE  = axes('Parent', figSE); hold(axSE, 'on');

plot(axSE, snr_db, se_dig, '-o', 'Color', C_BLUE, ...
     'MarkerFaceColor', C_BLUE,   'LineWidth', 2.8, 'MarkerSize', 9, ...
     'DisplayName', 'fully digital (SVD)');
plot(axSE, snr_db, se_hyb, '-s', 'Color', C_ORANGE, ...
     'MarkerFaceColor', C_ORANGE, 'LineWidth', 2.8, 'MarkerSize', 9, ...
     'DisplayName', sprintf('hybrid OMP (%d RF chains)', Nrf));
plot(axSE, snr_db, se_ana, '-^', 'Color', C_AQUA, ...
     'MarkerFaceColor', C_AQUA,   'LineWidth', 2.8, 'MarkerSize', 10, ...
     'DisplayName', 'analog only (1 beam)');

xlabel(axSE, 'SNR (dB)');
ylabel(axSE, 'Spectral efficiency (bit/s/Hz)');
title(axSE, {sprintf('%d\\times%d mmWave MIMO, %d paths, N_s = %d streams', ...
                     Nt, Nr, L, Ns), ...
             sprintf('%d RF chains track fully digital (gap %.2f bit/s/Hz)', ...
                     Nrf, gap_hi)});
legend(axSE, 'Location', 'northwest');
style_axes(axSE);

save_fig(figSE, fullfile(script_dir(), '..', '..', 'figures', 'fig_hybrid_se.png'));

% ---- Figure: static 3-beam array-factor snapshot (slide backup) ---------
% Three fixed steering angles, showing pencil beams and 20*log10(Nel) gain.
figAF = figure('Color', 'w', 'Position', [80 80 950 560]);
axAF  = axes('Parent', figAF); hold(axAF, 'on');

steer  = [-40, 0, 25];                       % steering angles (deg)
cols   = {C_AQUA, C_BLUE, C_ORANGE};         % one colour per beam
for k = 1:numel(steer)
    AF = array_factor_db(Nel, steer(k), thetaDeg);
    plot(axAF, thetaDeg, AF, 'Color', cols{k}, 'LineWidth', 2.8, ...
         'DisplayName', sprintf('steer %+d deg', steer(k)));
end
ylim(axAF, [-30 40]);  xlim(axAF, [-90 90]);
xlabel(axAF, 'Angle (deg)');
ylabel(axAF, 'Array gain (dB)');
title(axAF, sprintf('%d-element ULA: pencil beams, %.0f dB peak gain', ...
                    Nel, 20*log10(Nel)));
legend(axAF, 'Location', 'south');
set(axAF, 'XTick', -90:30:90);
style_axes(axAF);

save_fig(figAF, fullfile(script_dir(), '..', '..', 'figures', 'fig_demo2_arrayfactor.png'));

% =========================================================================
%  ACT (b) — LIVE steering slider (interactive centrepiece).
%  Guarded so the script still completes headless: if no figure display is
%  available (e.g. `matlab -batch` on a CI box or a projector-less laptop),
%  we simply skip the window — the two PNGs above are already saved.
% =========================================================================
hasDisplay = true;
try
    % `feature('ShowFigureWindows')` returns false under -nodisplay/-batch.
    hasDisplay = feature('ShowFigureWindows');
catch
    hasDisplay = usejava('desktop');
end

if ~hasDisplay
    fprintf('Headless mode: interactive steering slider skipped (PNGs saved).\n');
    fprintf('run_demo (demo2): done\n');
    return;
end

try
    rOffset = 40;                    % dB->radius shift so -40 dB maps to r=0
    th0     = 0;                     % initial steering angle (deg)

    figLive = figure('Name', 'Demo 2 - LIVE 64-element beam steering', ...
                     'Color', 'w', 'Position', [120 90 780 760], ...
                     'NumberTitle', 'off');

    % Polar beam pattern. polarplot() takes theta in RADIANS for the data,
    % while ThetaLim/ThetaTick are set in the axis display units (degrees).
    pax = polaraxes('Parent', figLive, 'Units', 'normalized', ...
                    'Position', [0.06 0.24 0.88 0.66]);
    AF  = array_factor_db(Nel, th0, thetaDeg);
    hLine = polarplot(pax, deg2rad(thetaDeg), max(AF, -40) + rOffset, ...
                      'Color', C_BLUE, 'LineWidth', 3.0);

    % Orient the fan: 0 deg (broadside) points up, angle increases clockwise,
    % show only the physical -90..+90 half-plane. Radius axis relabelled to dB.
    pax.ThetaZeroLocation = 'top';
    pax.ThetaDir          = 'clockwise';
    pax.ThetaLim          = [-90 90];
    pax.ThetaTick         = -90:30:90;
    pax.RLim              = [0 rOffset + 40];        % 0..80 (i.e. -40..+40 dB)
    pax.RTick             = 0:20:80;
    pax.RTickLabel        = {'-40','-20','0','20','40'};
    pax.FontSize          = 14;
    pax.LineWidth         = 1.2;

    hTitle = title(pax, steer_title(th0, Nel), 'FontSize', 17, ...
                   'FontWeight', 'bold');

    % Caption / instruction under the dial.
    uicontrol(figLive, 'Style', 'text', 'Units', 'normalized', ...
              'Position', [0.06 0.115 0.88 0.05], ...
              'String', 'Drag to steer the beam:  the main lobe swings, the sidelobes stay ~13 dB down', ...
              'FontSize', 14, 'FontWeight', 'bold', ...
              'BackgroundColor', 'w', 'ForegroundColor', INK2, ...
              'HorizontalAlignment', 'center');

    % Min/max end labels for the slider.
    uicontrol(figLive, 'Style', 'text', 'Units', 'normalized', ...
              'Position', [0.03 0.05 0.10 0.045], 'String', '-90 deg', ...
              'FontSize', 14, 'BackgroundColor', 'w', ...
              'HorizontalAlignment', 'center');
    uicontrol(figLive, 'Style', 'text', 'Units', 'normalized', ...
              'Position', [0.87 0.05 0.10 0.045], 'String', '+90 deg', ...
              'FontSize', 14, 'BackgroundColor', 'w', ...
              'HorizontalAlignment', 'center');

    % The steering slider itself. SliderStep is [minor major] as a fraction of
    % the (Max-Min)=180 range: click-arrows nudge 1 deg, trough-clicks 10 deg.
    sld = uicontrol(figLive, 'Style', 'slider', 'Units', 'normalized', ...
                    'Position', [0.14 0.05 0.72 0.045], ...
                    'Min', -90, 'Max', 90, 'Value', th0, ...
                    'SliderStep', [1/180, 10/180]);

    % Callback: recompute + redraw on release, and continuously while dragging.
    cb = @(s, ~) update_beam(s, hLine, hTitle, Nel, thetaDeg, rOffset);
    set(sld, 'Callback', cb);
    try
        addlistener(sld, 'ContinuousValueChange', cb);   % smooth live drag
    catch
        % Older MATLAB without ContinuousValueChange: release-only is fine.
    end

    drawnow;
    fprintf('Interactive steering slider is open — drag to steer the beam.\n');
catch ME
    % Never let a graphics hiccup abort the demo: the slide PNGs are saved.
    warning('run_demo:sliderSkipped', ...
            'Interactive slider skipped (%s). Saved figures are unaffected.', ...
            ME.message);
end

fprintf('run_demo (demo2): done\n');

end % ===================== end main function =============================


%% ------------------------------------------------------------------------
%  LOCAL HELPER FUNCTIONS  (keep run_demo.m fully self-contained)
%  ------------------------------------------------------------------------

function AF = array_factor_db(Nel, th0_deg, theta_deg)
% ULA array factor in dB for a beam steered to th0_deg, evaluated over the
% angle grid theta_deg. Half-wavelength spacing => inter-element phase is
% pi*sin(theta). Steering taper w_n = exp(+j*pi*n*sin(th0))/Nel, response is
% AF(theta) = w^H a(theta) with a_n(theta) = exp(+j*pi*n*sin(theta)). We add
% +20*log10(Nel) so the co-phased peak reads the true array gain (~36 dB).
    n = (0:Nel-1).';                                   % Nel x 1 element index
    w = exp(1i*pi*n*sin(deg2rad(th0_deg))) / Nel;      % Nel x 1 steering taper
    A = exp(1i*pi*n*sin(deg2rad(theta_deg(:).')));     % Nel x Ntheta responses
    AF = 20*log10(abs(w' * A) + 1e-9) + 20*log10(Nel); % 1 x Ntheta, in dB
    AF = AF(:).';
end

function update_beam(sld, hLine, hTitle, Nel, theta_deg, rOffset)
% Slider callback: read the steering angle, recompute the array factor, and
% push the new radii (floored at -40 dB, then offset to non-negative radius)
% into the existing polar line. Cheap enough to run live on every drag event.
    th0 = get(sld, 'Value');
    AF  = array_factor_db(Nel, th0, theta_deg);
    set(hLine, 'RData', max(AF, -40) + rOffset);
    set(hTitle, 'String', steer_title(th0, Nel));
end

function s = steer_title(th0, Nel)
% Title string for the live dial (kept ASCII so it renders on any machine).
    s = sprintf('Steering angle = %+.0f deg   |   peak array gain = %.0f dB', ...
                th0, 20*log10(Nel));
end

function [H, aod] = sv_channel(Nt, Nr, L)
% Narrowband Saleh-Valenzuela mmWave channel with ULAs at both ends and
% half-wavelength spacing. L propagation paths, each with a random complex
% gain g_l ~ CN(0,1) and independent AoD/AoA drawn uniformly on (-60,60) deg.
% H = sqrt(Nt*Nr/L) * sum_l g_l * ar(aoa_l) * at(aod_l)^H   (rank <= L).
    at  = @(th) exp(1i*pi*(0:Nt-1).' * sin(th)) / sqrt(Nt);   % Tx steering vec
    ar  = @(th) exp(1i*pi*(0:Nr-1).' * sin(th)) / sqrt(Nr);   % Rx steering vec
    aod = (rand(1, L)*2 - 1) * (pi/3);                        % AoD in (-pi/3,pi/3)
    aoa = (rand(1, L)*2 - 1) * (pi/3);                        % AoA in (-pi/3,pi/3)
    g   = (randn(1, L) + 1i*randn(1, L)) / sqrt(2);           % path gains CN(0,1)
    H   = zeros(Nr, Nt);
    for l = 1:L
        H = H + g(l) * (ar(aoa(l)) * at(aod(l))');   % outer product ar * at^H
    end
    H = H * sqrt(Nt*Nr / L);                          % normalise channel power
end

function [Frf, Fbb] = omp_hybrid(Fopt, Nrf, Nt)
% El-Ayach spatially-sparse hybrid precoding via Orthogonal Matching Pursuit.
% Greedily pick Nrf array-response "beams" from a DFT-like dictionary A whose
% columns best explain the residual of the target precoder Fopt, then solve a
% least-squares baseband Fbb and finally renormalise the total transmit power.
    G      = 128;                                     % dictionary resolution
    sinv   = -1 + (2/G)*(0:G-1) + 1/G;               % linspace(-1,1,G,endpt=F)+1/G
    thetas = asin(sinv);                             % candidate beam angles
    A      = exp(1i*pi*(0:Nt-1).' * sin(thetas)) / sqrt(Nt);  % Nt x G dictionary

    Frf  = zeros(Nt, 0);                             % chosen analog beams
    Fres = Fopt;                                     % residual to approximate
    for k = 1:Nrf
        % Correlate every dictionary beam with the residual; pick the beam
        % with the most total energy across the Ns columns.
        proj      = sum(abs(A' * Fres).^2, 2);       % G x 1 projected energy
        [~, idx]  = max(proj);
        Frf       = [Frf, A(:, idx)];                %#ok<AGROW> append beam
        Fbb       = Frf \ Fopt;                       % LS baseband (min ||Fopt-Frf Fbb||)
        Fres      = Fopt - Frf*Fbb;                   % new residual
        nrm       = norm(Fres, 'fro');
        if nrm > 1e-12, Fres = Fres / nrm; end        % renormalise residual
    end
    Fbb = Frf \ Fopt;                                 % final baseband solve
    Fbb = Fbb * (norm(Fopt, 'fro') / norm(Frf*Fbb, 'fro'));  % power renorm
end

function se = se_logdet(H, F, rho, ns)
% Spectral efficiency of a Gaussian MIMO link with precoder F and equal power
% split across ns streams:  SE = log2 det( I_Nr + (rho/ns) H F F^H H^H ).
% Writing G = H*F keeps it as one Hermitian PSD update; the tiny imaginary
% part of det() from round-off is discarded with real().
    Nr = size(H, 1);
    G  = H * F;                                   % Nr x ns effective channel
    M  = eye(Nr) + (rho/ns) * (G * G');           % Hermitian, I + low-rank
    se = real(log2(det(M)));
end

function style_axes(ax)
% Presentation-ready cosmetics: heavy fonts and a light grid so the plot
% reads from the back row of the lecture theatre.
    set(ax, 'FontSize', 15, ...          % tick label size (>= 14 pt rule)
            'LineWidth', 1.2, ...        % axis box line width
            'Box', 'on', ...
            'XColor', hex2rgb('#52514e'), ...
            'YColor', hex2rgb('#52514e'), ...
            'GridColor', hex2rgb('#d8d7d2'), ...
            'GridAlpha', 0.9, ...
            'Layer', 'top');
    grid(ax, 'on');
    ax.XLabel.FontSize = 16;  ax.XLabel.Color = 'k';
    ax.YLabel.FontSize = 16;  ax.YLabel.Color = 'k';
    ax.Title.FontSize  = 17;  ax.Title.Color  = 'k';
    lg = get(ax, 'Legend');
    if ~isempty(lg), lg.FontSize = 15; end
end

function save_fig(fig, outfile)
% Write a 300-dpi PNG. Prefer exportgraphics (R2020a+, tight crop); fall
% back to print -dpng -r300 on older MATLAB. Create the folder if needed.
    outdir = fileparts(outfile);
    if ~exist(outdir, 'dir'), mkdir(outdir); end
    if exist('exportgraphics', 'file') == 2
        exportgraphics(fig, outfile, 'Resolution', 300);
    else
        print(fig, outfile, '-dpng', '-r300');
    end
    fprintf('saved: %s\n', outfile);
end

function d = script_dir()
% Absolute directory of THIS script, so figure paths resolve no matter what
% the current working directory is when the demo is launched.
    d = fileparts(mfilename('fullpath'));
end

function rgb = hex2rgb(hex)
% Convert a '#rrggbb' hex string to a 1x3 RGB triplet in [0,1]. Written by
% hand to keep the script on base MATLAB (no toolbox colour helpers).
    hex = char(hex);
    if hex(1) == '#', hex = hex(2:end); end
    rgb = [hex2dec(hex(1:2)), hex2dec(hex(3:4)), hex2dec(hex(5:6))] / 255;
end
