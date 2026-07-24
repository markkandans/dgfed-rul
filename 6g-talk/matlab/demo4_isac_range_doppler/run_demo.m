function run_demo()
% run_demo  Demo 4: OFDM-based Integrated Sensing and Communication (ISAC).
% =========================================================================
%  6G talk -- LIVE on-stage demo.  Self-contained script (no helper files).
%
%  Idea (Sturm & Wiesbeck, Proc. IEEE 2011): the SAME QPSK-modulated OFDM
%  frame that carries user DATA also illuminates the environment like a
%  radar.  A monostatic receiver hears its own transmitted symbols echoed
%  back by two moving targets.  Because the transmitter KNOWS the data
%  symbols X, it can divide them out (D = Y ./ X) -- "channel sounding for
%  free" -- and what remains is a pure two-dimensional sinusoid whose
%  frequencies encode range (delay across subcarriers) and velocity
%  (Doppler across OFDM symbols).  Two FFTs turn that into a
%  range-Doppler image, exactly like a pulse-Doppler radar.
%
%  Signal model (per subcarrier n, per OFDM symbol m):
%     Y[n,m] = sum_t a_t * X[n,m]
%                    * exp(-j 2pi n df tau_t)      % delay  -> range
%                    * exp(+j 2pi m To fD_t) + W   % Doppler-> velocity
%     tau_t = 2 R_t / c,   fD_t = 2 v_t fc / c
%
%  Processing:
%     D   = Y ./ X                 % remove the (known) data modulation
%     ->  IFFT over subcarriers n  % delay/range profile
%     ->  FFT  over symbols   m    % Doppler/velocity profile
%     ->  fftshift in Doppler      % centre zero velocity
%
%  Resolutions:
%     dR = c / (2 B),         B  = Nsc * df       (range   resolution)
%     dv = c / (2 fc Msym To)                     (velocity resolution)
%  Unambiguous limits:
%     Rmax = c / (2 df),      vmax = c / (4 fc To)
%
%  Targets:  (R=40 m, v=+15 m/s, amp 1.0) and (R=75 m, v=-25 m/s, amp 0.7)
%  SNR = 10 dB per resolution cell BEFORE processing; the two FFTs add
%  10*log10(Nsc*Msym) ~ 45 dB of coherent processing gain, so both peaks
%  pop out cleanly and land within ~1 resolution bin of the truth.
%
% -------------------------------------------------------------------------
%  REQUIRES: base MATLAB ONLY.  fft / ifft / fftshift are core functions,
%            QPSK symbols are built by hand, and the viridis colormap is
%            embedded below -- so NO Signal Processing / Communications /
%            other toolbox is needed to run this demo.
%
%  EXPECTED RUNTIME: < 1 second (a 256 x 128 grid + two FFTs).
%
%  REPRODUCIBILITY: rng(4) is fixed.  NOTE that MATLAB's and NumPy's
%  random streams differ, so the noise realisation is NOT bit-identical to
%  the Python reference verify_demo4_isac.py; the DSP, the printed
%  resolutions and the detected (range, velocity) are reproduced exactly
%  (peaks within one bin of truth) because processing gain swamps the noise.
%
%  OUTPUT: figures/fig_demo4_rd_map.png  (300 dpi, presentation-ready).
% =========================================================================

    rng(4);                              % fixed seed -> reproducible run

    % ---- deck accent colours (match the talk_style palette) -------------
    C_ORANGE = [235 104  52] / 255;      % detection markers / annotations

    % =====================================================================
    % 1) Parameters  (kept in exact sync with the Python reference)
    % =====================================================================
    c0   = 3e8;          % speed of light            [m/s]
    fc   = 28e9;         % carrier frequency (mmWave) [Hz]
    df   = 120e3;        % subcarrier spacing         [Hz]
    Nsc  = 256;          % number of subcarriers
    Msym = 128;          % number of OFDM symbols
    CP   = 0.07;         % cyclic-prefix fraction
    To   = (1 + CP) / df;% total OFDM symbol duration [s]  (useful + CP)
    B    = Nsc * df;     % occupied bandwidth         [Hz]

    % Ground-truth targets: columns = [range(m), velocity(m/s), amplitude]
    targets = [ 40.0, +15.0, 1.0 ;       % strong, approaching
                75.0, -25.0, 0.7 ];      % weaker, receding
    nTgt    = size(targets, 1);
    snr_db  = 10.0;                       % pre-processing SNR per cell [dB]

    % ---- resolutions & unambiguous limits -------------------------------
    dR   = c0 / (2 * B);                  % range    resolution [m]
    dv   = c0 / (2 * fc * Msym * To);     % velocity resolution [m/s]
    Rmax = c0 / (2 * df);                 % max unambiguous range   [m]
    vmax = c0 / (4 * fc * To);            % max unambiguous |vel|   [m/s]

    fprintf('B = %.1f MHz | dR = %.2f m | dv = %.2f m/s | Rmax = %.0f m | vmax = +/-%.0f m/s\n', ...
            B/1e6, dR, dv, Rmax, vmax);

    % =====================================================================
    % 2) Transmit frame: unit-power QPSK on every subcarrier & symbol
    % =====================================================================
    %   Gray-mapped QPSK: each of I and Q is +/-1/sqrt(2).  This is the
    %   user's DATA -- random and unknown to a bystander, but known to the
    %   monostatic ISAC receiver (it transmitted it).
    b0 = randi([0 1], Nsc, Msym);         % in-phase   bit
    b1 = randi([0 1], Nsc, Msym);         % quadrature bit
    X  = ((1 - 2*b0) + 1j*(1 - 2*b1)) / sqrt(2);   % Nsc x Msym QPSK grid

    % =====================================================================
    % 3) Radar channel: superpose the two moving-target echoes + noise
    % =====================================================================
    %   n indexes subcarriers (column vector), m indexes symbols (row
    %   vector); implicit expansion broadcasts the phase ramps across the
    %   whole Nsc x Msym grid.
    n = (0:Nsc-1).';                      % Nsc x 1
    m = (0:Msym-1);                       % 1   x Msym
    Y = zeros(Nsc, Msym);
    for t = 1:nTgt
        R  = targets(t,1);  v = targets(t,2);  a = targets(t,3);
        tau = 2 * R  / c0;                % round-trip delay      [s]
        fD  = 2 * v  * fc / c0;           % Doppler shift         [Hz]
        % delay ramp along subcarriers, Doppler ramp along symbols:
        Y = Y + a * X ...
              .* exp(-1j*2*pi * n * df * tau) ...    % Nsc x 1  broadcast
              .* exp(+1j*2*pi * m * To * fD);        % 1 x Msym broadcast
    end

    % Complex AWGN.  sigma is set so the per-cell SNR is snr_db (the QPSK
    % symbols carry unit power); the 1/sqrt(2) splits power over I and Q.
    sigma = 10^(-snr_db/20);
    Y = Y + sigma * (randn(Nsc,Msym) + 1j*randn(Nsc,Msym)) / sqrt(2);

    % =====================================================================
    % 4) Range-Doppler processing  (two FFTs after removing the data)
    % =====================================================================
    D   = Y ./ X;                         % divide out KNOWN symbols
    D   = ifft(D, [], 1);                 % IFFT over subcarriers -> range
    D   = fft (D, [], 2);                 % FFT  over symbols     -> Doppler
    D   = fftshift(D, 2);                 % centre zero Doppler (velocity)

    P   = 20*log10(abs(D) + 1e-12);       % magnitude in dB
    P   = P - max(P(:));                  % normalise: peak = 0 dB

    r_axis = (0:Nsc-1) * dR;                          % range   axis [m]
    v_axis = ((0:Msym-1) - floor(Msym/2)) * dv;       % velocity axis [m/s]

    % =====================================================================
    % 5) Peak detection: greedily pick the two strongest cells
    % =====================================================================
    %   Only the first half of the range axis is unambiguous (the IFFT is
    %   conjugate-symmetric for real delays), so search rows 1..Nsc/2.
    half = Nsc/2;
    Psub = P(1:half, :);
    Pwork = Psub;                          % working copy we mask into
    found = zeros(nTgt, 3);                % [range, velocity, power(dB)]
    for k = 1:nTgt
        [~, lin] = max(Pwork(:));          % strongest remaining cell
        [ri, ci] = ind2sub(size(Pwork), lin);
        found(k,:) = [r_axis(ri), v_axis(ci), Psub(ri,ci)];
        % Blank a +/-4-bin neighbourhood so the next iteration finds a
        % DIFFERENT target rather than the same peak's shoulder.
        rr = max(1,ri-4):min(half, ri+4);
        cc = max(1,ci-4):min(Msym, ci+4);
        Pwork(rr,cc) = -200;
    end

    % ---- report detected vs. truth --------------------------------------
    for k = 1:nTgt
        fprintf('detected: R = %6.1f m, v = %+6.1f m/s  (%.1f dB)\n', ...
                found(k,1), found(k,2), found(k,3));
    end
    for t = 1:nTgt
        Rt = targets(t,1);  vt = targets(t,2);
        ok = any( abs(found(:,1)-Rt) <= 2*dR & abs(found(:,2)-vt) <= 2*dv );
        verdict = 'MISS';  if ok, verdict = 'MATCH'; end
        fprintf('truth   : R = %6.1f m, v = %+6.1f m/s  -> %s\n', Rt, vt, verdict);
    end

    % =====================================================================
    % 6) Figure: the range-Doppler map with detections circled
    % =====================================================================
    fig = figure('Color','w','Units','inches','Position',[1 1 10.5 6.2]);
    ax  = axes('Parent', fig);

    % imagesc maps the matrix onto the physical (velocity, range) axes;
    % 'YDir','normal' puts short range at the bottom (origin lower).
    imagesc(ax, v_axis, r_axis(1:half), Psub);
    set(ax, 'YDir', 'normal');
    colormap(ax, viridisMap());           % embedded perceptual colormap
    caxis(ax, [-40 0]);                    % same dynamic range as reference

    cb = colorbar(ax);
    cb.Label.String   = 'relative power (dB)';
    cb.Label.FontSize = 15;
    cb.FontSize       = 14;

    hold(ax, 'on');
    hDet = gobjects(1);
    for k = 1:nTgt
        v = found(k,2);  R = found(k,1);
        h = plot(ax, v, R, 'o', 'MarkerSize', 18, ...
                 'MarkerFaceColor','none', 'MarkerEdgeColor', C_ORANGE, ...
                 'LineWidth', 3);
        if k == 1, hDet = h; end           % keep one handle for the legend
        text(ax, v+8, R+6, sprintf('%.0f m, %+.0f m/s', R, v), ...
             'Color','w', 'FontSize', 14, 'FontWeight','bold');
    end
    hold(ax, 'off');

    xlim(ax, [-60 60]);
    ylim(ax, [0 150]);
    xlabel(ax, 'Radial velocity (m/s)');
    ylabel(ax, 'Range (m)');
    title(ax, { 'Range-Doppler map from a data-carrying OFDM frame', ...
                sprintf('%d subcarriers \\times %d symbols   |   \\Delta R = %.1f m,   \\Delta v = %.1f m/s', ...
                        Nsc, Msym, dR, dv) });
    legend(ax, hDet, 'Detected target', 'TextColor','w', ...
           'Color',[0 0 0], 'EdgeColor', C_ORANGE, 'Location','northeast');

    styleAxes(ax);                         % enforce presentation styling

    % ---- auto-save 300-dpi PNG next to the other talk figures -----------
    figDir = fullfile(fileparts(mfilename('fullpath')), '..', '..', 'figures');
    saveFigurePNG(fig, fullfile(figDir, 'fig_demo4_rd_map.png'));

    fprintf('run_demo (demo4 ISAC): done\n');
end

% =========================================================================
% ============================ LOCAL FUNCTIONS ============================
% =========================================================================

function styleAxes(ax)
% styleAxes  Enforce slide-ready styling: big fonts, heavy lines, labels.
    set(ax, 'FontSize', 15, 'LineWidth', 1.5, 'Box', 'on', 'Layer', 'top');
    ax.Title.FontSize  = 17;
    ax.XLabel.FontSize = 16;
    ax.YLabel.FontSize = 16;
    ax.TickDir = 'out';
end

function saveFigurePNG(fig, outPath)
% saveFigurePNG  Save FIG to OUTPATH as a 300-dpi PNG.  Prefer the modern
%   exportgraphics; fall back to print -dpng -r300 on older MATLAB.
    outDir = fileparts(outPath);
    if ~exist(outDir, 'dir'), mkdir(outDir); end
    try
        exportgraphics(fig, outPath, 'Resolution', 300);
    catch
        print(fig, outPath, '-dpng', '-r300');
    end
    fprintf('saved: %s\n', outPath);
end

function cmap = viridisMap()
% viridisMap  256-entry matplotlib "viridis" colormap, interpolated from
%   16 exact anchor colours (base MATLAB has no built-in viridis).
    anchors = [ ...
        0.2670 0.0049 0.3294;
        0.2827 0.1002 0.4222;
        0.2771 0.1852 0.4899;
        0.2539 0.2653 0.5300;
        0.2220 0.3392 0.5488;
        0.1906 0.4071 0.5561;
        0.1636 0.4711 0.5581;
        0.1391 0.5338 0.5553;
        0.1206 0.5964 0.5436;
        0.1347 0.6586 0.5176;
        0.2080 0.7187 0.4729;
        0.3278 0.7740 0.4066;
        0.4775 0.8214 0.3182;
        0.6473 0.8584 0.2099;
        0.8249 0.8847 0.1062;
        0.9932 0.9062 0.1439 ];
    xa = linspace(0, 1, size(anchors,1));
    xi = linspace(0, 1, 256);
    cmap = [ interp1(xa, anchors(:,1), xi).', ...
             interp1(xa, anchors(:,2), xi).', ...
             interp1(xa, anchors(:,3), xi).' ];
    cmap = min(max(cmap, 0), 1);           % clamp to valid RGB range
end
