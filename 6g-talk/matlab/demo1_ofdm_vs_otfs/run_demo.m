%% run_demo.m  --  Demo 1: CP-OFDM vs OTFS over a high-Doppler channel
% =========================================================================
% 6G talk, live on-stage demo.  Self-contained: NO external helper files.
% Styling/saving helpers live as LOCAL functions at the bottom of THIS file.
%
% REQUIRES: base MATLAB ONLY.
%   - No Signal Processing Toolbox function is called (FFTs are base MATLAB).
%   - No Communications Toolbox function is called (QPSK, channel, LMMSE are
%     all implemented by hand so the audience can follow the DSP).
%   - exportgraphics (R2020a+) is base MATLAB; a print(-dpng) fallback is used
%     on older releases.
%
% EXPECTED RUNTIME: ~3-8 s on a laptop (all 512x512 matrices, 40 frames).
%
% WHAT THIS SHOWS
%   A vehicle at 500 km/h @ 28 GHz sees a large Doppler (f_d ~ 13 kHz).  Over
%   one OFDM symbol the channel rotates, so subcarriers leak into each other
%   (inter-carrier interference, ICI).  A per-subcarrier 1-tap equalizer then
%   hits an irreducible BER *floor*.  OTFS instead carries data in the
%   delay-Doppler (DD) domain, where the same physical channel looks like a
%   few static taps; an LMMSE detector using the exact DD input-output matrix
%   keeps driving the BER down -- no floor in the simulated range.
%
% This is a faithful MATLAB translation of the verified reference
%   matlab/verification/verify_demo1_otfs.py
% Same model, same parameters.  Monte-Carlo BER values will differ from the
% Python mirror at the 4th decimal only (MATLAB's RNG stream differs from
% NumPy's); the curves and the OFDM-floor / OTFS-no-floor story are identical.
%
% FIGURES SAVED (300 dpi PNG, into ../../figures/):
%   fig_demo1_ber.png   BER vs SNR, CP-OFDM (floor) vs OTFS (keeps falling)
%   fig_tf_vs_dd.png    time-frequency |H| (fades everywhere) vs delay-Doppler
%                       channel grid (a few sparse, quasi-static taps)
% =========================================================================

clear; close all; clc;
rng(1);                              % fixed seed -> reproducible Monte-Carlo

% ------------------------- parameters (match the Python reference) --------
M      = 32;                         % delay bins  == OFDM subcarriers
N      = 16;                         % Doppler bins == OFDM symbols per frame
df     = 60e3;                       % subcarrier spacing [Hz]
fc     = 28e9;                       % carrier frequency [Hz]
v_kmh  = 500;                        % vehicle speed [km/h]
P      = 4;                          % number of physical channel paths
Lcp    = 8;                          % OFDM cyclic-prefix length [samples]
SNRS   = 0:5:30;                     % SNR sweep [dB]
NFRAMES= 40;                         % channel realizations averaged per SNR

fs     = M * df;                     % sample rate [Hz]  (full band = M*df)
Ts     = 1 / fs;                     % sample period [s]
Tsym   = 1 / df;                     % OFDM useful symbol duration [s]
fd_max = v_kmh/3.6 * fc / 3e8;       % max Doppler shift [Hz]  (v/c * fc)

% Normalized Doppler eps = f_d * Tsym  (fraction of a subcarrier the channel
% rotates through in one symbol -> the ICI knob).  Doppler resolution of the
% DD grid is 1/(N*Tsym) = df/N.
eps_norm = fd_max * Tsym;
dopp_res = df / N;
fprintf('fd_max        = %.2f kHz\n', fd_max/1e3);
fprintf('normalized Doppler  eps = fd*Tsym = %.3f\n', eps_norm);
fprintf('Doppler resolution  df/N          = %.2f kHz\n', dopp_res/1e3);

% Unitary N-point DFT matrix (used to move columns between time and Doppler).
Fn = fft(eye(N)) / sqrt(N);

% DD -> time operator for OTFS:  A = F_N^H  (kron)  I_M.
% A is the same for every frame, so build it ONCE (pure precompute, no change
% to the math).  s_time = A * x_dd ;  y_dd = A^H * y .
A  = kron(Fn', eye(M));              % (N*M) x (N*M)

nbits = 2 * N * M;                   % QPSK -> 2 bits/symbol, N*M symbols/frame

% ------------------------- Monte-Carlo BER simulation ---------------------
ber_ofdm = zeros(size(SNRS));
ber_otfs = zeros(size(SNRS));

for f = 1:NFRAMES
    % ---- draw one doubly-selective channel realization -------------------
    [delays, dopp, gains] = draw_channel(P, fd_max);

    % ======================= OTFS branch ==================================
    % Time-domain channel operator over the whole frame (cyclic in the frame),
    % then the exact DD input-output matrix  H_eff = A^H G A .
    G     = channel_time_matrix(delays, dopp, gains, N, M, Ts);
    H_eff = A' * G * A;              % DD-domain effective channel
    HhH   = H_eff' * H_eff;          % pre-form for the LMMSE normal equations

    bits_t = randi([0 1], nbits, 1); % OTFS payload bits (this frame)
    x_dd   = qpsk_mod(bits_t);       % N*M DD-domain QPSK symbols
    s_time = A * x_dd;               % transmit time samples
    r_clean= G * s_time;             % noiseless receive time samples

    % ======================= CP-OFDM branch ===============================
    % N consecutive CP-OFDM symbols pushed through the SAME physical channel
    % (linear, non-cyclic convolution with absolute time index so the Doppler
    % phase keeps advancing across the frame).
    bits_o = randi([0 1], nbits, 1);
    syms_o = qpsk_mod(bits_o);                   % N*M QPSK symbols
    Xf     = reshape(syms_o, M, N).';            % N symbols (rows) x M subc.
    rx_clean = zeros(M+Lcp, N);                  % clean rx per symbol (cols)
    Hf_mid   = zeros(M, N);                      % mid-symbol freq response
    nstart   = 0;                                % absolute sample index
    for i = 1:N
        xt     = ifft(Xf(i,:)).' * sqrt(M);      % M time samples (energy norm)
        xt_cp  = [xt(end-Lcp+1:end); xt];        % prepend cyclic prefix
        rx_clean(:,i) = apply_channel_linear(xt_cp, delays, dopp, gains, ...
                                             nstart, Ts);
        % Frequency response sampled at the MIDDLE of the symbol.  A 1-tap
        % equalizer can only use one snapshot -> the rotation across the
        % symbol becomes ICI it cannot undo (the eventual error floor).
        nmid = nstart + Lcp + M/2;
        h_t  = zeros(M,1);
        for p = 1:P
            h_t(delays(p)+1) = h_t(delays(p)+1) + gains(p) * ...
                exp(1j*2*pi*dopp(p)*(nmid - delays(p))*Ts);
        end
        Hf_mid(:,i) = fft(h_t);
        nstart = nstart + M + Lcp;
    end

    % ---- sweep SNR: add noise to the (cached) clean signals --------------
    for si = 1:numel(SNRS)
        sigma2 = 10.^(-SNRS(si)/10);             % noise power (Es = 1)

        % ---------- OTFS: single LMMSE solve in the DD domain -------------
        y     = r_clean + sqrt(sigma2/2) * ...
                (randn(N*M,1) + 1j*randn(N*M,1));
        y_dd  = A' * y;                          % back to DD domain
        x_hat = (HhH + sigma2*eye(N*M)) \ (H_eff' * y_dd);   % LMMSE
        ber_otfs(si) = ber_otfs(si) + ...
                       mean(qpsk_demod(x_hat) ~= bits_t) / NFRAMES;

        % ---------- CP-OFDM: per-subcarrier 1-tap LMMSE per symbol --------
        errs = 0;
        for i = 1:N
            r   = rx_clean(:,i) + sqrt(sigma2/2) * ...
                  (randn(M+Lcp,1) + 1j*randn(M+Lcp,1));
            Yf  = fft(r(Lcp+1:end)) / sqrt(M);   % strip CP, to freq domain
            Hf  = Hf_mid(:,i);
            Xhat= Yf .* conj(Hf) ./ (abs(Hf).^2 + sigma2);   % 1-tap LMMSE
            seg = bits_o(2*M*(i-1)+1 : 2*M*i);
            errs= errs + sum(qpsk_demod(Xhat) ~= seg);
        end
        ber_ofdm(si) = ber_ofdm(si) + errs / nbits / NFRAMES;
    end
end

fprintf('\nSNR(dB) : %s\n', mat2str(SNRS));
fprintf('BER OFDM: %s\n', num2str(ber_ofdm, '%.4g  '));
fprintf('BER OTFS: %s\n', num2str(ber_otfs, '%.4g  '));

% ------------------------- Figure 1: BER vs SNR ---------------------------
C_BLUE   = [42 120 214]/255;         % CP-OFDM series
C_ORANGE = [235 104 52]/255;         % OTFS series

fig1 = figure('Color','w','Position',[100 100 900 560]);
ax1  = axes(fig1);
semilogy(ax1, SNRS, ber_ofdm, '-o', 'Color', C_BLUE, ...
    'LineWidth', 2.8, 'MarkerSize', 9, 'MarkerFaceColor', C_BLUE, ...
    'DisplayName', 'CP-OFDM, 1-tap LMMSE'); hold(ax1,'on');
semilogy(ax1, SNRS, ber_otfs, '-s', 'Color', C_ORANGE, ...
    'LineWidth', 2.8, 'MarkerSize', 9, 'MarkerFaceColor', C_ORANGE, ...
    'DisplayName', 'OTFS, LMMSE (DD domain)'); hold(ax1,'off');
ylim(ax1, [1e-5 1]); xlim(ax1, [SNRS(1) SNRS(end)]);
xlabel(ax1, 'SNR (dB)'); ylabel(ax1, 'BER');
title(ax1, {sprintf('QPSK, 500 km/h @ 28 GHz (f_d = %.1f kHz), %d paths', ...
                    fd_max/1e3, P), ...
            'OFDM hits an ICI floor -- OTFS keeps falling'});
legend(ax1, 'Location', 'southwest');
style_axes(ax1);
saveFig(fig1, 'fig_demo1_ber.png');

% ------------------------- Figure 2: TF vs DD channel grids ---------------
% Fresh channel realization for the illustrative heatmaps (mirrors the
% reference, which draws a new channel here).
[delays, dopp, gains] = draw_channel(P, fd_max);

% Delay-Doppler grid: each path drops onto ONE (delay, Doppler) cell.
Hdd = zeros(M, N);
for p = 1:P
    k   = round(dopp(p) / (df/N));           % nearest Doppler bin
    col = mod(k + N/2, N) + 1;               % center zero Doppler
    Hdd(delays(p)+1, col) = Hdd(delays(p)+1, col) + abs(gains(p));
end

% Time-frequency grid: |H(f)| snapshot at the middle of each OFDM symbol.
% Because of Doppler, this magnitude fades all over the plane.
Htf = zeros(M, N);
for i = 1:N
    nmid = (i-1)*(M+Lcp) + Lcp + M/2;
    h_t  = zeros(M,1);
    for p = 1:P
        h_t(delays(p)+1) = h_t(delays(p)+1) + ...
            gains(p) * exp(1j*2*pi*dopp(p)*nmid*Ts);
    end
    Htf(:,i) = abs(fft(h_t));
end

fig2 = figure('Color','w','Position',[100 100 1200 500]);

axL = subplot(1,2,1);
imagesc(axL, [0 N], [0 M], Htf); set(axL,'YDir','normal');
axis(axL, [0 N 0 M]);
colormap(axL, blues_map(256)); cb1 = colorbar(axL); cb1.LineWidth = 1.2;
xlabel(axL, 'OFDM symbol (time)'); ylabel(axL, 'subcarrier (freq)');
title(axL, 'Time-frequency:  |H| fades everywhere');
style_axes(axL); grid(axL,'off');

axR = subplot(1,2,2);
imagesc(axR, [-N/2 N/2], [0 M], Hdd); set(axR,'YDir','normal');
axis(axR, [-N/2 N/2 0 M]);
colormap(axR, blues_map(256)); cb2 = colorbar(axR); cb2.LineWidth = 1.2;
xlabel(axR, 'Doppler bin'); ylabel(axR, 'delay bin');
title(axR, sprintf('Delay-Doppler:  %d taps, quasi-static', P));
style_axes(axR); grid(axR,'off');

saveFig(fig2, 'fig_tf_vs_dd.png');

fprintf('\nrun_demo (Demo 1): done.\n');

% =========================================================================
%                            LOCAL FUNCTIONS
% =========================================================================

function [delays, dopp, gains] = draw_channel(P, fd_max)
% P paths: integer delays (first is 0), Jakes-drawn Dopplers, unit avg power.
    delays = [0; randi([1 5], P-1, 1)];               % integer delay taps
    dopp   = fd_max * cos(2*pi*rand(P,1));            % Doppler per path [Hz]
    gains  = (randn(P,1) + 1j*randn(P,1)) / sqrt(2*P);% E[sum|g|^2] = 1
end

function G = channel_time_matrix(delays, dopp, gains, N, M, Ts)
% Time-domain channel over one OTFS frame, cyclic in the frame.
%   G[n, (n-l) mod NM] += g * exp(j*2*pi*nu*(n-l)*Ts)
% Built column-vectorized per path (each path is a shifted, Doppler-modulated
% diagonal, so its row->column map is a bijection -> no index collisions).
    NM = N * M;
    n  = (0:NM-1).';
    G  = zeros(NM, NM);
    rows = (1:NM).';
    for p = 1:numel(delays)
        l  = delays(p);  nu = dopp(p);  g = gains(p);
        cols = mod(n - l, NM) + 1;                    % 1-based column index
        ph   = g * exp(1j*2*pi*nu*(n - l)*Ts);        % phase per sample n
        idx  = rows + (cols - 1)*NM;                  % linear indices
        G(idx) = G(idx) + ph;
    end
end

function y = apply_channel_linear(x, delays, dopp, gains, nstart, Ts)
% Linear (non-cyclic) channel for the CP-OFDM path.  nstart is the absolute
% sample index of x(1), so the Doppler phase advances across the whole frame.
    L = numel(x);
    y = zeros(L + 5, 1);
    n = nstart + (0:L-1).';
    for p = 1:numel(delays)
        l  = delays(p);  nu = dopp(p);  g = gains(p);
        y(l+1 : l+L) = y(l+1 : l+L) + ...
            g * exp(1j*2*pi*nu*(n - l)*Ts) .* x;
    end
    y = y(1:L);
end

function s = qpsk_mod(bits)
% Gray QPSK: even-index bits -> real, odd-index bits -> imag, unit energy.
    b = bits(:);
    s = ((1 - 2*b(1:2:end)) + 1j*(1 - 2*b(2:2:end))) / sqrt(2);
end

function b = qpsk_demod(sym)
% Hard decision inverse of qpsk_mod.
    s = sym(:);
    b = zeros(2*numel(s), 1);
    b(1:2:end) = real(s) < 0;
    b(2:2:end) = imag(s) < 0;
end

function style_axes(ax)
% Presentation styling: heavy fonts / lines so it reads when projected.
    set(ax, 'FontSize', 15, 'LineWidth', 1.4, 'Box', 'on', ...
            'GridAlpha', 0.25);
    set(get(ax,'XLabel'), 'FontSize', 16);
    set(get(ax,'YLabel'), 'FontSize', 16);
    set(get(ax,'Title'),  'FontSize', 17);
    grid(ax, 'on');
end

function cmap = blues_map(nlev)
% White-ish -> deep-blue sequential colormap (approximates matplotlib "Blues"),
% so the MATLAB heatmaps match the static slide images.
    lo = [247 251 255] / 255;        % near white
    hi = [  8  48 107] / 255;        % deep blue
    t  = linspace(0, 1, nlev).';
    cmap = lo + t .* (hi - lo);
end

function saveFig(fig, name)
% Save one figure as a 300-dpi PNG into ../../figures/ using a path relative
% to THIS script (so it works from any current directory).  exportgraphics
% with a print(-dpng) fallback for pre-R2020a MATLAB.
    here   = fileparts(mfilename('fullpath'));
    figdir = fullfile(here, '..', '..', 'figures');
    if ~exist(figdir, 'dir'); mkdir(figdir); end
    outpath = fullfile(figdir, name);
    try
        exportgraphics(fig, outpath, 'Resolution', 300);
    catch
        print(fig, outpath, '-dpng', '-r300');
    end
    fprintf('saved: %s\n', outpath);
end
