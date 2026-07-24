%% ========================================================================
%  DEMO 3 — The RIS "N-squared law": why a Reconfigurable Intelligent
%           Surface is worth building.
%
%  SCENARIO
%  --------
%  A single-antenna transmitter and a single-antenna receiver. The direct
%  line-of-sight path is BLOCKED (think: a wall, or a building corner). The
%  only way through is to bounce the signal off a Reconfigurable Intelligent
%  Surface (RIS): a flat panel of N cheap, passive elements, each of which
%  can add a controllable phase shift theta_n to whatever hits it.
%
%  The cascaded (Tx -> RIS element n -> Rx) channel is the PRODUCT of two
%  fading coefficients:
%        cascade_n = h_n * g_n        (Tx->element  times  element->Rx)
%  and the receiver sees the coherent sum over all N elements:
%        y = sum_n  |h_n||g_n| * exp( j*( arg(h_n) + arg(g_n) + theta_n ) ).
%
%  THE DSP PUNCHLINE
%  -----------------
%  * OPTIMIZED phases: choose theta_n to CANCEL the cascade phase so every
%    term lines up as a positive real number. The amplitudes then add
%    coherently -> received amplitude ~ N -> received POWER ~ N^2.
%  * RANDOM phases: the N terms are little vectors pointing every which way,
%    i.e. a 2-D random walk -> received POWER ~ N (grows only linearly).
%
%  The gap between an N^2 curve and an N curve is the entire commercial case
%  for a RIS: doubling the panel size buys +6 dB with optimized phases
%  (power x4) but only +3 dB (power x2) if you leave the phases random.
%
%  WHAT THIS SCRIPT DOES
%  ---------------------
%  Sweep N = 2^4 .. 2^10 (16..1024). For each N run ~400 Monte-Carlo trials
%  with per-element channels h_n, g_n ~ CN(0,1). Measure the mean received
%  power for optimized vs random phases, overlay the analytic laws, fit the
%  log-log slopes (expect ~2.0 and ~1.0), and print a table.
%
%  This is a faithful MATLAB translation of the verified NumPy reference
%      matlab/verification/verify_demo3_ris.py
%  (same parameters, same math, same analytic references).
%
%  TOOLBOXES
%  ---------
%  REQUIRES: base MATLAB only. (No Signal Processing / Communications /
%  Deep Learning toolboxes are used — all randomness, sums, FFT-free
%  combining and the least-squares slope fit are base functions.)
%
%  EXPECTED RUNTIME: ~2 seconds on a laptop (well under the 60 s budget).
%
%  FIGURE SAVED (300 dpi PNG, into ../../figures/):
%      fig_demo3_ris_scaling.png
% =========================================================================

function run_demo()

% ---- Reproducibility -----------------------------------------------------
% Fixed seed so the on-stage numbers are identical every run. (The NumPy
% reference uses seed 3; MATLAB's generator is different, so the absolute
% Monte-Carlo values wobble at the ~1% level, but the SLOPES — which are the
% whole point — land on ~2.0 and ~1.0 either way.)
rng(3);

% ---- Sweep and Monte-Carlo settings -------------------------------------
Ns     = 2.^(4:10);      % RIS element counts: 16 32 64 128 256 512 1024
TRIALS = 400;            % Monte-Carlo trials per N (average out the fading)

p_opt = zeros(1, numel(Ns));   % measured mean power, optimized phases
p_rnd = zeros(1, numel(Ns));   % measured mean power, random phases

% ---- Monte-Carlo loop over panel size N ---------------------------------
for i = 1:numel(Ns)
    Nel = Ns(i);

    % Per-element cascade channels. Each of h_n, g_n is a unit-variance
    % complex Gaussian CN(0,1): real and imaginary parts are N(0,1/2), so
    % dividing (randn + 1j*randn) by sqrt(2) gives E[|h|^2] = 1.
    h = (randn(TRIALS, Nel) + 1i*randn(TRIALS, Nel)) / sqrt(2);
    g = (randn(TRIALS, Nel) + 1i*randn(TRIALS, Nel)) / sqrt(2);

    % Element-wise cascade: the effective per-element channel is the PRODUCT
    % h_n * g_n. Its magnitude |h_n||g_n| is what an optimally-phased element
    % contributes; its argument is the phase the RIS must cancel.
    casc = h .* g;                              % TRIALS-by-Nel complex

    % OPTIMIZED phases: theta_n = -arg(h_n g_n) makes every term real and
    % positive, so the coherent sum is simply sum of magnitudes. Summing
    % along dim 2 collapses the N elements into one scalar per trial.
    y_opt   = sum(abs(casc), 2);               % TRIALS-by-1, real >= 0
    p_opt(i) = mean(abs(y_opt).^2);            % mean received power

    % RANDOM phases: theta_n ~ Uniform(0,2*pi) leaves the terms pointing in
    % random directions. Their vector sum is a 2-D random walk of N steps.
    theta   = 2*pi*rand(TRIALS, Nel);
    y_rnd   = sum(casc .* exp(1i*theta), 2);   % TRIALS-by-1, complex
    p_rnd(i) = mean(abs(y_rnd).^2);            % mean received power
end

% ---- Analytic references ------------------------------------------------
% For CN(0,1) fading, |h| and |g| are Rayleigh with E[|h|]=sqrt(pi)/2, so
% E[|h||g|] = pi/4. With optimized phases the mean amplitude is N*pi/4;
% squaring and adding the exact per-element variance correction gives:
%     E[P_opt] = (N*pi/4)^2 * ( 1 + (16 - pi^2) / (N*pi^2) )  ~ (pi^2/16) N^2.
% With random phases the walk has zero-mean unit-variance steps
% (E[|h g|^2] = 1), so the mean power is exactly N.
ana_opt = (Ns*pi/4).^2 .* (1 + (16 - pi^2) ./ (Ns*pi^2));
ana_rnd = double(Ns);

% ---- Console table (mirrors the Python reference) -----------------------
fprintf('\n N    P_opt(sim)  P_opt(ana)   P_rnd(sim)  P_rnd(ana)\n');
for i = 1:numel(Ns)
    fprintf('%5d  %10.1f  %10.1f  %10.2f  %10.2f\n', ...
            Ns(i), p_opt(i), ana_opt(i), p_rnd(i), ana_rnd(i));
end

% ---- Fit the log-log slopes ---------------------------------------------
% A power law P = a*N^s is a straight line of slope s in log-log axes.
% polyfit(...,1) is an ordinary least-squares line fit; the first
% coefficient is the slope. Expect ~2.0 (optimized) and ~1.0 (random).
c_opt = polyfit(log10(Ns), log10(p_opt), 1);   slope_opt = c_opt(1);
c_rnd = polyfit(log10(Ns), log10(p_rnd), 1);   slope_rnd = c_rnd(1);
fprintf(['fitted log-log slopes: optimized %.3f (expect ~2), ' ...
         'random %.3f (expect ~1)\n'], slope_opt, slope_rnd);

% ---- Palette (matches the shared talk_style.py deck colours) ------------
C_BLUE   = hex2rgb('#2a78d6');   % random-phase series
C_ORANGE = hex2rgb('#eb6834');   % optimized-phase series
INK2     = hex2rgb('#52514e');   % secondary ink for annotations

% ---- Figure -------------------------------------------------------------
fig = figure('Color', 'w', 'Position', [100 100 950 600]);
ax  = axes('Parent', fig); hold(ax, 'on');

% Simulated points + connecting lines (markers make the 7 sweep points pop).
h_opt = loglog(ax, Ns, p_opt, '-o', 'Color', C_ORANGE, ...
               'MarkerFaceColor', C_ORANGE, 'LineWidth', 2.8, ...
               'MarkerSize', 9, 'DisplayName', 'optimized phases (sim)');
h_ao  = loglog(ax, Ns, ana_opt, '--', 'Color', C_ORANGE, ...
               'LineWidth', 2.6, 'DisplayName', 'analytic \approx (\pi^2/16) N^2');
h_rnd = loglog(ax, Ns, p_rnd, '-s', 'Color', C_BLUE, ...
               'MarkerFaceColor', C_BLUE, 'LineWidth', 2.8, ...
               'MarkerSize', 9, 'DisplayName', 'random phases (sim)');
h_ar  = loglog(ax, Ns, ana_rnd, '--', 'Color', C_BLUE, ...
               'LineWidth', 2.6, 'DisplayName', 'analytic N');

% Force true log-log scaling (loglog on an existing axes still needs this
% when we mix in hold/annotations).
set(ax, 'XScale', 'log', 'YScale', 'log');

% --- Annotation: the +6 dB-per-doubling story on the optimized curve ------
% On slope-2 axes, doubling N multiplies power by 4 = +6 dB. Draw a little
% "stair" between N=128 and N=256 on the optimized curve to make it visual.
n0 = 128;  j0 = find(Ns == n0);
xr = [Ns(j0) Ns(j0+1) Ns(j0+1)];              % right-angle step: over then up
yr = [p_opt(j0) p_opt(j0) p_opt(j0+1)];
plot(ax, xr, yr, ':', 'Color', INK2, 'LineWidth', 2.0, 'HandleVisibility', 'off');
text(ax, Ns(j0+1)*1.06, sqrt(p_opt(j0)*p_opt(j0+1)), ...
     {'+6 dB per', 'doubling of N', '(power \times4)'}, ...
     'FontSize', 14, 'Color', C_ORANGE, 'FontWeight', 'bold', ...
     'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle');
text(ax, 300, 700, '+3 dB per doubling (power \times2)', ...
     'FontSize', 14, 'Color', C_BLUE, 'FontWeight', 'bold', ...
     'HorizontalAlignment', 'left');

% Labels, title, legend.
xlabel(ax, 'Number of RIS elements  N');
ylabel(ax, 'Mean received power (linear, norm.)');
title(ax, {'The RIS N^2 law: co-phasing turns a random walk', ...
           'into coherent combining (+6 dB per doubling)'});
legend([h_opt h_ao h_rnd h_ar], 'Location', 'northwest');

% Tick marks exactly on the swept N values, log y-grid for readability.
set(ax, 'XTick', Ns, 'XTickLabel', string(Ns));
xlim(ax, [Ns(1)/1.3, Ns(end)*1.3]);

style_axes(ax);        % apply the presentation-ready cosmetics

% ---- Save 300-dpi PNG into ../../figures/ -------------------------------
outfile = fullfile(script_dir(), '..', '..', 'figures', ...
                   'fig_demo3_ris_scaling.png');
save_fig(fig, outfile);
fprintf('saved: %s\n', outfile);
fprintf('run_demo (demo3): done\n');

end % ===================== end main function =============================


%% ------------------------------------------------------------------------
%  LOCAL HELPER FUNCTIONS  (keep run_demo.m fully self-contained)
%  ------------------------------------------------------------------------

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
