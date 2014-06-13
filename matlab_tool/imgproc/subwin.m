function RES = subwin(IM, RECT)
% solve the boundary problem when cropping RECT in IM
% input IM is a 3-channel color image
% the RECT specify a rectangle (x1, y1, w, h)

RECT = round(RECT);
% RECT = RECT - [0, 0, RECT(1:2)];
x = RECT(1);
y = RECT(2);
w = RECT(3);
h = RECT(4);
[imH, imW, d] = size(IM);

if x < 1 || y < 1 || x+w > imW || y + h > imH
    % do padding
    px = max(-x, (x+w) - imW);
    px = max(px, 0);
    py = max(-y, (y+h) - imH);
    py = max(py, 0);
    PIM = padarray(IM, [py, px], 'symmetric', 'both');
    px = max(-x, -1);
    py = max(-y, -1);
    newrect = [x + px + 1, y + py + 1, w, h];
    RES = imcrop(PIM, newrect);
else
    RES = imcrop(IM, RECT);
end
