
% Base code: Raphaël Jeanneret (LPENS - CNRS)
% Adapted and used by: Romain Ratajczyk (Summer 2024)




% Code MATLAB pour créer un background MAX à soustraire à la séquence d'images associée
nframe = 401;

for m = 1:1
    % ninit = (m-1)*Nback;
    basepath = 'C:\Users\manip\Documents\Romain\240625\AVEC DCMU\';
    nom = [basepath, 'img_', num2str(0, '%04i'), '.tif'];
    back = imread(nom);
    % back = mean(back, 3);
    
    % for i = ninit+1 : ninit+Nback-1
    for i = 1:nframe
        nom = [basepath, 'img_', num2str(i, '%04i'), '.tif'];
        img = imread(nom);
        
        test = double(back) - double(img);
        a = find(test < 0);
        back(a) = img(a);
        
        if mod(i, 50) == 0
            disp(i)
        end
    end
    
    back = uint8(back);
    nom = [basepath, 'background_MAX.tiff'];
    imwrite(back, nom);
end
